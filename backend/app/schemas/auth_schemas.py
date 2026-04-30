"""
인증 관련 Pydantic 스키마 (요청/응답).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# === 요청 스키마 ===

class LoginRequest(BaseModel):
    """관리자 로그인 요청"""
    store_identifier: str = Field(..., min_length=1, max_length=100, description="매장 식별자")
    username: str = Field(..., min_length=1, max_length=100, description="사용자명")
    password: str = Field(..., min_length=1, description="비밀번호")


# === 응답 스키마 ===

class LoginResponse(BaseModel):
    """로그인 성공 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    store_id: uuid.UUID
    username: str
    display_name: str


class TokenVerifyResponse(BaseModel):
    """토큰 검증 응답"""
    valid: bool
    store_id: uuid.UUID | None = None
    username: str | None = None
    expires_at: datetime | None = None


class TokenPayload(BaseModel):
    """JWT 토큰 페이로드"""
    sub: str  # username
    store_id: str
    exp: datetime
