"""
시드 데이터 스크립트.
초기 매장, 관리자 계정, 테이블, 카테고리, 샘플 메뉴를 생성합니다.

사용법:
    python seed.py
"""

import asyncio
import uuid
from decimal import Decimal

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, engine, Base
from app.models.store import Store
from app.models.admin_user import AdminUser
from app.models.table import Table
from app.models.menu import Category, Menu


def hash_password(password: str) -> str:
    """bcrypt 비밀번호 해싱"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def seed_data():
    """시드 데이터 생성"""

    # 테이블 생성 (개발 환경용 — 프로덕션에서는 Alembic 사용)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 이미 시드 데이터가 있는지 확인
        result = await session.execute(select(Store).limit(1))
        if result.scalar_one_or_none():
            print("시드 데이터가 이미 존재합니다. 건너뜁니다.")
            return

        # === 매장 생성 ===
        store = Store(
            id=uuid.uuid4(),
            identifier="demo-store",
            name="데모 매장",
            is_active=True,
        )
        session.add(store)
        await session.flush()

        print(f"매장 생성: {store.name} (ID: {store.id})")

        # === 관리자 계정 생성 ===
        admin_users = [
            AdminUser(
                store_id=store.id,
                username="admin",
                password_hash=hash_password("admin1234"),
                display_name="점장 이상호",
            ),
            AdminUser(
                store_id=store.id,
                username="manager",
                password_hash=hash_password("manager1234"),
                display_name="홀매니저 최수진",
            ),
            AdminUser(
                store_id=store.id,
                username="staff",
                password_hash=hash_password("staff1234"),
                display_name="카운터 정하은",
            ),
        ]
        session.add_all(admin_users)
        print(f"관리자 계정 {len(admin_users)}개 생성")

        # === 테이블 생성 (10개) ===
        tables = []
        for i in range(1, 11):
            t = Table(
                store_id=store.id,
                table_number=i,
                is_active=True,
            )
            tables.append(t)
        session.add_all(tables)
        print(f"테이블 {len(tables)}개 생성 (1~10번)")

        # === 카테고리 생성 ===
        categories_data = [
            ("메인 메뉴", 1),
            ("사이드", 2),
            ("음료", 3),
            ("디저트", 4),
        ]
        categories = {}
        for name, sort_order in categories_data:
            cat = Category(
                store_id=store.id,
                name=name,
                sort_order=sort_order,
            )
            session.add(cat)
            await session.flush()
            categories[name] = cat

        print(f"카테고리 {len(categories)}개 생성")

        # === 샘플 메뉴 생성 ===
        menus_data = [
            # (카테고리, 메뉴명, 가격, 설명, 순서)
            ("메인 메뉴", "김치찌개", 9000, "돼지고기와 묵은지로 끓인 김치찌개", 1),
            ("메인 메뉴", "된장찌개", 8000, "두부와 야채가 들어간 된장찌개", 2),
            ("메인 메뉴", "제육볶음", 11000, "매콤한 돼지고기 제육볶음", 3),
            ("메인 메뉴", "불고기", 13000, "달콤한 양념의 소불고기", 4),
            ("메인 메뉴", "비빔밥", 9500, "신선한 야채와 고추장 비빔밥", 5),
            ("사이드", "계란말이", 5000, "부드러운 계란말이", 1),
            ("사이드", "김치전", 7000, "바삭한 김치전", 2),
            ("사이드", "떡볶이", 6000, "매콤달콤 떡볶이", 3),
            ("음료", "콜라", 2000, "코카콜라 355ml", 1),
            ("음료", "사이다", 2000, "칠성사이다 355ml", 2),
            ("음료", "맥주", 5000, "생맥주 500ml", 3),
            ("음료", "소주", 5000, "참이슬 360ml", 4),
            ("디저트", "아이스크림", 3000, "바닐라 아이스크림", 1),
            ("디저트", "식혜", 3000, "전통 식혜", 2),
        ]

        for cat_name, menu_name, price, desc, sort_order in menus_data:
            menu = Menu(
                store_id=store.id,
                category_id=categories[cat_name].id,
                name=menu_name,
                description=desc,
                price=Decimal(str(price)),
                sort_order=sort_order,
                is_available=True,
            )
            session.add(menu)

        print(f"샘플 메뉴 {len(menus_data)}개 생성")

        # 커밋
        await session.commit()
        print("\n시드 데이터 생성 완료!")
        print(f"  매장 식별자: demo-store")
        print(f"  관리자 계정: admin / admin1234")
        print(f"  테이블: 1~10번")
        print(f"  카테고리: {len(categories)}개")
        print(f"  메뉴: {len(menus_data)}개")


if __name__ == "__main__":
    asyncio.run(seed_data())
