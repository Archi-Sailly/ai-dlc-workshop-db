"""
테이블/세션 관련 Pydantic 스키마 (요청/응답).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# === 요청 스키마 ===

class CreateTableRequest(BaseModel):
    """테이블 등록 요청"""
    table_number: int = Field(..., gt=0, description="테이블 번호 (양수)")


# === 응답 스키마 ===

class TableResponse(BaseModel):
    """테이블 응답"""
    id: uuid.UUID
    store_id: uuid.UUID
    table_number: int
    is_active: bool
    created_at: datetime
    url: str | None = None

    model_config = {"from_attributes": True}


class TableListResponse(BaseModel):
    """테이블 목록 응답"""
    tables: list[TableResponse]
    total: int


class TableValidationResponse(BaseModel):
    """테이블 유효성 검증 응답"""
    valid: bool
    store_id: uuid.UUID | None = None
    store_name: str | None = None
    table_number: int | None = None
    message: str | None = None


class SessionResponse(BaseModel):
    """세션 응답"""
    id: uuid.UUID
    store_id: uuid.UUID
    table_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class SessionCompleteResponse(BaseModel):
    """세션 종료 응답"""
    session_id: uuid.UUID
    status: str = "completed"
    completed_at: datetime
    message: str = "이용 완료 처리되었습니다."
