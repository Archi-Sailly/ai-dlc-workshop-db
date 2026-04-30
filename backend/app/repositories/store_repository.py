"""
매장 데이터 접근 레이어.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store


class StoreRepository:
    """매장 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, store_id: uuid.UUID) -> Optional[Store]:
        """매장 ID로 조회"""
        result = await self.db.execute(select(Store).where(Store.id == store_id))
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> Optional[Store]:
        """매장 식별자로 조회 (로그인용)"""
        result = await self.db.execute(
            select(Store).where(Store.identifier == identifier)
        )
        return result.scalar_one_or_none()

    async def exists(self, store_id: uuid.UUID) -> bool:
        """매장 존재 여부 확인"""
        result = await self.db.execute(
            select(Store.id).where(Store.id == store_id)
        )
        return result.scalar_one_or_none() is not None
