"""
메뉴 데이터 접근 레이어.
Menu, Category 테이블에 대한 CRUD를 제공합니다.
"""

import uuid
from typing import Optional

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.menu import Category, Menu


class MenuRepository:
    """메뉴 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # === Menu ===

    async def create(self, menu_data: dict) -> Menu:
        """메뉴 생성"""
        menu = Menu(**menu_data)
        self.db.add(menu)
        await self.db.flush()
        return menu

    async def get_by_id(self, menu_id: uuid.UUID) -> Optional[Menu]:
        """메뉴 ID로 조회 (카테고리 포함)"""
        result = await self.db.execute(
            select(Menu)
            .options(joinedload(Menu.category))
            .where(Menu.id == menu_id)
        )
        return result.scalar_one_or_none()

    async def get_by_store(
        self,
        store_id: uuid.UUID,
        category_id: Optional[uuid.UUID] = None,
        available_only: bool = False,
    ) -> list[Menu]:
        """매장 메뉴 목록 조회 (카테고리 필터, 정렬 순서 적용)"""
        query = (
            select(Menu)
            .options(joinedload(Menu.category))
            .where(Menu.store_id == store_id)
        )
        if category_id:
            query = query.where(Menu.category_id == category_id)
        if available_only:
            query = query.where(Menu.is_available == True)
        query = query.order_by(Menu.sort_order, Menu.created_at)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, menu_id: uuid.UUID, menu_data: dict) -> Menu:
        """메뉴 수정"""
        result = await self.db.execute(select(Menu).where(Menu.id == menu_id))
        menu = result.scalar_one()
        for key, value in menu_data.items():
            if value is not None:
                setattr(menu, key, value)
        await self.db.flush()
        return menu

    async def delete(self, menu_id: uuid.UUID) -> bool:
        """메뉴 삭제"""
        result = await self.db.execute(select(Menu).where(Menu.id == menu_id))
        menu = result.scalar_one_or_none()
        if not menu:
            return False
        await self.db.delete(menu)
        await self.db.flush()
        return True

    async def update_sort_orders(self, menu_orders: list[dict]) -> bool:
        """메뉴 노출 순서 일괄 변경"""
        for item in menu_orders:
            await self.db.execute(
                update(Menu)
                .where(Menu.id == item["menu_id"])
                .values(sort_order=item["sort_order"])
            )
        await self.db.flush()
        return True

    # === Category ===

    async def get_categories(self, store_id: uuid.UUID) -> list[Category]:
        """매장 카테고리 목록 조회 (정렬 순서)"""
        result = await self.db.execute(
            select(Category)
            .where(Category.store_id == store_id)
            .order_by(Category.sort_order, Category.name)
        )
        return list(result.scalars().all())

    async def create_category(self, category_data: dict) -> Category:
        """카테고리 생성"""
        category = Category(**category_data)
        self.db.add(category)
        await self.db.flush()
        return category

    async def get_category_by_id(
        self, category_id: uuid.UUID
    ) -> Optional[Category]:
        """카테고리 ID로 조회"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
