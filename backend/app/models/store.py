"""
매장(Store) 모델.
멀티테넌시의 기본 단위로, 모든 데이터는 store_id로 격리됩니다.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # 매장 식별자 (로그인 시 사용, 예: "store-001")
    identifier: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    admin_users = relationship("AdminUser", back_populates="store", lazy="selectin")
    tables = relationship("Table", back_populates="store", lazy="selectin")
    menus = relationship("Menu", back_populates="store", lazy="selectin")
    categories = relationship("Category", back_populates="store", lazy="selectin")
