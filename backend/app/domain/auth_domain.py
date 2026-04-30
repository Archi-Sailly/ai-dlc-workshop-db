"""
인증 도메인 규칙.
- bcrypt 비밀번호 해싱/검증
- JWT 토큰 생성/디코딩
- 로그인 시도 제한 판단
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings
from app.schemas.auth_schemas import TokenPayload

settings = get_settings()


class AuthDomain:
    """인증 비즈니스 규칙"""

    @staticmethod
    def hash_password(password: str) -> str:
        """bcrypt 비밀번호 해싱"""
        return bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def is_login_blocked(attempts: int) -> bool:
        """로그인 차단 여부 판단 (30분 내 5회 실패 시 차단)"""
        return attempts >= settings.LOGIN_MAX_ATTEMPTS

    @staticmethod
    def create_jwt_token(username: str, store_id: str) -> tuple[str, datetime]:
        """JWT 토큰 생성. (token, expires_at) 반환"""
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.JWT_EXPIRE_HOURS
        )
        payload = {
            "sub": username,
            "store_id": store_id,
            "exp": expires_at,
        }
        token = jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return token, expires_at

    @staticmethod
    def decode_jwt_token(token: str) -> TokenPayload:
        """JWT 토큰 디코딩/검증. 만료 시 예외 발생."""
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
