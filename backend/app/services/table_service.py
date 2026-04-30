"""
테이블 서비스 (테이블 등록, 유효성 검증, URL 생성).
담당 스토리: US-C01(테이블 식별), US-A06(테이블 등록)

의존성:
- TableDomain: 테이블 번호 검증, URL 생성
- TableRepository: 테이블 CRUD
- StoreRepository: 매장 존재 확인
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.table_domain import TableDomain
from app.models.table import Table
from app.repositories.store_repository import StoreRepository
from app.repositories.table_repository import TableRepository
from app.schemas.table_schemas import TableValidationResponse


class TableService:
    """테이블 비즈니스 오케스트레이션"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.table_repo = TableRepository(db)
        self.store_repo = StoreRepository(db)
        self.domain = TableDomain()

    async def validate_table(
        self, store_id: uuid.UUID, table_number: int
    ) -> TableValidationResponse:
        """매장/테이블 유효성 검증 (US-C01)"""
        store = await self.store_repo.get_by_id(store_id)
        if not store or not store.is_active:
            return TableValidationResponse(
                valid=False, message="존재하지 않는 매장입니다."
            )

        table = await self.table_repo.get_by_store_and_number(store_id, table_number)
        if not table or not table.is_active:
            return TableValidationResponse(
                valid=False, message="존재하지 않는 테이블입니다."
            )

        return TableValidationResponse(
            valid=True,
            store_id=store.id,
            store_name=store.name,
            table_number=table.table_number,
        )

    async def create_table(self, store_id: uuid.UUID, table_number: int) -> Table:
        """테이블 등록 (US-A06) — 중복 체크 포함"""
        if not self.domain.validate_table_number(table_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="테이블 번호는 양수여야 합니다.",
            )

        # 매장 존재 확인
        if not await self.store_repo.exists(store_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 매장입니다.",
            )

        # 중복 체크
        if await self.table_repo.exists(store_id, table_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"테이블 번호 {table_number}은(는) 이미 등록되어 있습니다.",
            )

        table = await self.table_repo.create(store_id, table_number)
        await self.db.commit()
        return table

    async def get_tables(self, store_id: uuid.UUID) -> list[Table]:
        """매장 테이블 목록 조회"""
        return await self.table_repo.get_by_store(store_id)

    def get_table_url(self, store_id: uuid.UUID, table_number: int) -> str:
        """테이블 접속 URL 생성"""
        return self.domain.generate_table_url(str(store_id), table_number)
