"""
인증 서비스 (관리자 로그인, JWT 토큰 관리).
담당 스토리: US-A01(관리자 로그인), US-A02(세션 유지)

의존성:
- AuthDomain: 비밀번호 검증, JWT 생성/디코딩, 로그인 차단 판단
- AdminUserRepository: 관리자 계정 조회, 로그인 시도 기록
- StoreRepository: 매장 조회
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth_domain import AuthDomain
from app.repositories.admin_user_repository import AdminUserRepository
from app.repositories.store_repository import StoreRepository
from app.schemas.auth_schemas import LoginRequest, LoginResponse, TokenPayload


class AuthService:
    """인증 비즈니스 오케스트레이션"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_user_repo = AdminUserRepository(db)
        self.store_repo = StoreRepository(db)
        self.domain = AuthDomain()

    async def login(self, request: LoginRequest) -> LoginResponse:
        """
        관리자 로그인 + JWT 발급.
        1. 매장 조회
        2. 로그인 차단 확인
        3. 사용자 조회
        4. 비밀번호 검증
        5. 로그인 성공 기록
        6. JWT 토큰 생성
        """
        # 1. 매장 조회
        store = await self.store_repo.get_by_identifier(request.store_identifier)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="매장 식별자, 사용자명 또는 비밀번호가 올바르지 않습니다.",
            )

        # 2. 로그인 차단 확인
        recent_failures = await self.admin_user_repo.get_recent_failed_attempts(
            store.id, request.username
        )
        if self.domain.is_login_blocked(recent_failures):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="로그인 시도가 너무 많습니다. 잠시 후 다시 시도해주세요.",
            )

        # 3. 사용자 조회
        admin_user = await self.admin_user_repo.get_by_username(
            store.id, request.username
        )
        if not admin_user:
            await self.admin_user_repo.record_login_attempt(
                store.id, request.username, success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="매장 식별자, 사용자명 또는 비밀번호가 올바르지 않습니다.",
            )

        # 4. 비밀번호 검증
        if not self.domain.verify_password(
            request.password, admin_user.password_hash
        ):
            await self.admin_user_repo.record_login_attempt(
                store.id, request.username, success=False
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="매장 식별자, 사용자명 또는 비밀번호가 올바르지 않습니다.",
            )

        # 5. 로그인 성공 기록
        await self.admin_user_repo.record_login_attempt(
            store.id, request.username, success=True
        )

        # 6. JWT 토큰 생성
        token, expires_at = self.domain.create_jwt_token(
            username=admin_user.username,
            store_id=str(store.id),
        )

        return LoginResponse(
            access_token=token,
            expires_at=expires_at,
            store_id=store.id,
            username=admin_user.username,
            display_name=admin_user.display_name,
        )

    async def verify_token(self, token: str) -> TokenPayload:
        """JWT 토큰 검증"""
        try:
            payload = self.domain.decode_jwt_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )

        # 사용자 존재 확인
        admin_user = await self.admin_user_repo.get_by_username(
            uuid.UUID(payload.store_id), payload.sub
        )
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
            )

        return payload
