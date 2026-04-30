# 테이블오더 서비스 - Unit of Work 정의서

## 설계 결정사항

| 항목 | 결정 |
|---|---|
| 배포 모델 | 마이크로서비스 (도메인별 Backend 분리 + Frontend 2개) |
| 개발 순서 | 데이터 모델 우선 (DB 스키마 → API → UI) |
| 백엔드 모듈 분리 | 도메인 기준 (주문, 메뉴, 테이블/세션, 인증, SSE) |

---

## 유닛 목록 요약

| # | 유닛 | 유형 | 기술 스택 | 스토리 수 |
|---|---|---|---|---|
| U1 | Database Schema | 데이터 모델 | PostgreSQL + Alembic | — (기반) |
| U2 | Auth Service | 백엔드 서비스 | FastAPI + JWT + bcrypt | 2 |
| U3 | Menu Service | 백엔드 서비스 | FastAPI + SQLAlchemy | 6 |
| U4 | Table & Session Service | 백엔드 서비스 | FastAPI + SQLAlchemy | 3 |
| U5 | Order Service | 백엔드 서비스 | FastAPI + SQLAlchemy | 6 |
| U6 | SSE Service | 백엔드 서비스 | FastAPI + SSE | 2 |
| U7 | Customer App | 프론트엔드 | React + TypeScript + Zustand | 8 |
| U8 | Admin App | 프론트엔드 | React + TypeScript + Zustand | 14 |

---

## 유닛 상세 정의

### U1: Database Schema
**유형**: 데이터 모델 (기반 인프라)
**책임**: 전체 시스템의 PostgreSQL 데이터베이스 스키마 정의 및 마이그레이션

**범위**:
- 모든 테이블 스키마 정의 (stores, admin_users, tables, sessions, orders, order_items, menus, categories, login_attempts)
- Alembic 마이그레이션 설정 및 초기 마이그레이션 생성
- 인덱스, 제약 조건, 외래 키 정의
- 시드 데이터 (초기 매장, 관리자 계정)

**기술 스택**: PostgreSQL, SQLAlchemy ORM (모델 정의), Alembic

**산출물**:
```
database/
  alembic/
    versions/          # 마이그레이션 파일
    env.py
  models/
    __init__.py
    store.py           # Store 모델
    admin_user.py      # AdminUser 모델
    table.py           # Table 모델
    session.py         # Session 모델
    order.py           # Order, OrderItem 모델
    menu.py            # Menu, Category 모델
    login_attempt.py   # LoginAttempt 모델
  alembic.ini
  seed.py              # 시드 데이터
```

**개발 순서**: 1단계 (최우선 — 모든 서비스의 기반)

---

### U2: Auth Service
**유형**: 백엔드 마이크로서비스
**책임**: 관리자 인증, JWT 토큰 관리, 로그인 시도 제한

**범위**:
- 관리자 로그인 API (매장 식별자 + 사용자명 + 비밀번호)
- JWT 토큰 발급 (16시간 만료) 및 검증
- bcrypt 비밀번호 해싱/검증
- 로그인 시도 제한 (연속 실패 시 차단)
- JWT 미들웨어 (다른 서비스에서 공유 가능한 라이브러리)

**컴포넌트**: AdminAuthRouter, AuthService, AuthDomain, AdminUserRepository

**기술 스택**: FastAPI, PyJWT, bcrypt, SQLAlchemy

**산출물**:
```
services/auth-service/
  app/
    routers/auth.py
    services/auth_service.py
    domain/auth_domain.py
    repositories/admin_user_repository.py
    middleware/jwt_middleware.py
    schemas/auth_schemas.py
    config.py
    main.py
  tests/
  requirements.txt
```

**개발 순서**: 2단계 (DB 스키마 완성 후)

---

### U3: Menu Service
**유형**: 백엔드 마이크로서비스
**책임**: 메뉴 CRUD, 카테고리 관리, 이미지 업로드, 메뉴 노출 순서 관리

**범위**:
- 메뉴 등록/조회/수정/삭제 API
- 카테고리 등록/조회 API
- 이미지 파일 업로드 (FastAPI UploadFile)
- 메뉴 노출 순서 조정 API
- 고객용 메뉴 조회 API (카테고리별, 정렬 순서 적용)

**컴포넌트**: AdminMenuRouter, CustomerRouter(메뉴 부분), MenuService, MenuDomain, MenuRepository, FileService

**기술 스택**: FastAPI, SQLAlchemy, python-multipart

**산출물**:
```
services/menu-service/
  app/
    routers/
      admin_menu.py
      customer_menu.py
    services/
      menu_service.py
      file_service.py
    domain/menu_domain.py
    repositories/menu_repository.py
    schemas/menu_schemas.py
    config.py
    main.py
  uploads/              # 이미지 저장 디렉토리
  tests/
  requirements.txt
```

**개발 순서**: 2단계 (DB 스키마 완성 후, Auth와 병렬 가능)

---

### U4: Table & Session Service
**유형**: 백엔드 마이크로서비스
**책임**: 테이블 등록/관리, 세션 라이프사이클 관리, 테이블 유효성 검증

**범위**:
- 테이블 등록 API (중복 체크, URL 생성)
- 테이블 목록 조회 API
- 테이블 유효성 검증 API (고객 접근 시)
- 세션 생성/조회/종료 API
- 세션 라이프사이클 관리 (자동 생성, 이용 완료)

**컴포넌트**: AdminTableRouter, CustomerRouter(테이블 부분), TableService, SessionService, TableDomain, SessionDomain, TableRepository, SessionRepository, StoreRepository

**기술 스택**: FastAPI, SQLAlchemy

**산출물**:
```
services/table-session-service/
  app/
    routers/
      admin_table.py
      customer_table.py
    services/
      table_service.py
      session_service.py
    domain/
      table_domain.py
      session_domain.py
    repositories/
      table_repository.py
      session_repository.py
      store_repository.py
    schemas/
      table_schemas.py
      session_schemas.py
    config.py
    main.py
  tests/
  requirements.txt
```

**개발 순서**: 2단계 (DB 스키마 완성 후, Auth/Menu와 병렬 가능)

---

### U5: Order Service
**유형**: 백엔드 마이크로서비스
**책임**: 주문 생성, 상태 변경, 삭제, 대시보드 데이터, 주문 내역 조회

**범위**:
- 주문 생성 API (세션 자동 생성/귀속 연동)
- 주문 상태 변경 API (4단계 순차)
- 주문 삭제 API (대기중/접수 상태만)
- 대시보드 데이터 조회 API
- 주문 상세/내역 조회 API
- 과거 주문 내역 조회 API (날짜 필터링, 페이지네이션)
- SSE Service 연동 (이벤트 발행)

**컴포넌트**: AdminOrderRouter, CustomerRouter(주문 부분), OrderService, OrderDomain, OrderRepository

**기술 스택**: FastAPI, SQLAlchemy

**산출물**:
```
services/order-service/
  app/
    routers/
      admin_order.py
      customer_order.py
    services/order_service.py
    domain/order_domain.py
    repositories/order_repository.py
    schemas/order_schemas.py
    config.py
    main.py
  tests/
  requirements.txt
```

**개발 순서**: 3단계 (Table & Session Service 완성 후 — 세션 연동 필요)

---

### U6: SSE Service
**유형**: 백엔드 마이크로서비스
**책임**: SSE 연결 관리, 이벤트 발행, 구독자 관리

**범위**:
- 고객용 SSE 엔드포인트 (테이블 단위 구독)
- 관리자용 SSE 엔드포인트 (매장 단위 구독)
- 이벤트 수신 API (다른 서비스에서 호출)
- 인메모리 연결 풀 관리
- 하트비트 (30초 간격)
- 자동 재연결 지원

**컴포넌트**: SSERouter, SSEService, SSEManager

**기술 스택**: FastAPI, sse-starlette

**산출물**:
```
services/sse-service/
  app/
    routers/sse.py
    services/sse_service.py
    manager/sse_manager.py
    schemas/sse_schemas.py
    config.py
    main.py
  tests/
  requirements.txt
```

**개발 순서**: 3단계 (Order Service와 병렬 — 이벤트 발행/수신 인터페이스 정의 후)

---

### U7: Customer App
**유형**: 프론트엔드 SPA
**책임**: 고객용 주문 인터페이스 (메뉴 조회, 장바구니, 주문, 주문 내역)

**범위**:
- 테이블 식별 (URL 기반 접근)
- 카테고리별 메뉴 조회
- 장바구니 관리 (localStorage 영속화)
- 주문 확정 및 성공 화면
- 주문 내역 조회
- 주문 상태 실시간 업데이트 (SSE)

**컴포넌트**: 페이지 6개, 공통 UI 9개, 훅 4개, 스토어 3개

**기술 스택**: React, TypeScript, Zustand, React Router, Vite

**산출물**:
```
frontend/customer-app/
  src/
    pages/
    components/
    hooks/
    stores/
    api/              # API 클라이언트
    types/            # TypeScript 타입 정의
    App.tsx
    main.tsx
  public/
  package.json
  vite.config.ts
  tsconfig.json
```

**개발 순서**: 4단계 (백엔드 API 완성 후)

---

### U8: Admin App
**유형**: 프론트엔드 SPA
**책임**: 관리자용 매장 관리 인터페이스 (대시보드, 주문/테이블/메뉴 관리)

**범위**:
- 관리자 로그인
- 실시간 주문 대시보드 (SSE)
- 주문 상세 보기 및 상태 변경
- 주문 삭제 (상태 제한)
- 테이블 등록 및 이용 완료
- 메뉴 CRUD 및 순서 조정
- 과거 주문 내역 조회

**컴포넌트**: 페이지 7개, 공통 UI 10개, 훅 6개, 스토어 4개

**기술 스택**: React, TypeScript, Zustand, React Router, Vite

**산출물**:
```
frontend/admin-app/
  src/
    pages/
    components/
    hooks/
    stores/
    api/              # API 클라이언트 (JWT 인터셉터 포함)
    types/            # TypeScript 타입 정의
    App.tsx
    main.tsx
  public/
  package.json
  vite.config.ts
  tsconfig.json
```

**개발 순서**: 4단계 (백엔드 API 완성 후, Customer App과 병렬)

---

## 코드 조직 전략 (Greenfield)

### 전체 디렉토리 구조

```
/ (workspace root)
├── database/                    # U1: Database Schema
│   ├── alembic/
│   ├── models/
│   ├── alembic.ini
│   └── seed.py
│
├── services/                    # U2~U6: Backend Microservices
│   ├── auth-service/
│   ├── menu-service/
│   ├── table-session-service/
│   ├── order-service/
│   └── sse-service/
│
├── shared/                      # 공유 라이브러리
│   ├── jwt_utils.py             # JWT 검증 유틸 (Auth → 다른 서비스)
│   ├── db_config.py             # DB 연결 공통 설정
│   └── schemas/                 # 공유 스키마 (서비스 간 통신)
│
├── frontend/                    # U7~U8: Frontend Apps
│   ├── customer-app/
│   └── admin-app/
│
├── aidlc-docs/                  # AI-DLC 문서 (코드 아님)
└── aidlc-workshop/              # 워크숍 프로젝트 (코드 아님)
```

### 서비스 간 통신 방식
- **동기 통신**: HTTP REST (서비스 간 내부 API 호출)
- **비동기 통신**: Order Service → SSE Service (이벤트 발행 HTTP POST)
- **공유 DB**: 모든 백엔드 서비스가 동일 PostgreSQL 인스턴스 접근 (Shared Database 패턴)

---

## 개발 순서 로드맵

```
단계 1: U1 (Database Schema)
  │
  ▼
단계 2: U2 (Auth) + U3 (Menu) + U4 (Table & Session)  [병렬]
  │
  ▼
단계 3: U5 (Order) + U6 (SSE)  [병렬]
  │
  ▼
단계 4: U7 (Customer App) + U8 (Admin App)  [병렬]
```
