"""
로그인 시도(LoginAttempt) 모델.
관리자 로그인 시도를 기록하여 연속 실패 시 차단합니다.
30분 내 5회 연속 실패 시 로그인 차단.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    __table_args__ = (
        # 최근 로그인 시도 조회 인덱스
        Index(
            "ix_login_attempts_lookup",
            "store_id",
            "username",
            "attempted_at",
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
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
