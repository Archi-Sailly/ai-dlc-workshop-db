"""
고객용 테이블 검증 API 라우터.
담당 스토리: US-C01(테이블 식별 — URL 기반 접근)
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.table_schemas import (
    SessionResponse,
    TableValidationResponse,
)
from app.services.session_service import SessionService
from app.services.table_service import TableService

router = APIRouter(
    prefix="/api/stores/{store_id}/tables/{table_number}",
    tags=["customer-tables"],
)


@router.get("/validate", response_model=TableValidationResponse)
async def validate_table(
    store_id: uuid.UUID,
    table_number: int,
    db: AsyncSession = Depends(get_db),
):
    """
    매장/테이블 유효성 검증 (US-C01).
    URL에 포함된 매장 ID와 테이블 번호가 유효한지 확인합니다.
    - 유효: valid=True + 매장명, 테이블 번호
    - 무효: valid=False + 에러 메시지
    """
    service = TableService(db)
    return await service.validate_table(store_id, table_number)


@router.get("/session", response_model=SessionResponse | None)
async def get_active_session(
    store_id: uuid.UUID,
    table_number: int,
    db: AsyncSession = Depends(get_db),
):
    """현재 활성 세션 조회"""
    from app.models.table import Table
    from sqlalchemy import select, and_

    stmt = select(Table).where(
        and_(Table.store_id == store_id, Table.table_number == table_number)
    )
    result = await db.execute(stmt)
    table = result.scalar_one_or_none()
    if not table:
        return None

    session_service = SessionService(db)
    session = await session_service.get_active_session(store_id, table.id)
    if not session:
        return None
    return SessionResponse.model_validate(session)
