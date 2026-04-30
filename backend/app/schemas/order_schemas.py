"""
주문 관련 Pydantic 스키마 (요청/응답).
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


# === 요청 스키마 ===

class OrderItemRequest(BaseModel):
    """주문 항목 요청"""
    menu_id: uuid.UUID
    menu_name: str = Field(..., min_length=1, max_length=200)
    unit_price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


class CreateOrderRequest(BaseModel):
    """주문 생성 요청 (고객용)"""
    items: list[OrderItemRequest] = Field(..., min_length=1)


class UpdateOrderStatusRequest(BaseModel):
    """주문 상태 변경 요청 (관리자용)"""
    status: OrderStatus


class OrderHistoryFilter(BaseModel):
    """과거 주문 내역 필터"""
    table_number: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


# === 응답 스키마 ===

class OrderItemResponse(BaseModel):
    """주문 항목 응답"""
    id: uuid.UUID
    menu_id: Optional[uuid.UUID] = None
    menu_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """주문 응답"""
    id: uuid.UUID
    store_id: uuid.UUID
    table_id: uuid.UUID
    session_id: uuid.UUID
    order_number: int
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """주문 목록 응답"""
    orders: list[OrderResponse]
    total: int


class DeleteResponse(BaseModel):
    """삭제 응답"""
    success: bool
    message: str


# === 대시보드 스키마 ===

class TableOrderSummary(BaseModel):
    """테이블별 주문 요약 (대시보드용)"""
    table_id: uuid.UUID
    table_number: int
    total_amount: Decimal
    order_count: int
    latest_orders: list[OrderResponse] = []
    has_new_order: bool = False


class DashboardResponse(BaseModel):
    """대시보드 응답"""
    tables: list[TableOrderSummary]


# === 과거 주문 내역 스키마 ===

class OrderHistoryItem(BaseModel):
    """과거 주문 내역 항목"""
    id: uuid.UUID
    order_number: int
    table_number: int
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemResponse] = []
    created_at: datetime
    session_completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderHistoryResponse(BaseModel):
    """과거 주문 내역 응답 (페이지네이션)"""
    orders: list[OrderHistoryItem]
    total: int
    page: int
    size: int
    total_pages: int
