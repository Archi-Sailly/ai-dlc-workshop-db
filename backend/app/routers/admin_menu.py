"""
관리자 메뉴 관리 API 라우터.
담당 스토리: US-A10(등록), US-A11(조회), US-A12(수정), US-A13(삭제), US-A14(순서 조정)
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.jwt_middleware import get_current_admin
from app.schemas.auth_schemas import TokenPayload
from app.schemas.menu_schemas import (
    CategoryListResponse,
    CategoryResponse,
    CreateCategoryRequest,
    CreateMenuRequest,
    DeleteResponse,
    MenuDetailResponse,
    MenuListResponse,
    MenuResponse,
    ReorderMenuRequest,
    SuccessResponse,
    UpdateMenuRequest,
)
from app.services.file_service import FileService
from app.services.menu_service import MenuService

router = APIRouter(
    prefix="/api/admin/stores/{store_id}",
    tags=["admin-menus"],
)


def _menu_to_response(menu) -> MenuResponse:
    """Menu 모델을 MenuResponse로 변환"""
    return MenuResponse(
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
    )


# === Menu ===


@router.post("/menus", response_model=MenuResponse)
async def create_menu(
    store_id: uuid.UUID,
    name: str = Form(...),
    price: float = Form(...),
    category_id: uuid.UUID = Form(...),
    description: str | None = Form(default=None),
    sort_order: int = Form(default=0),
    image: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """
    메뉴 등록 (US-A10).
    multipart/form-data로 메뉴 정보와 이미지를 함께 업로드합니다.
    - 필수: 메뉴명, 가격, 카테고리
    - 선택: 설명, 이미지, 정렬 순서
    """
    from decimal import Decimal

    menu_data = CreateMenuRequest(
        name=name,
        price=Decimal(str(price)),
        category_id=category_id,
        description=description,
        sort_order=sort_order,
    )
    service = MenuService(db)
    menu = await service.create_menu(store_id, menu_data, image)
    return _menu_to_response(menu)


@router.get("/menus", response_model=MenuListResponse)
async def get_menus(
    store_id: uuid.UUID,
    category_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """메뉴 목록 조회 (US-A11)"""
    service = MenuService(db)
    menus = await service.get_menus(store_id, category_id)
    return MenuListResponse(
        menus=[_menu_to_response(m) for m in menus],
        total=len(menus),
    )


@router.get("/menus/{menu_id}", response_model=MenuDetailResponse)
async def get_menu_detail(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """메뉴 상세 조회"""
    service = MenuService(db)
    menu = await service.get_menu_detail(store_id, menu_id)
    return MenuDetailResponse(
        **_menu_to_response(menu).model_dump(),
        category_name=menu.category.name if menu.category else None,
    )


@router.put("/menus/{menu_id}", response_model=MenuResponse)
async def update_menu(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    name: str | None = Form(default=None),
    price: float | None = Form(default=None),
    category_id: uuid.UUID | None = Form(default=None),
    description: str | None = Form(default=None),
    sort_order: int | None = Form(default=None),
    is_available: bool | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """메뉴 수정 (US-A12)"""
    from decimal import Decimal

    menu_data = UpdateMenuRequest(
        name=name,
        price=Decimal(str(price)) if price is not None else None,
        category_id=category_id,
        description=description,
        sort_order=sort_order,
        is_available=is_available,
    )
    service = MenuService(db)
    menu = await service.update_menu(store_id, menu_id, menu_data, image)
    return _menu_to_response(menu)


@router.delete("/menus/{menu_id}", response_model=DeleteResponse)
async def delete_menu(
    store_id: uuid.UUID,
    menu_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """메뉴 삭제 (US-A13)"""
    service = MenuService(db)
    await service.delete_menu(store_id, menu_id)
    return DeleteResponse()


@router.patch("/menus/reorder", response_model=SuccessResponse)
async def reorder_menus(
    store_id: uuid.UUID,
    request: ReorderMenuRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """메뉴 노출 순서 조정 (US-A14)"""
    service = MenuService(db)
    orders = [
        {"menu_id": item.menu_id, "sort_order": item.sort_order}
        for item in request.menu_orders
    ]
    await service.reorder_menus(store_id, orders)
    return SuccessResponse(message="메뉴 순서가 변경되었습니다.")


# === Category ===


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    store_id: uuid.UUID,
    request: CreateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """카테고리 등록"""
    service = MenuService(db)
    return await service.create_category(
        store_id, request.name, request.sort_order
    )


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    store_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(get_current_admin),
):
    """카테고리 목록 조회"""
    service = MenuService(db)
    categories = await service.get_categories(store_id)
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(c) for c in categories],
        total=len(categories),
    )
