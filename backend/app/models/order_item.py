"""
주문 항목(OrderItem) 모델.
주문에 포함된 개별 메뉴 항목을 나타냅니다.
주문 시점의 메뉴명과 가격을 스냅샷으로 저장합니다 (메뉴 변경에 영향받지 않음).
"""

import uuid
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menus.id", ondelete="SET NULL"),
        nullable=True,  # 메뉴 삭제 시에도 주문 항목은 유지
    )
    # 주문 시점 스냅샷 (메뉴가 나중에 변경/삭제되어도 주문 기록 유지)
    menu_name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
