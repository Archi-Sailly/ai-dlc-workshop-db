"""
관리자 인증 API 라우터.
담당 스토리: US-A01(관리자 로그인), US-A02(세션 유지/토큰 검증)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_middleware import get_current_admin
from app.schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    TokenPayload,
    TokenVerifyResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/admin/auth",
    tags=["admin-auth"],
)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    관리자 로그인 (US-A01).
    매장 식별자, 사용자명, 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.
    - 올바른 정보 입력 시 JWT 토큰 발급 + 대시보드 이동
    - 잘못된 정보 입력 시 에러 메시지
    - 연속 5회 실패 시 30분간 로그인 차단
    """
    service = AuthService(db)
    return await service.login(request)


@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    admin: TokenPayload = Depends(get_current_admin),
):
    """
    JWT 토큰 유효성 검증 (US-A02).
    Authorization 헤더의 Bearer 토큰을 검증합니다.
    - 유효한 토큰: valid=True + 사용자 정보
    - 만료/무효 토큰: 401 에러
    """
    return TokenVerifyResponse(
        valid=True,
        store_id=admin.store_id,
        username=admin.sub,
        expires_at=admin.exp,
    )
