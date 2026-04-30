"""
테이블(Table) 모델.
매장 내 물리적 테이블을 나타냅니다. 고객은 URL로 테이블에 접근합니다.
"""

import uuid
from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Table(Base):
    __tablename__ = "tables"
    __table_args__ = (
        # 동일 매장 내 테이블 번호 중복 방지
        UniqueConstraint(
            "store_id", "table_number", name="uq_tables_store_table_number"
        ),
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
    table_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    store = relationship("Store", back_populates="tables")
    sessions = relationship("Session", back_populates="table", lazy="selectin")
