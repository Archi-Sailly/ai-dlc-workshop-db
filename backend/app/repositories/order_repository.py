"""
주문 데이터 접근 레이어.
Order, OrderItem 테이블에 대한 CRUD 및 조회 기능을 제공합니다.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.session import Session


class OrderRepository:
    """주문 리포지토리"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        store_id: uuid.UUID,
        table_id: uuid.UUID,
        session_id: uuid.UUID,
        order_number: int,
        total_amount: Decimal,
        items_data: list[dict],
    ) -> Order:
        """주문 생성 (주문 항목 포함)"""
        order = Order(
            store_id=store_id,
            table_id=table_id,
            session_id=session_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
        )
        self.db.add(order)
        await self.db.flush()

        # 주문 항목 생성
        for item_data in items_data:
            unit_price = Decimal(str(item_data["unit_price"]))
            quantity = int(item_data["quantity"])
            order_item = OrderItem(
                order_id=order.id,
                menu_id=item_data.get("menu_id"),
                menu_name=item_data["menu_name"],
                unit_price=unit_price,
                quantity=quantity,
                subtotal=unit_price * quantity,
            )
            self.db.add(order_item)

        await self.db.flush()
        # items 관계 로드
        await self.db.refresh(order, ["items"])
        return order

    async def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        """주문 ID로 조회 (항목 포함)"""
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_session(self, session_id: uuid.UUID) -> list[Order]:
        """세션별 주문 목록 조회 (시간순)"""
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.session_id == session_id)
            .order_by(Order.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_orders_by_store(self, store_id: uuid.UUID) -> list[Order]:
        """
        매장의 활성 주문 조회 (활성 세션에 속한 주문만).
        대시보드용 데이터.
        """
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .join(Session, Order.session_id == Session.id)
            .where(
                and_(
                    Order.store_id == store_id,
                    Session.completed_at.is_(None),  # 활성 세션만
                )
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, order_id: uuid.UUID, status: OrderStatus
    ) -> Optional[Order]:
        """주문 상태 업데이트"""
        order = await self.get_by_id(order_id)
        if order is None:
            return None
        order.status = status
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def delete_order(self, order_id: uuid.UUID) -> bool:
        """주문 삭제 (cascade로 항목도 삭제)"""
        order = await self.get_by_id(order_id)
        if order is None:
            return False
        await self.db.delete(order)
        await self.db.flush()
        return True

    async def get_next_order_number(self, store_id: uuid.UUID) -> int:
        """매장 내 다음 주문 번호 생성 (순차 증가)"""
        stmt = (
            select(func.coalesce(func.max(Order.order_number), 0))
            .where(Order.store_id == store_id)
        )
        result = await self.db.execute(stmt)
        current_max = result.scalar_one()
        return current_max + 1

    async def get_history(
        self,
        store_id: uuid.UUID,
        table_number: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[tuple], int]:
        """
        과거 주문 내역 조회 (종료된 세션의 주문).
        Session의 completed_at을 JOIN하여 이용 완료 시각도 반환.
        """
        from app.models.table import Table

        base_conditions = [
            Order.store_id == store_id,
            Session.completed_at.is_not(None),  # 종료된 세션만
        ]

        if table_number is not None:
            base_conditions.append(Table.table_number == table_number)
        if date_from is not None:
            base_conditions.append(Order.created_at >= date_from)
        if date_to is not None:
            base_conditions.append(Order.created_at <= date_to)

        # 총 개수 조회
        count_stmt = (
            select(func.count(Order.id))
            .join(Session, Order.session_id == Session.id)
            .join(Table, Order.table_id == Table.id)
            .where(and_(*base_conditions))
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # 데이터 조회 (페이지네이션)
        offset = (page - 1) * size
        data_stmt = (
            select(Order, Table.table_number, Session.completed_at)
            .join(Session, Order.session_id == Session.id)
            .join(Table, Order.table_id == Table.id)
            .where(and_(*base_conditions))
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        data_result = await self.db.execute(data_stmt)
        rows = data_result.all()

        return rows, total
