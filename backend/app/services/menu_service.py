"""
메뉴 서비스 (메뉴 CRUD, 카테고리 관리, 이미지 처리).
담당 스토리: US-C03(메뉴 조회), US-A10~A14(메뉴 관리)

의존성:
- MenuDomain: 메뉴 데이터 검증
- MenuRepository: 메뉴/카테고리 CRUD
- FileService: 이미지 업로드/삭제
"""

import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.menu_domain import MenuDomain
from app.models.menu import Category, Menu
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_schemas import CreateMenuRequest, UpdateMenuRequest
from app.services.file_service import FileService


class MenuService:
    """메뉴 비즈니스 오케스트레이션"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.menu_repo = MenuRepository(db)
        self.domain = MenuDomain()
        self.file_service = FileService()

    # === Menu ===

    async def get_menus(
        self,
        store_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        available_only: bool = False,
    ) -> list[Menu]:
        """메뉴 목록 조회 (카테고리 필터, 정렬 순서 적용)"""
        return await self.menu_repo.get_by_store(
            store_id, category_id, available_only
        )

    async def get_menu_detail(
        self, store_id: uuid.UUID, menu_id: uuid.UUID
    ) -> Menu:
        """메뉴 상세 조회"""
        menu = await self.menu_repo.get_by_id(menu_id)
        if not menu or menu.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="메뉴를 찾을 수 없습니다.",
            )
        return menu

    async def create_menu(
        self,
        store_id: uuid.UUID,
        menu_data: CreateMenuRequest,
        image_file: UploadFile | None = None,
    ) -> Menu:
        """메뉴 등록 (US-A10) + 이미지 업로드"""
        # 유효성 검증
        validation = self.domain.validate_menu_data(
            name=menu_data.name, price=menu_data.price
        )
        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation.message,
            )

        # 카테고리 존재 확인
        category = await self.menu_repo.get_category_by_id(menu_data.category_id)
        if not category or category.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효하지 않은 카테고리입니다.",
            )

        # 이미지 업로드
        image_path = None
        if image_file:
            try:
                image_path = await self.file_service.upload_image(
                    image_file, store_id
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        # 메뉴 생성
        data = {
            "store_id": store_id,
            "category_id": menu_data.category_id,
            "name": menu_data.name,
            "price": menu_data.price,
            "description": menu_data.description,
            "image_path": image_path,
            "sort_order": menu_data.sort_order,
        }
        menu = await self.menu_repo.create(data)
        await self.db.commit()
        return menu

    async def update_menu(
        self,
        store_id: uuid.UUID,
        menu_id: uuid.UUID,
        menu_data: UpdateMenuRequest,
        image_file: UploadFile | None = None,
    ) -> Menu:
        """메뉴 수정 (US-A12) + 이미지 교체"""
        existing = await self.menu_repo.get_by_id(menu_id)
        if not existing or existing.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="메뉴를 찾을 수 없습니다.",
            )

        # 유효성 검증
        validation = self.domain.validate_menu_data(
            name=menu_data.name, price=menu_data.price
        )
        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation.message,
            )

        # 카테고리 변경 시 확인
        if menu_data.category_id:
            category = await self.menu_repo.get_category_by_id(
                menu_data.category_id
            )
            if not category or category.store_id != store_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="유효하지 않은 카테고리입니다.",
                )

        # 이미지 교체
        update_data: dict = {}
        if image_file:
            try:
                new_path = await self.file_service.upload_image(
                    image_file, store_id
                )
                if existing.image_path:
                    await self.file_service.delete_image(existing.image_path)
                update_data["image_path"] = new_path
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )

        # 변경 필드 적용
        for field in [
            "name", "price", "description", "category_id", "sort_order", "is_available"
        ]:
            value = getattr(menu_data, field, None)
            if value is not None:
                update_data[field] = value

        if not update_data:
            return existing

        menu = await self.menu_repo.update(menu_id, update_data)
        await self.db.commit()
        return menu

    async def delete_menu(
        self, store_id: uuid.UUID, menu_id: uuid.UUID
    ) -> bool:
        """메뉴 삭제 (US-A13) + 이미지 파일 삭제"""
        existing = await self.menu_repo.get_by_id(menu_id)
        if not existing or existing.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="메뉴를 찾을 수 없습니다.",
            )

        if existing.image_path:
            await self.file_service.delete_image(existing.image_path)

        result = await self.menu_repo.delete(menu_id)
        await self.db.commit()
        return result

    async def reorder_menus(
        self, store_id: uuid.UUID, menu_orders: list[dict]
    ) -> bool:
        """메뉴 노출 순서 일괄 변경 (US-A14)"""
        result = await self.menu_repo.update_sort_orders(menu_orders)
        await self.db.commit()
        return result

    # === Category ===

    async def get_categories(self, store_id: uuid.UUID) -> list[Category]:
        """카테고리 목록 조회"""
        return await self.menu_repo.get_categories(store_id)

    async def create_category(
        self, store_id: uuid.UUID, name: str, sort_order: int = 0
    ) -> Category:
        """카테고리 등록"""
        category = await self.menu_repo.create_category(
            {"store_id": store_id, "name": name, "sort_order": sort_order}
        )
        await self.db.commit()
        return category
