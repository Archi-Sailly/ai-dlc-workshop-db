# 테이블오더 서비스 - 컴포넌트 메서드 정의서

> **참고**: 이 문서는 메서드 시그니처와 고수준 목적을 정의합니다. 상세 비즈니스 로직은 Construction 단계의 Functional Design에서 정의됩니다.

---

## 1. Router Layer 메서드

### 1.1 CustomerRouter

```python
# 테이블 접근 및 메뉴 조회
GET  /api/stores/{store_id}/tables/{table_number}/validate
     → Response: TableValidationResponse
     # 매장/테이블 유효성 검증 (US-C01)

GET  /api/stores/{store_id}/menus
     → Query: category_id (optional)
     → Response: MenuListResponse
     # 카테고리별 메뉴 목록 조회 (US-C03)

GET  /api/stores/{store_id}/menus/{menu_id}
     → Response: MenuDetailResponse
     # 메뉴 상세 조회

GET  /api/stores/{store_id}/categories
     → Response: CategoryListResponse
     # 카테고리 목록 조회

# 주문
POST /api/stores/{store_id}/tables/{table_number}/orders
     → Body: CreateOrderRequest
     → Response: OrderResponse
     # 주문 생성 (US-C07)

GET  /api/stores/{store_id}/tables/{table_number}/orders
     → Query: session_id (optional)
     → Response: OrderListResponse
     # 현재 세션 주문 내역 조회 (US-C08)

# 세션
GET  /api/stores/{store_id}/tables/{table_number}/session
     → Response: SessionResponse
     # 현재 활성 세션 조회
```

### 1.2 AdminAuthRouter

```python
POST /api/admin/auth/login
     → Body: LoginRequest { store_identifier, username, password }
     → Response: LoginResponse { access_token, expires_at }
     # 관리자 로그인 (US-A01)

POST /api/admin/auth/verify
     → Header: Authorization: Bearer {token}
     → Response: TokenVerifyResponse
     # JWT 토큰 유효성 검증 (US-A02)
```

### 1.3 AdminOrderRouter

```python
GET  /api/admin/stores/{store_id}/dashboard
     → Response: DashboardResponse
     # 대시보드 데이터 조회 (US-A03)

GET  /api/admin/stores/{store_id}/tables/{table_number}/orders
     → Query: session_id (optional)
     → Response: OrderListResponse
     # 테이블별 주문 상세 조회 (US-A04)

PATCH /api/admin/stores/{store_id}/orders/{order_id}/status
      → Body: UpdateOrderStatusRequest { status }
      → Response: OrderResponse
      # 주문 상태 변경 (US-A05)

DELETE /api/admin/stores/{store_id}/orders/{order_id}
       → Response: DeleteResponse
       # 주문 삭제 - 대기중/접수 상태만 (US-A07)

GET  /api/admin/stores/{store_id}/orders/history
     → Query: table_number, date_from, date_to, page, size
     → Response: OrderHistoryResponse
     # 과거 주문 내역 조회 (US-A09)
```

### 1.4 AdminTableRouter

```python
POST /api/admin/stores/{store_id}/tables
     → Body: CreateTableRequest { table_number }
     → Response: TableResponse
     # 테이블 등록 (US-A06)

GET  /api/admin/stores/{store_id}/tables
     → Response: TableListResponse
     # 테이블 목록 조회

POST /api/admin/stores/{store_id}/tables/{table_number}/complete
     → Response: SessionCompleteResponse
     # 테이블 이용 완료 / 세션 종료 (US-A08)
```

### 1.5 AdminMenuRouter

```python
POST /api/admin/stores/{store_id}/menus
     → Body: CreateMenuRequest (multipart/form-data)
     → Response: MenuResponse
     # 메뉴 등록 (US-A10)

GET  /api/admin/stores/{store_id}/menus
     → Query: category_id (optional)
     → Response: MenuListResponse
     # 메뉴 목록 조회 (US-A11)

PUT  /api/admin/stores/{store_id}/menus/{menu_id}
     → Body: UpdateMenuRequest (multipart/form-data)
     → Response: MenuResponse
     # 메뉴 수정 (US-A12)

DELETE /api/admin/stores/{store_id}/menus/{menu_id}
       → Response: DeleteResponse
       # 메뉴 삭제 (US-A13)

PATCH /api/admin/stores/{store_id}/menus/reorder
      → Body: ReorderMenuRequest { menu_orders: [{menu_id, sort_order}] }
      → Response: SuccessResponse
      # 메뉴 노출 순서 조정 (US-A14)

POST /api/admin/stores/{store_id}/categories
     → Body: CreateCategoryRequest { name, sort_order }
     → Response: CategoryResponse
     # 카테고리 등록

GET  /api/admin/stores/{store_id}/categories
     → Response: CategoryListResponse
     # 카테고리 목록 조회
```

### 1.6 SSERouter

```python
GET /api/sse/stores/{store_id}/tables/{table_number}/orders
    → Response: text/event-stream
    # 고객용 SSE - 테이블 단위 주문 상태 업데이트 (US-C09)

GET /api/sse/stores/{store_id}/orders
    → Header: Authorization: Bearer {token}
    → Response: text/event-stream
    # 관리자용 SSE - 매장 전체 주문 업데이트 (US-A03)
```

---

## 2. Service Layer 메서드

### 2.1 OrderService

```python
class OrderService:
    async def create_order(store_id, table_number, items) → Order
        # 주문 생성 + 세션 자동 생성/귀속 + SSE 이벤트 발행

    async def get_orders_by_session(store_id, table_number, session_id) → list[Order]
        # 세션별 주문 목록 조회

    async def update_order_status(store_id, order_id, new_status) → Order
        # 주문 상태 변경 + SSE 이벤트 발행

    async def delete_order(store_id, order_id) → bool
        # 주문 삭제 (상태 제한 적용) + SSE 이벤트 발행

    async def get_dashboard_data(store_id) → DashboardData
        # 대시보드용 테이블별 주문 현황 집계

    async def get_order_history(store_id, filters) → PaginatedOrders
        # 과거 주문 내역 조회 (필터링, 페이지네이션)
```

### 2.2 MenuService

```python
class MenuService:
    async def get_menus(store_id, category_id=None) → list[Menu]
        # 메뉴 목록 조회 (카테고리 필터링, 정렬 순서 적용)

    async def get_menu_detail(store_id, menu_id) → Menu
        # 메뉴 상세 조회

    async def create_menu(store_id, menu_data, image_file=None) → Menu
        # 메뉴 등록 + 이미지 업로드

    async def update_menu(store_id, menu_id, menu_data, image_file=None) → Menu
        # 메뉴 수정 + 이미지 교체

    async def delete_menu(store_id, menu_id) → bool
        # 메뉴 삭제 + 이미지 파일 삭제

    async def reorder_menus(store_id, menu_orders) → bool
        # 메뉴 노출 순서 일괄 변경

    async def get_categories(store_id) → list[Category]
        # 카테고리 목록 조회

    async def create_category(store_id, category_data) → Category
        # 카테고리 등록
```

### 2.3 TableService

```python
class TableService:
    async def validate_table(store_id, table_number) → TableValidation
        # 매장/테이블 유효성 검증

    async def create_table(store_id, table_number) → Table
        # 테이블 등록 (중복 체크 포함)

    async def get_tables(store_id) → list[Table]
        # 매장 테이블 목록 조회

    async def get_table_url(store_id, table_number) → str
        # 테이블 접속 URL 생성
```

### 2.4 SessionService

```python
class SessionService:
    async def get_or_create_session(store_id, table_number) → Session
        # 활성 세션 조회 또는 새 세션 생성

    async def get_active_session(store_id, table_number) → Session | None
        # 현재 활성 세션 조회

    async def complete_session(store_id, table_number) → Session
        # 세션 종료 (이용 완료) + 주문 내역 아카이브
```

### 2.5 AuthService

```python
class AuthService:
    async def login(store_identifier, username, password) → TokenPair
        # 관리자 로그인 + JWT 발급

    async def verify_token(token) → AdminUser
        # JWT 토큰 검증

    async def check_login_attempts(store_id, username) → bool
        # 로그인 시도 제한 확인
```

### 2.6 SSEService

```python
class SSEService:
    async def subscribe_table(store_id, table_number) → AsyncGenerator
        # 고객용 테이블 단위 SSE 구독

    async def subscribe_store(store_id) → AsyncGenerator
        # 관리자용 매장 단위 SSE 구독

    async def publish_event(store_id, table_number, event_type, data) → None
        # SSE 이벤트 발행 (구독자에게 전달)

    async def disconnect(connection_id) → None
        # SSE 연결 해제
```

### 2.7 FileService

```python
class FileService:
    async def upload_image(file, store_id) → str
        # 이미지 파일 저장, 파일 경로 반환

    async def delete_image(file_path) → bool
        # 이미지 파일 삭제

    def get_image_url(file_path) → str
        # 이미지 서빙 URL 생성
```

---

## 3. Domain Layer 메서드

### 3.1 OrderDomain

```python
class OrderDomain:
    def validate_status_transition(current_status, new_status) → bool
        # 주문 상태 전이 유효성 검증 (PENDING→ACCEPTED→PREPARING→COMPLETED)

    def can_delete(order_status) → bool
        # 삭제 가능 여부 판단 (PENDING, ACCEPTED만 가능)

    def calculate_order_total(items) → Decimal
        # 주문 총액 계산
```

### 3.2 SessionDomain

```python
class SessionDomain:
    def should_create_new_session(active_session) → bool
        # 새 세션 생성 필요 여부 판단

    def can_complete_session(session) → bool
        # 세션 종료 가능 여부 판단
```

### 3.3 MenuDomain

```python
class MenuDomain:
    def validate_menu_data(menu_data) → ValidationResult
        # 메뉴 데이터 유효성 검증 (필수 필드, 가격 양수)

    def validate_image_file(file) → ValidationResult
        # 이미지 파일 유효성 검증 (타입, 크기)
```

### 3.4 AuthDomain

```python
class AuthDomain:
    def hash_password(password) → str
        # bcrypt 비밀번호 해싱

    def verify_password(plain, hashed) → bool
        # 비밀번호 검증

    def is_login_blocked(attempts, max_attempts) → bool
        # 로그인 차단 여부 판단

    def create_jwt_token(admin_user, expires_hours=16) → str
        # JWT 토큰 생성

    def decode_jwt_token(token) → TokenPayload
        # JWT 토큰 디코딩/검증
```

### 3.5 TableDomain

```python
class TableDomain:
    def validate_table_number(table_number) → bool
        # 테이블 번호 유효성 검증

    def generate_table_url(store_id, table_number) → str
        # 테이블 접속 URL 생성
```

---

## 4. Repository Layer 메서드

### 4.1 OrderRepository

```python
class OrderRepository:
    async def create(order_data) → Order
    async def get_by_id(order_id) → Order | None
    async def get_by_session(session_id) → list[Order]
    async def get_by_store_and_table(store_id, table_number) → list[Order]
    async def update_status(order_id, status) → Order
    async def delete(order_id) → bool
    async def get_history(store_id, filters) → PaginatedResult[Order]
    async def get_active_orders_by_store(store_id) → list[Order]
```

### 4.2 MenuRepository

```python
class MenuRepository:
    async def create(menu_data) → Menu
    async def get_by_id(menu_id) → Menu | None
    async def get_by_store(store_id, category_id=None) → list[Menu]
    async def update(menu_id, menu_data) → Menu
    async def delete(menu_id) → bool
    async def update_sort_orders(menu_orders) → bool
```

### 4.3 TableRepository

```python
class TableRepository:
    async def create(table_data) → Table
    async def get_by_store_and_number(store_id, table_number) → Table | None
    async def get_by_store(store_id) → list[Table]
    async def exists(store_id, table_number) → bool
```

### 4.4 SessionRepository

```python
class SessionRepository:
    async def create(session_data) → Session
    async def get_active(store_id, table_number) → Session | None
    async def complete(session_id) → Session
    async def get_by_id(session_id) → Session | None
```

### 4.5 StoreRepository

```python
class StoreRepository:
    async def get_by_id(store_id) → Store | None
    async def get_by_identifier(identifier) → Store | None
    async def exists(store_id) → bool
```

### 4.6 AdminUserRepository

```python
class AdminUserRepository:
    async def get_by_username(store_id, username) → AdminUser | None
    async def record_login_attempt(store_id, username, success) → None
    async def get_recent_attempts(store_id, username, minutes=30) → int
```

---

## 5. 프론트엔드 주요 인터페이스

### 5.1 Customer App — Zustand 스토어

```typescript
// cartStore
interface CartStore {
  items: CartItem[];
  addItem(menu: Menu): void;
  removeItem(menuId: string): void;
  updateQuantity(menuId: string, quantity: number): void;
  clearCart(): void;
  getTotalPrice(): number;
  getTotalItems(): number;
}

// orderStore
interface OrderStore {
  orders: Order[];
  isLoading: boolean;
  fetchOrders(storeId: string, tableNumber: string): Promise<void>;
  updateOrderStatus(orderId: string, status: OrderStatus): void;
}

// tableStore
interface TableStore {
  storeId: string | null;
  tableNumber: string | null;
  sessionId: string | null;
  setTableContext(storeId: string, tableNumber: string): void;
  setSessionId(sessionId: string): void;
}
```

### 5.2 Admin App — Zustand 스토어

```typescript
// authStore
interface AuthStore {
  token: string | null;
  user: AdminUser | null;
  isAuthenticated: boolean;
  login(credentials: LoginRequest): Promise<void>;
  logout(): void;
  checkTokenExpiry(): void;
}

// dashboardStore
interface DashboardStore {
  tables: TableWithOrders[];
  isLoading: boolean;
  fetchDashboard(storeId: string): Promise<void>;
  updateTableOrders(tableNumber: string, orders: Order[]): void;
  addNewOrder(tableNumber: string, order: Order): void;
}
```
