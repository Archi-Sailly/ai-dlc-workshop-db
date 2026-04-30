"""
주문(Order) 및 주문 항목(OrderItem) 모델.
주문 상태 흐름: PENDING → ACCEPTED → PREPARING → COMPLETED
삭제 가능 상태: PENDING, ACCEPTED만 (PREPARING, COMPLETED는 삭제 불가)
"""

import uuid
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Enum,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    """주문 상태 (4단계)"""
    PENDING = "PENDING"        # 대기중 - 고객이 주문 생성 직후
    ACCEPTED = "ACCEPTED"      # 접수 - 관리자가 주문 확인/접수
    PREPARING = "PREPARING"    # 준비중 - 음식 준비 시작
    COMPLETED = "COMPLETED"    # 완료 - 음식 준비 완료/서빙 완료


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        # 세션별 주문 조회 인덱스
        Index("ix_orders_session_id", "session_id"),
        # 매장별 활성 주문 조회 인덱스
        Index("ix_orders_store_status", "store_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    # 사람이 읽기 쉬운 주문 번호 (매장 내 순차 번호)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    session = relationship("Session", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )
