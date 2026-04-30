"""
주문 서비스 (비즈니스 오케스트레이션).
주문 생성, 상태 변경, 삭제, 대시보드 데이터, 주문 내역 조회를 담당합니다.

의존성:
- SessionService: 주문 생성 시 세션 자동 생성/귀속
- OrderDomain: 상태 전이 검증, 삭제 가능 여부
- OrderRepository: 데이터 접근
- SSEService: 이벤트 발행
"""

import uuid
import math
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.order_domain import OrderDomain
from app.models.order import Order, OrderStatus
from app.models.table import Table
from app.repositories.order_repository import OrderRepository
from app.schemas.order_schemas import (
    CreateOrderRequest,
    OrderResponse,
    OrderItemResponse,
    OrderListResponse,
    DashboardResponse,
    TableOrderSummary,
    OrderHistoryResponse,
    OrderHistoryItem,
)
from app.services.sse_service import get_sse_service


class OrderService:
    """주문 비즈니스 오케스트레이션"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrderRepository(db)
        self.domain = OrderDomain()
        self.sse = get_sse_service()

    async def create_order(
        self,
        store_id: uuid.UUID,
        table_id: uuid.UUID,
        table_number: int,
        request: CreateOrderRequest,
        session_service,  # SessionService 인스턴스 (순환 import 방지)
    ) -> OrderResponse:
        """
        주문 생성.
        1. 세션 자동 생성/귀속 (SessionService 호출)
        2. 총액 계산 (OrderDomain)
        3. DB 저장 (OrderRepository)
        4. 트랜잭션 커밋
        5. SSE 이벤트 발행
        """
        # 1. 세션 조회 또는 생성
        session = await session_service.get_or_create_session(store_id, table_id)

        # 2. 총액 계산
        items_data = [
            {
                "menu_id": item.menu_id,
                "menu_name": item.menu_name,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
            }
            for item in request.items
        ]
        total_amount = self.domain.calculate_order_total(items_data)

        # 3. 주문 번호 생성 및 DB 저장
        order_number = await self.repo.get_next_order_number(store_id)
        order = await self.repo.create(
            store_id=store_id,
            table_id=table_id,
            session_id=session.id,
            order_number=order_number,
            total_amount=total_amount,
            items_data=items_data,
        )

        # 4. 트랜잭션 커밋
        await self.db.commit()
        await self.db.refresh(order, ["items"])

        # 5. SSE 이벤트 발행 (커밋 후)
        response = self._to_response(order)
        await self.sse.publish_event(
            store_id=store_id,
            table_number=table_number,
            event_type="order_created",
            data=response.model_dump(),
        )

        return response

    async def get_orders_by_session(
        self,
        store_id: uuid.UUID,
        table_id: uuid.UUID,
        session_service,
    ) -> OrderListResponse:
        """현재 활성 세션의 주문 목록 조회"""
        session = await session_service.get_active_session(store_id, table_id)
        if session is None:
            return OrderListResponse(orders=[], total=0)

        orders = await self.repo.get_by_session(session.id)
        return OrderListResponse(
            orders=[self._to_response(o) for o in orders],
            total=len(orders),
        )

    async def update_order_status(
        self,
        store_id: uuid.UUID,
        order_id: uuid.UUID,
        new_status: OrderStatus,
    ) -> OrderResponse:
        """
        주문 상태 변경.
        1. 주문 조회
        2. 상태 전이 검증 (OrderDomain)
        3. DB 업데이트
        4. 트랜잭션 커밋
        5. SSE 이벤트 발행
        """
        # 1. 주문 조회
        order = await self.repo.get_by_id(order_id)
        if order is None or order.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="주문을 찾을 수 없습니다.",
            )

        # 2. 상태 전이 검증
        if not self.domain.validate_status_transition(order.status, new_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{order.status.value}' 상태에서 '{new_status.value}' 상태로 변경할 수 없습니다.",
            )

        # 3. DB 업데이트
        order = await self.repo.update_status(order_id, new_status)

        # 4. 커밋
        await self.db.commit()
        await self.db.refresh(order, ["items"])

        # 5. SSE 이벤트 발행
        # table_number를 가져오기 위해 테이블 조회
        from app.models.table import Table
        from sqlalchemy import select
        table_stmt = select(Table).where(Table.id == order.table_id)
        table_result = await self.db.execute(table_stmt)
        table = table_result.scalar_one()

        response = self._to_response(order)
        await self.sse.publish_event(
            store_id=store_id,
            table_number=table.table_number,
            event_type="order_status_changed",
            data={"order_id": str(order.id), "status": new_status.value},
        )

        return response

    async def delete_order(
        self,
        store_id: uuid.UUID,
        order_id: uuid.UUID,
    ) -> dict:
        """
        주문 삭제 (대기중/접수 상태만).
        1. 주문 조회
        2. 삭제 가능 여부 검증 (OrderDomain)
        3. DB 삭제
        4. 트랜잭션 커밋
        5. SSE 이벤트 발행
        """
        # 1. 주문 조회
        order = await self.repo.get_by_id(order_id)
        if order is None or order.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="주문을 찾을 수 없습니다.",
            )

        # 2. 삭제 가능 여부 검증
        if not self.domain.can_delete(order.status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{order.status.value}' 상태의 주문은 삭제할 수 없습니다. 대기중 또는 접수 상태만 삭제 가능합니다.",
            )

        # table_number 미리 조회 (삭제 전)
        from app.models.table import Table
        from sqlalchemy import select
        table_stmt = select(Table).where(Table.id == order.table_id)
        table_result = await self.db.execute(table_stmt)
        table = table_result.scalar_one()

        order_id_str = str(order.id)

        # 3. DB 삭제
        await self.repo.delete_order(order_id)

        # 4. 커밋
        await self.db.commit()

        # 5. SSE 이벤트 발행
        await self.sse.publish_event(
            store_id=store_id,
            table_number=table.table_number,
            event_type="order_deleted",
            data={"order_id": order_id_str},
        )

        return {"success": True, "message": "주문이 삭제되었습니다."}

    async def get_dashboard_data(
        self, store_id: uuid.UUID
    ) -> DashboardResponse:
        """
        대시보드용 테이블별 주문 현황 집계.
        활성 세션이 있는 테이블의 주문만 표시합니다.
        """
        from app.models.table import Table
        from sqlalchemy import select

        # 매장의 모든 테이블 조회
        tables_stmt = select(Table).where(Table.store_id == store_id).order_by(Table.table_number)
        tables_result = await self.db.execute(tables_stmt)
        tables = list(tables_result.scalars().all())

        # 활성 주문 조회
        active_orders = await self.repo.get_active_orders_by_store(store_id)

        # 테이블별 주문 그룹화
        table_orders: dict[uuid.UUID, list[Order]] = {}
        for order in active_orders:
            if order.table_id not in table_orders:
                table_orders[order.table_id] = []
            table_orders[order.table_id].append(order)

        # 테이블별 요약 생성
        summaries = []
        for table in tables:
            orders = table_orders.get(table.id, [])
            total_amount = sum(o.total_amount for o in orders)
            latest_orders = sorted(orders, key=lambda o: o.created_at, reverse=True)[:3]

            summaries.append(
                TableOrderSummary(
                    table_id=table.id,
                    table_number=table.table_number,
                    total_amount=total_amount,
                    order_count=len(orders),
                    latest_orders=[self._to_response(o) for o in latest_orders],
                    has_new_order=any(o.status == OrderStatus.PENDING for o in orders),
                )
            )

        return DashboardResponse(tables=summaries)

    async def get_order_history(
        self,
        store_id: uuid.UUID,
        table_number: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        size: int = 20,
    ) -> OrderHistoryResponse:
        """
        과거 주문 내역 조회 (종료된 세션의 주문).
        US-A09: Order 모듈(주 담당) + Session 모듈(이용 완료 시각 데이터)
        """
        rows, total = await self.repo.get_history(
            store_id=store_id,
            table_number=table_number,
            date_from=date_from,
            date_to=date_to,
            page=page,
            size=size,
        )

        history_items = []
        for order, tbl_number, session_completed_at in rows:
            history_items.append(
                OrderHistoryItem(
                    id=order.id,
                    order_number=order.order_number,
                    table_number=tbl_number,
                    status=order.status,
                    total_amount=order.total_amount,
                    items=[
                        OrderItemResponse.model_validate(item)
                        for item in order.items
                    ],
                    created_at=order.created_at,
                    session_completed_at=session_completed_at,
                )
            )

        total_pages = math.ceil(total / size) if total > 0 else 0

        return OrderHistoryResponse(
            orders=history_items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages,
        )

    @staticmethod
    def _to_response(order: Order) -> OrderResponse:
        """Order 모델을 OrderResponse로 변환"""
        return OrderResponse(
            id=order.id,
            store_id=order.store_id,
            table_id=order.table_id,
            session_id=order.session_id,
            order_number=order.order_number,
            status=order.status,
            total_amount=order.total_amount,
            items=[
                OrderItemResponse.model_validate(item)
                for item in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
