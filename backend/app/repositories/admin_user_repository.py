"""
관리자 사용자 데이터 접근 레이어.
AdminUser, LoginAttempt 테이블에 대한 CRUD를 제공합니다.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.admin_user import AdminUser
from app.models.login_attempt import LoginAttempt

settings = get_settings()


class AdminUserRepository:
    """관리자 사용자 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(
        self, store_id: uuid.UUID, username: str
    ) -> AdminUser | None:
        """매장 내 사용자명으로 관리자 조회"""
        result = await self.db.execute(
            select(AdminUser).where(
                and_(
                    AdminUser.store_id == store_id,
                    AdminUser.username == username,
                    AdminUser.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def record_login_attempt(
        self, store_id: uuid.UUID, username: str, success: bool
    ) -> None:
        """로그인 시도 기록"""
        attempt = LoginAttempt(
            store_id=store_id,
            username=username,
            success=success,
        )
        self.db.add(attempt)
        await self.db.flush()

    async def get_recent_failed_attempts(
        self, store_id: uuid.UUID, username: str
    ) -> int:
        """최근 N분 내 실패한 로그인 시도 횟수 조회"""
        since = datetime.now(timezone.utc) - timedelta(
            minutes=settings.LOGIN_BLOCK_MINUTES
        )
        result = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(
                and_(
                    LoginAttempt.store_id == store_id,
                    LoginAttempt.username == username,
                    LoginAttempt.success.is_(False),
                    LoginAttempt.attempted_at >= since,
                )
            )
        )
        return result.scalar_one()
