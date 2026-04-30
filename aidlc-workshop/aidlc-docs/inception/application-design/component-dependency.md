# 테이블오더 서비스 - 컴포넌트 의존성 설계서

---

## 1. 백엔드 의존성 매트릭스

### 1.1 Router → Service 의존성

| Router | 의존 Service |
|---|---|
| CustomerRouter | OrderService, MenuService, TableService, SessionService |
| AdminAuthRouter | AuthService |
| AdminOrderRouter | OrderService |
| AdminTableRouter | TableService, SessionService |
| AdminMenuRouter | MenuService |
| SSERouter | SSEService |

### 1.2 Service → Domain / Repository 의존성

| Service | Domain | Repository | Other Service |
|---|---|---|---|
| OrderService | OrderDomain | OrderRepository | SessionService, SSEService |
| MenuService | MenuDomain | MenuRepository | FileService |
| TableService | TableDomain | TableRepository, StoreRepository | — |
| SessionService | SessionDomain | SessionRepository | SSEService |
| AuthService | AuthDomain | AdminUserRepository | — |
| SSEService | — | — | — |
| FileService | — | — | — |

### 1.3 의존성 방향 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROUTER LAYER                             │
│  CustomerRouter  AdminAuthRouter  AdminOrderRouter              │
│  AdminTableRouter  AdminMenuRouter  SSERouter                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                             │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ OrderService  │───▶│SessionService│───▶│  SSEService  │      │
│  │              │───▶│              │    │              │      │
│  └──────┬───────┘    └──────┬───────┘    └──────────────┘      │
│         │                   │                    ▲              │
│         │                   │                    │              │
│  ┌──────┴───────┐    ┌──────┴───────┐    ┌──────┴───────┐      │
│  │  MenuService │───▶│ FileService  │    │  AuthService │      │
│  └──────┬───────┘    └──────────────┘    └──────┬───────┘      │
│         │                                       │              │
│  ┌──────┴───────┐                               │              │
│  │ TableService │                               │              │
│  └──────┬───────┘                               │              │
└─────────┼───────────────────────────────────────┼──────────────┘
          │                                       │
          ▼                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DOMAIN LAYER                              │
│  OrderDomain  SessionDomain  MenuDomain  AuthDomain  TableDomain│
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REPOSITORY LAYER                            │
│  OrderRepo  MenuRepo  TableRepo  SessionRepo  StoreRepo        │
│  AdminUserRepo                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE                                  │
│                    PostgreSQL + SQLAlchemy                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 프론트엔드 의존성

### 2.1 Customer App 의존성

```
┌─────────────────────────────────────────────────┐
│                   PAGES                          │
│  MenuPage  CartPage  OrderConfirmPage            │
│  OrderHistoryPage  OrderSuccessPage  ErrorPage   │
└──────────────────────┬──────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────┐
│              COMPONENTS + HOOKS                  │
│  MenuCard  CategoryTab  CartItem  CartBadge      │
│  OrderStatusBadge  BottomNav  ConfirmDialog      │
│  useCart  useTableContext  useSSE  useOrders      │
└──────────────────────┬──────────────────────────┘
                       │ reads/writes
                       ▼
┌─────────────────────────────────────────────────┐
│            ZUSTAND STORES                        │
│  cartStore ──→ localStorage                      │
│  orderStore ──→ Backend API + SSE                │
│  tableStore ──→ URL params                       │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / SSE
                       ▼
┌─────────────────────────────────────────────────┐
│            BACKEND API                           │
│  REST API (fetch/axios)                          │
│  SSE Stream (EventSource)                        │
└─────────────────────────────────────────────────┘
```

### 2.2 Admin App 의존성

```
┌─────────────────────────────────────────────────┐
│                   PAGES                          │
│  LoginPage  DashboardPage  TableDetailPage       │
│  TableManagePage  MenuManagePage  MenuFormPage    │
│  OrderHistoryPage                                │
└──────────────────────┬──────────────────────────┘
                       │ uses
                       ▼
┌─────────────────────────────────────────────────┐
│              COMPONENTS + HOOKS                  │
│  TableCard  OrderItem  OrderStatusButton         │
│  MenuListItem  ImageUploader  DateFilter         │
│  SideNav  ConfirmDialog  Toast                   │
│  useAuth  useSSE  useDashboard  useOrders        │
│  useMenus  useTables                             │
└──────────────────────┬──────────────────────────┘
                       │ reads/writes
                       ▼
┌─────────────────────────────────────────────────┐
│            ZUSTAND STORES                        │
│  authStore ──→ JWT token (localStorage)          │
│  dashboardStore ──→ Backend API + SSE            │
│  menuStore ──→ Backend API                       │
│  tableStore ──→ Backend API                      │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / SSE
                       ▼
┌─────────────────────────────────────────────────┐
│            BACKEND API                           │
│  REST API (fetch/axios) + JWT Header             │
│  SSE Stream (EventSource) + JWT Auth             │
└─────────────────────────────────────────────────┘
```

---

## 3. 통신 패턴

### 3.1 동기 통신 (HTTP REST)

| 발신 | 수신 | 프로토콜 | 용도 |
|---|---|---|---|
| Customer App | Backend API | HTTP REST | 메뉴 조회, 주문 생성, 주문 내역 조회 |
| Admin App | Backend API | HTTP REST | 로그인, 주문 관리, 메뉴 CRUD, 테이블 관리 |

### 3.2 비동기 통신 (SSE)

| 발신 | 수신 | 프로토콜 | 용도 |
|---|---|---|---|
| Backend (SSEService) | Customer App | SSE (테이블 단위) | 주문 상태 실시간 업데이트 |
| Backend (SSEService) | Admin App | SSE (매장 단위) | 신규 주문, 상태 변경 실시간 알림 |

### 3.3 SSE 이벤트 흐름

```
[고객 주문 생성]
  → OrderService.create_order()
    → DB 저장 (트랜잭션 커밋)
    → SSEService.publish_event("order_created", order_data)
      → 해당 테이블 구독자에게 전달 (고객 화면)
      → 해당 매장 구독자에게 전달 (관리자 대시보드)

[관리자 상태 변경]
  → OrderService.update_order_status()
    → DB 업데이트 (트랜잭션 커밋)
    → SSEService.publish_event("order_status_changed", order_data)
      → 해당 테이블 구독자에게 전달 (고객 화면)
      → 해당 매장 구독자에게 전달 (관리자 대시보드)

[관리자 세션 종료]
  → SessionService.complete_session()
    → DB 업데이트 (트랜잭션 커밋)
    → SSEService.publish_event("session_completed", session_data)
      → 해당 테이블 구독자에게 전달 (고객 화면 리셋)
      → 해당 매장 구독자에게 전달 (관리자 대시보드 리셋)
```

---

## 4. 데이터 흐름 다이어그램

### 4.1 고객 주문 흐름

```
[Customer App]                    [Backend]                      [Admin App]
     │                                │                               │
     │  1. GET /menus                 │                               │
     │──────────────────────────────▶│                               │
     │  ◀── MenuListResponse         │                               │
     │                                │                               │
     │  2. 장바구니 관리 (localStorage) │                               │
     │  (클라이언트 로컬)              │                               │
     │                                │                               │
     │  3. POST /orders               │                               │
     │──────────────────────────────▶│                               │
     │                                │── SessionService              │
     │                                │── OrderRepository.create      │
     │                                │── SSEService.publish ────────▶│
     │  ◀── OrderResponse             │                    SSE event  │
     │                                │                               │
     │  4. SSE: order_status_changed  │                               │
     │  ◀─────────────────────────────│◀── PATCH /orders/{id}/status  │
     │                                │                               │
```

### 4.2 관리자 대시보드 흐름

```
[Admin App]                       [Backend]
     │                                │
     │  1. POST /auth/login           │
     │──────────────────────────────▶│
     │  ◀── JWT Token                 │
     │                                │
     │  2. GET /dashboard             │
     │──────────────────────────────▶│
     │  ◀── DashboardResponse         │
     │                                │
     │  3. SSE /sse/stores/{id}/orders│
     │──────────────────────────────▶│
     │  ◀── SSE Stream (실시간)       │
     │                                │
     │  4. PATCH /orders/{id}/status  │
     │──────────────────────────────▶│
     │  ◀── OrderResponse             │
     │                                │
```

---

## 5. 인프라 컴포넌트 의존성

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI     │────▶│  SQLAlchemy  │────▶│  PostgreSQL  │
│   App         │     │  + Alembic   │     │  Database    │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├──▶ JWTMiddleware (관리자 API 보호)
       ├──▶ CORSMiddleware (프론트엔드 접근 허용)
       ├──▶ ErrorHandler (전역 에러 처리)
       ├──▶ SSEManager (인메모리 연결 풀)
       └──▶ StaticFiles (이미지 서빙)

┌──────────────┐     ┌──────────────┐
│ Customer App │────▶│              │
│ (React SPA)  │     │   FastAPI    │
└──────────────┘     │   Backend    │
                     │              │
┌──────────────┐     │              │
│  Admin App   │────▶│              │
│ (React SPA)  │     └──────────────┘
└──────────────┘
```

---

## 6. 순환 의존 방지 규칙

| 규칙 | 설명 |
|---|---|
| **단방향 의존** | Router → Service → Domain → Repository (역방향 금지) |
| **Service 간 호출 제한** | OrderService → SessionService만 허용 |
| **SSE 단방향** | 모든 Service → SSEService (SSEService는 다른 Service 호출 금지) |
| **Domain 독립** | Domain 컴포넌트 간 상호 의존 금지 |
| **Repository 독립** | Repository 컴포넌트 간 상호 의존 금지 |
