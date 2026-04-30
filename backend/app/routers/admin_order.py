"""
관리자 주문 관리 API 라우터.
담당 스토리: US-A03(대시보드), US-A04(주문 상세), US-A05(상태 변경),
            US-A07(주문 삭제), US-A09(과거 내역)
"""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order_schemas import (
    UpdateOrderStatusRequest,
    OrderResponse,
    OrderListResponse,
    DashboardResponse,
    DeleteResponse,
    OrderHistoryResponse,
)
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/api/admin/stores/{store_id}",
    tags=["admin-orders"],
)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    대시보드 데이터 조회 (US-A03).
    테이블별 주문 현황을 그리드 형태로 제공합니다.
    """
    service = OrderService(db)
    return await service.get_dashboard_data(store_id)


@router.get(
    "/tables/{table_number}/orders",
    response_model=OrderListResponse,
)
async def get_table_orders(
    store_id: uuid.UUID,
    table_number: int,
    db: AsyncSession = Depends(get_db),
):
    """
    테이블별 주문 상세 조회 (US-A04).
    현재 활성 세션의 주문 목록을 반환합니다.
    """
    from app.services.session_service import SessionService
    from app.models.table import Table
    from sqlalchemy import select, and_

    # 테이블 ID 조회
    stmt = select(Table).where(
        and_(Table.store_id == store_id, Table.table_number == table_number)
    )
    result = await db.execute(stmt)
    table = result.scalar_one_or_none()
    if table is None:
        return OrderListResponse(orders=[], total=0)

    order_service = OrderService(db)
    session_service = SessionService(db)
    return await order_service.get_orders_by_session(
        store_id, table.id, session_service
    )


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
)
async def update_order_status(
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    request: UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    주문 상태 변경 (US-A05).
    대기중 → 접수 → 준비중 → 완료 (4단계 순차).
    """
    service = OrderService(db)
    return await service.update_order_status(store_id, order_id, request.status)


@router.delete(
    "/orders/{order_id}",
    response_model=DeleteResponse,
)
async def delete_order(
    store_id: uuid.UUID,
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    주문 삭제 (US-A07).
    대기중/접수 상태만 삭제 가능. 준비중/완료는 삭제 불가.
    """
    service = OrderService(db)
    result = await service.delete_order(store_id, order_id)
    return DeleteResponse(**result)


@router.get("/orders/history", response_model=OrderHistoryResponse)
async def get_order_history(
    store_id: uuid.UUID,
    table_number: Optional[int] = Query(None, description="테이블 번호 필터"),
    date_from: Optional[datetime] = Query(None, description="시작 날짜"),
    date_to: Optional[datetime] = Query(None, description="종료 날짜"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
):
    """
    과거 주문 내역 조회 (US-A09).
    종료된 세션의 주문을 날짜/테이블 필터링하여 조회합니다.
    """
    service = OrderService(db)
    return await service.get_order_history(
        store_id=store_id,
        table_number=table_number,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size,
    )
