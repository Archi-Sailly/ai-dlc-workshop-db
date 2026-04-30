"""
메뉴 관련 Pydantic 스키마 (요청/응답).
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# === 요청 스키마 ===

class CreateCategoryRequest(BaseModel):
    """카테고리 등록 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="카테고리명")
    sort_order: int = Field(default=0, description="정렬 순서")


class CreateMenuRequest(BaseModel):
    """메뉴 등록 요청"""
    name: str = Field(..., min_length=1, max_length=200, description="메뉴명")
    price: Decimal = Field(..., gt=0, description="가격 (양수)")
    description: str | None = Field(default=None, description="메뉴 설명")
    category_id: uuid.UUID = Field(..., description="카테고리 ID")
    sort_order: int = Field(default=0, description="정렬 순서")


class UpdateMenuRequest(BaseModel):
    """메뉴 수정 요청"""
    name: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0)
    description: str | None = None
    category_id: uuid.UUID | None = None
    sort_order: int | None = None
    is_available: bool | None = None


class ReorderMenuItem(BaseModel):
    """메뉴 순서 변경 항목"""
    menu_id: uuid.UUID
    sort_order: int


class ReorderMenuRequest(BaseModel):
    """메뉴 노출 순서 일괄 변경 요청"""
    menu_orders: list[ReorderMenuItem]


# === 응답 스키마 ===

class CategoryResponse(BaseModel):
    """카테고리 응답"""
    id: uuid.UUID
    store_id: uuid.UUID
    name: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답"""
    categories: list[CategoryResponse]
    total: int


class MenuResponse(BaseModel):
    """메뉴 응답"""
    id: uuid.UUID
    store_id: uuid.UUID
    category_id: uuid.UUID
    name: str
    price: Decimal
    description: str | None = None
    image_url: str | None = None
    sort_order: int
    is_available: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MenuListResponse(BaseModel):
    """메뉴 목록 응답"""
    menus: list[MenuResponse]
    total: int


class MenuDetailResponse(MenuResponse):
    """메뉴 상세 응답 (카테고리명 포함)"""
    category_name: str | None = None


class SuccessResponse(BaseModel):
    """범용 성공 응답"""
    success: bool = True
    message: str = "성공"


class DeleteResponse(BaseModel):
    """삭제 응답"""
    success: bool = True
    message: str = "삭제되었습니다."
