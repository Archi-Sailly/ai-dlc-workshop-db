"""
SSE 관련 Pydantic 스키마.
"""

import uuid
from typing import Any, Optional

from pydantic import BaseModel


class SSEEvent(BaseModel):
    """SSE 이벤트 데이터"""
    event_type: str  # order_created, order_status_changed, order_deleted, session_completed
    store_id: uuid.UUID
    table_number: int
    data: dict[str, Any]
