"""
세션 도메인 규칙.
- 새 세션 생성 필요 여부 판단
- 세션 종료 가능 여부 판단
"""

from typing import Optional

from app.models.session import Session


class SessionDomain:
    """세션 비즈니스 규칙"""

    @staticmethod
    def should_create_new_session(active_session: Optional[Session]) -> bool:
        """새 세션 생성 필요 여부 판단 (활성 세션이 없으면 True)"""
        return active_session is None

    @staticmethod
    def can_complete_session(session: Optional[Session]) -> bool:
        """세션 종료 가능 여부 판단 (활성 세션이 있어야 True)"""
        if session is None:
            return False
        return session.completed_at is None
