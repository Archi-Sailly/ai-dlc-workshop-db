"""
FastAPI 애플리케이션 엔트리포인트.
모든 라우터, 미들웨어, 이벤트 핸들러를 등록합니다.

실행: uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 이벤트 핸들러"""
    # 시작 시
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작")
    yield
    # 종료 시
    print(f"👋 {settings.APP_NAME} 종료")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 이미지 정적 파일 서빙
# StaticFiles는 uploads 디렉토리가 존재할 때만 마운트
import os
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# === 라우터 등록 ===

# 팀원 A 담당: Order, SSE, 고객 주문
from app.routers import admin_order
from app.routers import customer_order
from app.routers import sse

app.include_router(admin_order.router)
app.include_router(customer_order.router)
app.include_router(sse.router)

# 팀원 B 담당: Auth, Menu, Table/Session (구현 후 아래 주석 해제)
# from app.routers import admin_auth
# from app.routers import admin_menu
# from app.routers import admin_table
# from app.routers import customer_menu    # 고객 메뉴 조회
# from app.routers import customer_table   # 고객 테이블 검증

# app.include_router(admin_auth.router)
# app.include_router(admin_menu.router)
# app.include_router(admin_table.router)
# app.include_router(customer_menu.router)
# app.include_router(customer_table.router)


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "service": settings.APP_NAME}
