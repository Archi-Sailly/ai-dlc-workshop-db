"""
세션(Session) 모델.
테이블 세션 라이프사이클을 관리합니다.
- 고객의 첫 주문 시 자동 생성
- 관리자의 "이용 완료" 처리 시 종료
- 세션 종료 후 다음 고객의 첫 주문 시 새 세션 생성
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        # 활성 세션 빠른 조회를 위한 인덱스
        Index(
            "ix_sessions_active_lookup",
            "store_id",
            "table_id",
            "completed_at",
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
    table_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # NULL이면 활성 세션, 값이 있으면 종료된 세션
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # Relationships
    table = relationship("Table", back_populates="sessions")
    orders = relationship("Order", back_populates="session", lazy="selectin")
