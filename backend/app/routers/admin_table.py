"""
관리자 테이블/세션 관리 API 라우터.
담당 스토리: US-A06(테이블 등록), US-A08(이용 완료/세션 종료)
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_middleware import get_current_admin
from app.models.table import Table
from app.schemas.auth_schemas import TokenPayload
from app.schemas.table_schemas import (
    CreateTableRequest,
    SessionCompleteResponse,
    TableListResponse,
    TableResponse,
)
from app.services.session_service import SessionService
from app.services.table_service import TableService

router = APIRouter(
    prefix="/api/admin/stores/{store_id}",
    tags=["admin-tables"],
)


@router.post("/tables", response_model=TableResponse)
async def create_table(
    store_id: uuid.UUID,
    request: CreateTableRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """
    테이블 등록 (US-A06).
    새 테이블 번호를 등록하고 매장에 매핑합니다.
    - 테이블 번호 중복 시 409 에러
    - 등록 후 테이블 접속 URL 생성
    """
    service = TableService(db)
    table = await service.create_table(store_id, request.table_number)
    url = service.get_table_url(store_id, table.table_number)
    return TableResponse(
        id=table.id,
        store_id=table.store_id,
        table_number=table.table_number,
        is_active=table.is_active,
        created_at=table.created_at,
        url=url,
    )


@router.get("/tables", response_model=TableListResponse)
async def get_tables(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """테이블 목록 조회"""
    service = TableService(db)
    tables = await service.get_tables(store_id)
    table_responses = [
        TableResponse(
            id=t.id,
            store_id=t.store_id,
            table_number=t.table_number,
            is_active=t.is_active,
            created_at=t.created_at,
            url=service.get_table_url(store_id, t.table_number),
        )
        for t in tables
    ]
    return TableListResponse(tables=table_responses, total=len(table_responses))


@router.post(
    "/tables/{table_number}/complete",
    response_model=SessionCompleteResponse,
)
async def complete_table_session(
    store_id: uuid.UUID,
    table_number: int,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """
    테이블 이용 완료 / 세션 종료 (US-A08).
    - 현재 활성 세션을 종료합니다.
    - 주문 내역이 과거 이력으로 이동합니다.
    - 다음 고객의 첫 주문 시 새 세션이 자동 생성됩니다.
    - SSE로 고객/관리자에게 세션 종료 이벤트 발행
    """
    # 테이블 조회
    stmt = select(Table).where(
        and_(
            Table.store_id == store_id,
            Table.table_number == table_number,
        )
    )
    result = await db.execute(stmt)
    table = result.scalar_one_or_none()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 테이블입니다.",
        )

    session_service = SessionService(db)
    completed = await session_service.complete_session(
        store_id, table.id, table_number
    )

    if completed is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="종료할 활성 세션이 없습니다.",
        )

    await db.commit()

    return SessionCompleteResponse(
        session_id=completed.id,
        completed_at=completed.completed_at,
    )
