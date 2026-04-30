"""
세션 서비스 (세션 라이프사이클 관리).
팀원 B 담당이지만, OrderService에서 호출하므로 팀원 A가 인터페이스를 정의합니다.
팀원 B가 상세 구현을 채워넣을 예정입니다.

세션 라이프사이클:
- 고객 첫 주문 시 자동 생성 (get_or_create_session)
- 추가 주문은 동일 세션에 귀속
- 관리자 "이용 완료" 시 종료 (complete_session)
"""

import uuid
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session as SessionModel
from app.services.sse_service import get_sse_service


class SessionService:
    """세션 라이프사이클 관리"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sse = get_sse_service()

    async def get_or_create_session(
        self, store_id: uuid.UUID, table_id: uuid.UUID
    ) -> SessionModel:
        """
        활성 세션 조회 또는 새 세션 생성.
        - 활성 세션(completed_at IS NULL)이 있으면 반환
        - 없으면 새 세션 생성
        """
        # 활성 세션 조회
        active = await self.get_active_session(store_id, table_id)
        if active is not None:
            return active

        # 새 세션 생성
        new_session = SessionModel(
            store_id=store_id,
            table_id=table_id,
        )
        self.db.add(new_session)
        await self.db.flush()
        return new_session

    async def get_active_session(
        self, store_id: uuid.UUID, table_id: uuid.UUID
    ) -> Optional[SessionModel]:
        """현재 활성 세션 조회 (completed_at IS NULL)"""
        stmt = select(SessionModel).where(
            and_(
                SessionModel.store_id == store_id,
                SessionModel.table_id == table_id,
                SessionModel.completed_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # complete_session은 팀원 B가 AdminTableRouter에서 구현 예정
    # 아래는 인터페이스만 정의
    async def complete_session(
        self, store_id: uuid.UUID, table_id: uuid.UUID, table_number: int
    ) -> Optional[SessionModel]:
        """
        세션 종료 (이용 완료).
        팀원 B가 상세 구현 예정.
        - 활성 세션의 completed_at 설정
        - SSE 이벤트 발행
        """
        from datetime import datetime, timezone

        active = await self.get_active_session(store_id, table_id)
        if active is None:
            return None

        active.completed_at = datetime.now(timezone.utc)
        await self.db.flush()

        # SSE 이벤트 발행
        await self.sse.publish_event(
            store_id=store_id,
            table_number=table_number,
            event_type="session_completed",
            data={"session_id": str(active.id), "table_number": table_number},
        )

        return active
