"""
애플리케이션 설정 모듈.
환경 변수 또는 .env 파일에서 설정을 로드합니다.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # 앱 기본 설정
    APP_NAME: str = "테이블오더 서비스"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 데이터베이스
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/table_order"
    DATABASE_ECHO: bool = False

    # JWT 인증
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 16

    # 로그인 시도 제한
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_BLOCK_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]

    # 파일 업로드
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # SSE
    SSE_HEARTBEAT_INTERVAL: int = 30  # 초

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()
