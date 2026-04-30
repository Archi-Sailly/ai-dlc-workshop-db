"""
SSE(Server-Sent Events) 서비스.
인메모리 연결 풀을 관리하고, 이벤트를 구독자에게 발행합니다.

구독 구조:
- 테이블 단위: 고객용 (해당 테이블 이벤트만 수신)
- 매장 단위: 관리자용 (매장 전체 이벤트 수신)

이벤트 타입:
- order_created: 신규 주문 생성
- order_status_changed: 주문 상태 변경
- order_deleted: 주문 삭제
- session_completed: 세션 종료 (이용 완료)
"""

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator

from app.config import get_settings

settings = get_settings()


class SSEService:
    """SSE 연결 관리 및 이벤트 발행 서비스 (싱글톤)"""

    def __init__(self):
        # 테이블 단위 구독자: {(store_id, table_number): {connection_id: queue}}
        self._table_subscribers: dict[
            tuple[uuid.UUID, int], dict[str, asyncio.Queue]
        ] = {}
        # 매장 단위 구독자: {store_id: {connection_id: queue}}
        self._store_subscribers: dict[
            uuid.UUID, dict[str, asyncio.Queue]
        ] = {}

    async def subscribe_table(
        self, store_id: uuid.UUID, table_number: int
    ) -> AsyncGenerator[str, None]:
        """
        고객용 테이블 단위 SSE 구독.
        해당 테이블의 주문 이벤트만 수신합니다.
        """
        key = (store_id, table_number)
        connection_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()

        # 구독자 등록
        if key not in self._table_subscribers:
            self._table_subscribers[key] = {}
        self._table_subscribers[key][connection_id] = queue

        try:
            while True:
                try:
                    # 하트비트 간격으로 이벤트 대기
                    data = await asyncio.wait_for(
                        queue.get(),
                        timeout=settings.SSE_HEARTBEAT_INTERVAL,
                    )
                    yield data
                except asyncio.TimeoutError:
                    # 하트비트 전송
                    yield self._format_sse_event("heartbeat", {"ping": True})
        finally:
            # 연결 해제 시 구독자 제거
            self._table_subscribers.get(key, {}).pop(connection_id, None)
            if key in self._table_subscribers and not self._table_subscribers[key]:
                del self._table_subscribers[key]

    async def subscribe_store(
        self, store_id: uuid.UUID
    ) -> AsyncGenerator[str, None]:
        """
        관리자용 매장 단위 SSE 구독.
        매장 전체 테이블의 주문 이벤트를 수신합니다.
        """
        connection_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()

        # 구독자 등록
        if store_id not in self._store_subscribers:
            self._store_subscribers[store_id] = {}
        self._store_subscribers[store_id][connection_id] = queue

        try:
            while True:
                try:
                    data = await asyncio.wait_for(
                        queue.get(),
                        timeout=settings.SSE_HEARTBEAT_INTERVAL,
                    )
                    yield data
                except asyncio.TimeoutError:
                    yield self._format_sse_event("heartbeat", {"ping": True})
        finally:
            self._store_subscribers.get(store_id, {}).pop(connection_id, None)
            if store_id in self._store_subscribers and not self._store_subscribers[store_id]:
                del self._store_subscribers[store_id]

    async def publish_event(
        self,
        store_id: uuid.UUID,
        table_number: int,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """
        SSE 이벤트 발행.
        해당 테이블 구독자 + 해당 매장 구독자 모두에게 전달합니다.
        트랜잭션 커밋 후 호출해야 데이터 일관성이 보장됩니다.
        """
        event_str = self._format_sse_event(event_type, data)

        # 1. 테이블 단위 구독자에게 전달 (고객)
        table_key = (store_id, table_number)
        table_subs = self._table_subscribers.get(table_key, {})
        for queue in table_subs.values():
            try:
                queue.put_nowait(event_str)
            except asyncio.QueueFull:
                pass  # 큐가 가득 차면 건너뜀

        # 2. 매장 단위 구독자에게 전달 (관리자)
        store_subs = self._store_subscribers.get(store_id, {})
        for queue in store_subs.values():
            try:
                queue.put_nowait(event_str)
            except asyncio.QueueFull:
                pass

    def get_connection_count(self) -> dict[str, int]:
        """현재 연결 수 조회 (디버깅용)"""
        table_count = sum(len(subs) for subs in self._table_subscribers.values())
        store_count = sum(len(subs) for subs in self._store_subscribers.values())
        return {"table_connections": table_count, "store_connections": store_count}

    @staticmethod
    def _format_sse_event(event_type: str, data: dict[str, Any]) -> str:
        """SSE 이벤트 포맷으로 변환"""
        # UUID를 문자열로 변환하는 커스텀 직렬화
        def default_serializer(obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            if hasattr(obj, "__str__"):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        json_data = json.dumps(data, default=default_serializer, ensure_ascii=False)
        return f"event: {event_type}\ndata: {json_data}\n\n"


# 싱글톤 인스턴스
sse_service = SSEService()


def get_sse_service() -> SSEService:
    """SSE 서비스 싱글톤 반환"""
    return sse_service
