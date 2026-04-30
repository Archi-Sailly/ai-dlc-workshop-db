"""
JWT 인증 미들웨어.
FastAPI 의존성 주입 방식으로 관리자 인증을 처리합니다.

사용법:
    @router.get("/protected")
    async def protected_endpoint(
        admin: TokenPayload = Depends(get_current_admin),
    ):
        ...
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.domain.auth_domain import AuthDomain
from app.schemas.auth_schemas import TokenPayload

# Bearer 토큰 추출기
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    JWT 토큰에서 현재 관리자 정보 추출.
    관리자 인증이 필요한 엔드포인트에서 의존성으로 사용합니다.
    """
    try:
        payload = AuthDomain.decode_jwt_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_store_id(
    admin: TokenPayload = Depends(get_current_admin),
) -> uuid.UUID:
    """현재 관리자의 매장 ID 추출"""
    return uuid.UUID(admin.store_id)
