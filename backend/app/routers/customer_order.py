"""
고객용 주문 API 라우터.
담당 스토리: US-C07(주문 확정), US-C08(주문 내역 조회)

참고: 메뉴 조회(US-C03), 테이블 검증(US-C01)은 팀원 B가 구현합니다.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.table import Table
from app.schemas.order_schemas import (
    CreateOrderRequest,
    OrderResponse,
    OrderListResponse,
)
from app.services.order_service import OrderService
from app.services.session_service import SessionService

router = APIRouter(
    prefix="/api/stores/{store_id}/tables/{table_number}",
    tags=["customer-orders"],
)


async def _get_table(
    db: AsyncSession, store_id: uuid.UUID, table_number: int
) -> Table:
    """테이블 조회 헬퍼. 없으면 404."""
    stmt = select(Table).where(
        and_(
            Table.store_id == store_id,
            Table.table_number == table_number,
            Table.is_active == True,
        )
    )
    result = await db.execute(stmt)
    table = result.scalar_one_or_none()
    if table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 매장 또는 테이블입니다.",
        )
    return table


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    store_id: uuid.UUID,
    table_number: int,
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    주문 생성 (US-C07).
    - 현재 활성 세션이 없으면 새 세션 자동 생성
    - 활성 세션이 있으면 동일 세션에 귀속
    - 주문 성공 시 SSE로 관리자에게 실시간 알림
    """
    table = await _get_table(db, store_id, table_number)

    order_service = OrderService(db)
    session_service = SessionService(db)

    return await order_service.create_order(
        store_id=store_id,
        table_id=table.id,
        table_number=table_number,
        request=request,
        session_service=session_service,
    )


@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    store_id: uuid.UUID,
    table_number: int,
    db: AsyncSession = Depends(get_db),
):
    """
    현재 세션 주문 내역 조회 (US-C08).
    현재 테이블의 활성 세션에 속한 주문만 반환합니다.
    이전 세션의 주문은 표시되지 않습니다.
    """
    table = await _get_table(db, store_id, table_number)

    order_service = OrderService(db)
    session_service = SessionService(db)

    return await order_service.get_orders_by_session(
        store_id=store_id,
        table_id=table.id,
        session_service=session_service,
    )
