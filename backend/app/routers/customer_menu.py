"""
고객용 메뉴 조회 API 라우터.
담당 스토리: US-C03(카테고리별 메뉴 조회)
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.menu_schemas import (
    CategoryListResponse,
    CategoryResponse,
    MenuDetailResponse,
    MenuListResponse,
    MenuResponse,
)
from app.services.file_service import FileService
from app.services.menu_service import MenuService

router = APIRouter(
    prefix="/api/stores/{store_id}",
    tags=["customer-menus"],
)


@router.get("/menus", response_model=MenuListResponse)
async def get_menus(
    store_id: uuid.UUID,
    category_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    카테고리별 메뉴 목록 조회 (US-C03).
    - 판매 가능한 메뉴만 표시 (is_available=True)
    - 카테고리 필터링 지원
    - 정렬 순서 적용
    """
    service = MenuService(db)
    menus = await service.get_menus(
        store_id, category_id, available_only=True
    )
    menu_responses = [
        MenuResponse(
            id=m.id,
            store_id=m.store_id,
            category_id=m.category_id,
            name=m.name,
            price=m.price,
            description=m.description,
            image_url=FileService.get_image_url(m.image_path),
            sort_order=m.sort_order,
            is_available=m.is_available,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
        for m in menus
    ]
    return MenuListResponse(menus=menu_responses, total=len(menu_responses))


@router.get("/menus/{menu_id}", response_model=MenuDetailResponse)
async def get_menu_detail(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """메뉴 상세 조회"""
    service = MenuService(db)
    menu = await service.get_menu_detail(store_id, menu_id)
    return MenuDetailResponse(
        id=menu.id,
        store_id=menu.store_id,
        category_id=menu.category_id,
        name=menu.name,
        price=menu.price,
        description=menu.description,
        image_url=FileService.get_image_url(menu.image_path),
        sort_order=menu.sort_order,
        is_available=menu.is_available,
        created_at=menu.created_at,
        updated_at=menu.updated_at,
        category_name=menu.category.name if menu.category else None,
    )


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """카테고리 목록 조회"""
    service = MenuService(db)
    categories = await service.get_categories(store_id)
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(c) for c in categories],
        total=len(categories),
    )
