"""
주문 도메인 규칙.
- 주문 상태 전이 검증: PENDING → ACCEPTED → PREPARING → COMPLETED
- 삭제 가능 여부: PENDING, ACCEPTED만 가능
- 주문 총액 계산
"""

from decimal import Decimal

from app.models.order import OrderStatus


class OrderDomain:
    """주문 비즈니스 규칙"""

    # 허용되는 상태 전이 맵
    VALID_TRANSITIONS: dict[OrderStatus, OrderStatus] = {
        OrderStatus.PENDING: OrderStatus.ACCEPTED,
        OrderStatus.ACCEPTED: OrderStatus.PREPARING,
        OrderStatus.PREPARING: OrderStatus.COMPLETED,
    }

    # 삭제 가능한 상태
    DELETABLE_STATUSES: set[OrderStatus] = {
        OrderStatus.PENDING,
        OrderStatus.ACCEPTED,
    }

    @staticmethod
    def validate_status_transition(
        current_status: OrderStatus, new_status: OrderStatus
    ) -> bool:
        """
        주문 상태 전이 유효성 검증.
        PENDING → ACCEPTED → PREPARING → COMPLETED 순서만 허용.
        """
        expected_next = OrderDomain.VALID_TRANSITIONS.get(current_status)
        return expected_next == new_status

    @staticmethod
    def can_delete(order_status: OrderStatus) -> bool:
        """
        삭제 가능 여부 판단.
        PENDING, ACCEPTED 상태만 삭제 가능.
        PREPARING, COMPLETED 상태는 삭제 불가 (조리 시작 후 삭제 방지).
        """
        return order_status in OrderDomain.DELETABLE_STATUSES

    @staticmethod
    def calculate_order_total(
        items: list[dict],
    ) -> Decimal:
        """
        주문 총액 계산.
        각 항목의 unit_price * quantity 합산.
        """
        total = Decimal("0")
        for item in items:
            unit_price = Decimal(str(item["unit_price"]))
            quantity = int(item["quantity"])
            total += unit_price * quantity
        return total

    @staticmethod
    def get_next_status(current_status: OrderStatus) -> OrderStatus | None:
        """현재 상태의 다음 상태를 반환. 마지막 상태면 None."""
        return OrderDomain.VALID_TRANSITIONS.get(current_status)
