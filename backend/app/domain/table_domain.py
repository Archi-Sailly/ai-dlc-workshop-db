"""
테이블 도메인 규칙.
- 테이블 번호 유효성 검증
- 테이블 접속 URL 생성
"""


class TableDomain:
    """테이블 비즈니스 규칙"""

    @staticmethod
    def validate_table_number(table_number: int) -> bool:
        """테이블 번호 유효성 검증 (양수만 허용)"""
        return isinstance(table_number, int) and table_number > 0

    @staticmethod
    def generate_table_url(store_id: str, table_number: int) -> str:
        """테이블 접속 URL 생성 (고객 태블릿용)"""
        return f"/store/{store_id}/table/{table_number}"
