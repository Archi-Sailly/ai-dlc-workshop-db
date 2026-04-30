"""
메뉴 도메인 규칙.
- 메뉴 데이터 유효성 검증
- 이미지 파일 유효성 검증
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.config import get_settings

settings = get_settings()


@dataclass
class ValidationResult:
    """유효성 검증 결과"""
    valid: bool
    message: str = ""


class MenuDomain:
    """메뉴 비즈니스 규칙"""

    @staticmethod
    def validate_menu_data(
        name: Optional[str] = None,
        price: Optional[Decimal] = None,
    ) -> ValidationResult:
        """메뉴 데이터 유효성 검증 (필수 필드, 가격 양수)"""
        if name is not None and len(name.strip()) == 0:
            return ValidationResult(valid=False, message="메뉴명은 비어있을 수 없습니다.")
        if price is not None and price <= 0:
            return ValidationResult(valid=False, message="가격은 양수여야 합니다.")
        return ValidationResult(valid=True)

    @staticmethod
    def validate_image_file(content_type: str, size: int) -> ValidationResult:
        """이미지 파일 유효성 검증 (타입, 크기)"""
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            allowed = ", ".join(settings.ALLOWED_IMAGE_TYPES)
            return ValidationResult(
                valid=False,
                message=f"허용되지 않는 이미지 형식입니다. 허용: {allowed}",
            )
        max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if size > max_size:
            return ValidationResult(
                valid=False,
                message=f"이미지 크기가 {settings.MAX_IMAGE_SIZE_MB}MB를 초과합니다.",
            )
        return ValidationResult(valid=True)
