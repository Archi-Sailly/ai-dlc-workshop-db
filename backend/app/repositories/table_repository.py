"""
테이블 데이터 접근 레이어.
"""

import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import Table


class TableRepository:
    """테이블 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, store_id: uuid.UUID, table_number: int) -> Table:
        """테이블 등록"""
        table = Table(store_id=store_id, table_number=table_number, is_active=True)
        self.db.add(table)
        await self.db.flush()
        return table

    async def get_by_store_and_number(
        self, store_id: uuid.UUID, table_number: int
    ) -> Optional[Table]:
        """매장 ID + 테이블 번호로 조회"""
        result = await self.db.execute(
            select(Table).where(
                and_(
                    Table.store_id == store_id,
                    Table.table_number == table_number,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_store(self, store_id: uuid.UUID) -> list[Table]:
        """매장의 전체 테이블 목록 조회 (번호순)"""
        result = await self.db.execute(
            select(Table)
            .where(Table.store_id == store_id)
            .order_by(Table.table_number)
        )
        return list(result.scalars().all())

    async def exists(self, store_id: uuid.UUID, table_number: int) -> bool:
        """테이블 존재 여부 확인"""
        result = await self.db.execute(
            select(Table.id).where(
                and_(
                    Table.store_id == store_id,
                    Table.table_number == table_number,
                )
            )
        )
        return result.scalar_one_or_none() is not None
