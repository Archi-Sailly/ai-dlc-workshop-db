# 테이블오더 서비스 - Application Design 통합 문서

---

## 1. 설계 결정사항

| 항목 | 결정 | 근거 |
|---|---|---|
| 백엔드 아키텍처 | 4-Layer (Router → Service → Domain → Repository) | 도메인 로직 분리, 확장성 우수 |
| 프론트엔드 구성 | 별도 React 앱 2개 (Customer + Admin) | 독립 배포, 관심사 완전 분리 |
| 상태 관리 | Zustand | 경량, SSE 실시간 상태 관리에 적합 |
| SSE 구조 | 테이블 단위 (table-level) | 테이블별 개별 스트림, 서버 부하 분산 |
| DB 마이그레이션 | Alembic (SQLAlchemy 기반) | Python 생태계 표준, 자동 마이그레이션 |
| ORM | SQLAlchemy ORM | 모델 정의, 관계 매핑, 쿼리 빌더 |
| 이미지 업로드 | FastAPI 내장 UploadFile | 단순, 별도 설정 불필요 |

---

## 2. 시스템 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                                  │
│                                                                      │
│  ┌─────────────────────┐          ┌─────────────────────┐           │
│  │   Customer App       │          │    Admin App         │           │
│  │   (React + TS)       │          │    (React + TS)      │           │
│  │   Zustand            │          │    Zustand           │           │
│  │   7~10" 태블릿 중심   │          │    데스크톱/태블릿    │           │
│  └──────────┬──────────┘          └──────────┬──────────┘           │
│             │ HTTP + SSE                      │ HTTP + SSE + JWT     │
└─────────────┼─────────────────────────────────┼─────────────────────┘
              │                                 │
              ▼                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SERVER TIER                                   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                         │  │
│  │                                                               │  │
│  │  ┌─── Router Layer ──────────────────────────────────────┐   │  │
│  │  │ CustomerRouter │ AdminAuthRouter │ AdminOrderRouter    │   │  │
│  │  │ AdminTableRouter │ AdminMenuRouter │ SSERouter         │   │  │
│  │  └───────────────────────────┬───────────────────────────┘   │  │
│  │                              │                                │  │
│  │  ┌─── Middleware ────────────┤                                │  │
│  │  │ JWTMiddleware │ CORS │ ErrorHandler                       │  │
│  │  └───────────────────────────┤                                │  │
│  │                              │                                │  │
│  │  ┌─── Service Layer ─────────┴───────────────────────────┐   │  │
│  │  │ OrderService │ MenuService │ TableService              │   │  │
│  │  │ SessionService │ AuthService │ SSEService │ FileService│   │  │
│  │  └───────────────────────────┬───────────────────────────┘   │  │
│  │                              │                                │  │
│  │  ┌─── Domain Layer ──────────┴───────────────────────────┐   │  │
│  │  │ OrderDomain │ SessionDomain │ MenuDomain               │   │  │
│  │  │ AuthDomain │ TableDomain                               │   │  │
│  │  └───────────────────────────┬───────────────────────────┘   │  │
│  │                              │                                │  │
│  │  ┌─── Repository Layer ──────┴───────────────────────────┐   │  │
│  │  │ OrderRepo │ MenuRepo │ TableRepo │ SessionRepo         │   │  │
│  │  │ StoreRepo │ AdminUserRepo                              │   │  │
│  │  └───────────────────────────┬───────────────────────────┘   │  │
│  │                              │                                │  │
│  └──────────────────────────────┼────────────────────────────────┘  │
│                                 │                                    │
└─────────────────────────────────┼────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA TIER                                    │
│                                                                      │
│  ┌─────────────────────┐          ┌─────────────────────┐           │
│  │   PostgreSQL         │          │   Local File System  │           │
│  │   (SQLAlchemy ORM)   │          │   (메뉴 이미지)      │           │
│  │   (Alembic 마이그레이션)│          │   uploads/stores/   │           │
│  └─────────────────────┘          └─────────────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 컴포넌트 요약

### 3.1 백엔드 (30개 컴포넌트)

| 레이어 | 컴포넌트 | 수 |
|---|---|---|
| Router | CustomerRouter, AdminAuthRouter, AdminOrderRouter, AdminTableRouter, AdminMenuRouter, SSERouter | 6 |
| Service | OrderService, MenuService, TableService, SessionService, AuthService, SSEService, FileService | 7 |
| Domain | OrderDomain, SessionDomain, MenuDomain, AuthDomain, TableDomain | 5 |
| Repository | OrderRepository, MenuRepository, TableRepository, SessionRepository, StoreRepository, AdminUserRepository | 6 |
| 인프라/공통 | Database, AlembicMigration, JWTMiddleware, CORSMiddleware, ErrorHandler, SSEManager | 6 |

### 3.2 Customer App (22개 컴포넌트)

| 유형 | 컴포넌트 | 수 |
|---|---|---|
| 페이지 | MenuPage, CartPage, OrderConfirmPage, OrderHistoryPage, OrderSuccessPage, ErrorPage | 6 |
| 공통 UI | MenuCard, CategoryTab, CartBadge, CartItem, OrderStatusBadge, BottomNav, LoadingSpinner, ErrorMessage, ConfirmDialog | 9 |
| 훅 | useCart, useTableContext, useSSE, useOrders | 4 |
| 스토어 | cartStore, orderStore, tableStore | 3 |

### 3.3 Admin App (27개 컴포넌트)

| 유형 | 컴포넌트 | 수 |
|---|---|---|
| 페이지 | LoginPage, DashboardPage, TableDetailPage, TableManagePage, MenuManagePage, MenuFormPage, OrderHistoryPage | 7 |
| 공통 UI | TableCard, OrderItem, OrderStatusButton, MenuListItem, ImageUploader, DateFilter, TableFilter, SideNav, ConfirmDialog, Toast | 10 |
| 훅 | useAuth, useSSE, useDashboard, useOrders, useMenus, useTables | 6 |
| 스토어 | authStore, dashboardStore, menuStore, tableStore | 4 |

**총 79개 컴포넌트**

---

## 4. 핵심 서비스 오케스트레이션

### 4.1 주문 생성 흐름
```
CustomerRouter.create_order()
  → OrderService.create_order()
    → SessionService.get_or_create_session()  // 세션 자동 생성/귀속
    → OrderDomain.calculate_order_total()     // 총액 계산
    → OrderRepository.create()                // DB 저장
    → [트랜잭션 커밋]
    → SSEService.publish_event("order_created")  // 실시간 알림
```

### 4.2 주문 상태 변경 흐름
```
AdminOrderRouter.update_status()
  → OrderService.update_order_status()
    → OrderRepository.get_by_id()                    // 주문 조회
    → OrderDomain.validate_status_transition()        // 상태 전이 검증
    → OrderRepository.update_status()                 // DB 업데이트
    → [트랜잭션 커밋]
    → SSEService.publish_event("order_status_changed") // 실시간 알림
```

### 4.3 세션 종료 흐름
```
AdminTableRouter.complete_session()
  → SessionService.complete_session()
    → SessionRepository.get_active()           // 활성 세션 조회
    → SessionDomain.can_complete_session()     // 종료 가능 여부
    → SessionRepository.complete()             // 세션 종료
    → [트랜잭션 커밋]
    → SSEService.publish_event("session_completed") // 실시간 알림
```

---

## 5. SSE 통신 설계

### 5.1 구독 구조

| 구독 유형 | 엔드포인트 | 대상 | 이벤트 |
|---|---|---|---|
| 테이블 단위 | `/sse/stores/{store_id}/tables/{table_number}/orders` | 고객 | 해당 테이블 주문 이벤트 |
| 매장 단위 | `/sse/stores/{store_id}/orders` | 관리자 | 매장 전체 주문 이벤트 |

### 5.2 이벤트 타입

| 이벤트 | 발생 시점 | 데이터 |
|---|---|---|
| `order_created` | 고객 주문 생성 | 주문 전체 정보 |
| `order_status_changed` | 관리자 상태 변경 | 주문 ID + 새 상태 |
| `order_deleted` | 관리자 주문 삭제 | 주문 ID |
| `session_completed` | 관리자 이용 완료 | 세션 ID + 테이블 번호 |

### 5.3 연결 관리
- 인메모리 연결 풀 (SSEManager)
- 연결 끊김 시 클라이언트 자동 재연결 (EventSource 기본 동작)
- 하트비트: 30초 간격 ping 이벤트
- 2초 이내 이벤트 전달 목표

---

## 6. 멀티테넌시 설계

### 6.1 데이터 격리 방식
- **Shared Database, Shared Schema** 방식
- 모든 테이블에 `store_id` 컬럼으로 매장별 데이터 격리
- 모든 API 요청에 `store_id` 포함 (URL 경로 파라미터)

### 6.2 접근 제어
- 고객: URL의 `store_id` + `table_number`로 매장/테이블 식별
- 관리자: JWT 토큰에 `store_id` 포함, 자신의 매장 데이터만 접근

---

## 7. 인증/보안 설계

### 7.1 고객 접근
- 인증 없음 (URL 기반 매장/테이블 식별)
- URL: `/store/{store_id}/table/{table_number}`
- 유효하지 않은 조합 시 에러 페이지

### 7.2 관리자 인증
- JWT 토큰 기반 (16시간 만료)
- bcrypt 비밀번호 해싱
- 로그인 시도 제한 (30분 내 연속 실패 시 차단)
- JWTMiddleware로 관리자 API 보호

---

## 8. 유저 스토리 매핑

| 컴포넌트 영역 | 커버하는 스토리 |
|---|---|
| CustomerRouter + Customer App | US-C01, C03, C04, C05, C06, C07, C08, C09 |
| AdminAuthRouter + LoginPage | US-A01, A02 |
| AdminOrderRouter + DashboardPage | US-A03, A04, A05, A07, A09 |
| AdminTableRouter + TableManagePage | US-A06, A08 |
| AdminMenuRouter + MenuManagePage | US-A10, A11, A12, A13, A14 |
| SSEService + SSERouter | US-C09, A03 (실시간 부분) |

**전체 22개 스토리 100% 커버**

---

## 9. 상세 문서 참조

| 문서 | 경로 | 내용 |
|---|---|---|
| 컴포넌트 정의서 | `components.md` | 컴포넌트 목록, 책임, 관련 스토리 |
| 메서드 정의서 | `component-methods.md` | API 엔드포인트, 메서드 시그니처, 입출력 타입 |
| 서비스 설계서 | `services.md` | 서비스 오케스트레이션, 트랜잭션 경계, 호출 규칙 |
| 의존성 설계서 | `component-dependency.md` | 의존성 매트릭스, 통신 패턴, 데이터 흐름 |
