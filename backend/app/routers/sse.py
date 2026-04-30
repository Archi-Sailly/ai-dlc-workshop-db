"""
SSE(Server-Sent Events) 라우터.
담당 스토리: US-C09(고객 실시간 업데이트), US-A03(관리자 실시간 대시보드)

구독 구조:
- 고객: 테이블 단위 (/api/sse/stores/{store_id}/tables/{table_number}/orders)
- 관리자: 매장 단위 (/api/sse/stores/{store_id}/orders)
"""

import uuid

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.services.sse_service import get_sse_service

router = APIRouter(
    prefix="/api/sse",
    tags=["sse"],
)


@router.get("/stores/{store_id}/tables/{table_number}/orders")
async def subscribe_table_orders(
    store_id: uuid.UUID,
    table_number: int,
):
    """
    고객용 SSE - 테이블 단위 주문 상태 업데이트 (US-C09).
    해당 테이블의 주문 이벤트만 수신합니다.
    이벤트: order_created, order_status_changed, order_deleted, session_completed
    """
    sse = get_sse_service()
    return EventSourceResponse(
        sse.subscribe_table(store_id, table_number),
        media_type="text/event-stream",
    )


@router.get("/stores/{store_id}/orders")
async def subscribe_store_orders(
    store_id: uuid.UUID,
):
    """
    관리자용 SSE - 매장 전체 주문 업데이트 (US-A03).
    매장의 모든 테이블 주문 이벤트를 수신합니다.
    이벤트: order_created, order_status_changed, order_deleted, session_completed

    참고: JWT 인증은 팀원 B가 JWT 미들웨어 구현 후 적용 예정.
    """
    sse = get_sse_service()
    return EventSourceResponse(
        sse.subscribe_store(store_id),
        media_type="text/event-stream",
    )
