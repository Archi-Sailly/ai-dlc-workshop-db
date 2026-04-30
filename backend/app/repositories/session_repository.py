"""
세션 데이터 접근 레이어.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    """세션 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, store_id: uuid.UUID, table_id: uuid.UUID) -> Session:
        """새 세션 생성"""
        session = Session(store_id=store_id, table_id=table_id)
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_active(
        self, store_id: uuid.UUID, table_id: uuid.UUID
    ) -> Optional[Session]:
        """활성 세션 조회 (completed_at IS NULL)"""
        result = await self.db.execute(
            select(Session).where(
                and_(
                    Session.store_id == store_id,
                    Session.table_id == table_id,
                    Session.completed_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def complete(self, session_id: uuid.UUID) -> Session:
        """세션 종료 (completed_at 설정)"""
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one()
        session.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> Optional[Session]:
        """세션 ID로 조회"""
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
