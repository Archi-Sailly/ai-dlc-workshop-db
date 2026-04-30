# 테이블오더 서비스 - 컴포넌트 정의서

## 설계 결정사항 요약

| 항목 | 결정 |
|---|---|
| 배포 모델 | 모놀리스 (Backend 1개 + Frontend 2개 = 3개 배포 단위) |
| 백엔드 아키텍처 | 4-Layer (Router → Service → Domain → Repository) |
| 프론트엔드 구성 | 별도 React 앱 2개 (Customer + Admin) |
| 상태 관리 | Zustand |
| SSE 구조 | 테이블 단위 (table-level) |
| DB 마이그레이션 | Alembic (SQLAlchemy 기반) |
| ORM | SQLAlchemy ORM |
| 이미지 업로드 | FastAPI 내장 UploadFile |

---

## 1. 백엔드 컴포넌트 (Python + FastAPI)

### 1.1 Router Layer (API 엔드포인트)

| 컴포넌트 | 책임 | 관련 스토리 |
|---|---|---|
| **CustomerRouter** | 고객용 API 엔드포인트 (메뉴 조회, 주문 생성, 주문 내역) | US-C01, C03, C07, C08 |
| **AdminAuthRouter** | 관리자 인증 API (로그인, 토큰 갱신) | US-A01, A02 |
| **AdminOrderRouter** | 관리자 주문 관리 API (대시보드, 상태 변경, 삭제) | US-A03, A04, A05, A07, A09 |
| **AdminTableRouter** | 관리자 테이블 관리 API (등록, 세션 종료) | US-A06, A08 |
| **AdminMenuRouter** | 관리자 메뉴 관리 API (CRUD, 순서 조정) | US-A10, A11, A12, A13, A14 |
| **SSERouter** | SSE 스트림 엔드포인트 (고객용 + 관리자용) | US-C09, A03 |

### 1.2 Service Layer (비즈니스 오케스트레이션)

| 컴포넌트 | 책임 | 관련 스토리 |
|---|---|---|
| **OrderService** | 주문 생성, 상태 변경, 삭제 오케스트레이션 | US-C07, A05, A07 |
| **MenuService** | 메뉴 CRUD, 카테고리 관리, 순서 조정 | US-C03, A10~A14 |
| **TableService** | 테이블 등록, 유효성 검증, URL 생성 | US-C01, A06 |
| **SessionService** | 세션 생성, 조회, 종료 라이프사이클 관리 | US-C07, C08, A08 |
| **AuthService** | 관리자 인증, JWT 발급/검증, 로그인 제한 | US-A01, A02 |
| **SSEService** | SSE 연결 관리, 이벤트 발행, 구독자 관리 | US-C09, A03 |
| **FileService** | 이미지 업로드, 저장, 서빙 | US-A10, A12 |

### 1.3 Domain Layer (도메인 모델 및 비즈니스 규칙)

| 컴포넌트 | 책임 | 관련 스토리 |
|---|---|---|
| **OrderDomain** | 주문 상태 흐름 규칙, 삭제 가능 여부 판단 | US-A05, A07 |
| **SessionDomain** | 세션 라이프사이클 규칙, 세션 자동 생성 로직 | US-C07, A08 |
| **MenuDomain** | 메뉴 유효성 검증, 가격 규칙 | US-A10, A12 |
| **AuthDomain** | 인증 규칙, 로그인 시도 제한 로직 | US-A01 |
| **TableDomain** | 테이블 유효성 검증, 중복 체크 | US-A06 |

### 1.4 Repository Layer (데이터 접근)

| 컴포넌트 | 책임 |
|---|---|
| **OrderRepository** | 주문 CRUD, 상태별 조회, 세션별 조회 |
| **MenuRepository** | 메뉴 CRUD, 카테고리별 조회, 순서 관리 |
| **TableRepository** | 테이블 CRUD, 매장별 조회 |
| **SessionRepository** | 세션 CRUD, 활성 세션 조회 |
| **StoreRepository** | 매장 정보 조회 |
| **AdminUserRepository** | 관리자 계정 CRUD, 로그인 시도 기록 |

### 1.5 인프라/공통 컴포넌트

| 컴포넌트 | 책임 |
|---|---|
| **Database** | SQLAlchemy 엔진, 세션 팩토리, 커넥션 풀 관리 |
| **AlembicMigration** | DB 스키마 마이그레이션 관리 |
| **JWTMiddleware** | JWT 토큰 검증 미들웨어 |
| **CORSMiddleware** | CORS 설정 (프론트엔드 ↔ 백엔드) |
| **ErrorHandler** | 전역 에러 핸들링, 사용자 친화적 에러 응답 |
| **SSEManager** | SSE 연결 풀 관리, 이벤트 브로드캐스트 |

---

## 2. 프론트엔드 컴포넌트 — Customer App (React + TypeScript)

### 2.1 페이지 컴포넌트

| 컴포넌트 | 책임 | 관련 스토리 |
|---|---|---|
| **MenuPage** | 카테고리별 메뉴 조회 메인 화면 | US-C03 |
| **CartPage** | 장바구니 관리 (수량 조절, 삭제) | US-C04, C05 |
| **OrderConfirmPage** | 주문 최종 확인 및 확정 | US-C07 |
| **OrderHistoryPage** | 현재 세션 주문 내역 조회 | US-C08 |
| **OrderSuccessPage** | 주문 성공 안내 (5초 후 리다이렉트) | US-C07 |
| **ErrorPage** | 유효하지 않은 매장/테이블 에러 | US-C01 |

### 2.2 공통 컴포넌트

| 컴포넌트 | 책임 |
|---|---|
| **MenuCard** | 메뉴 카드 UI (이름, 가격, 설명, 이미지, 추가 버튼) |
| **CategoryTab** | 카테고리 탭/사이드바 네비게이션 |
| **CartBadge** | 장바구니 아이템 수 배지 |
| **CartItem** | 장바구니 개별 아이템 (수량 조절, 삭제) |
| **OrderStatusBadge** | 주문 상태 표시 배지 (색상 구분) |
| **BottomNav** | 하단 네비게이션 바 (메뉴, 장바구니, 주문내역) |
| **LoadingSpinner** | 로딩 인디케이터 |
| **ErrorMessage** | 에러 메시지 표시 |
| **ConfirmDialog** | 확인 팝업 다이얼로그 |

### 2.3 커스텀 훅

| 훅 | 책임 |
|---|---|
| **useCart** | 장바구니 상태 관리 (localStorage 연동) |
| **useTableContext** | 매장 ID, 테이블 번호 컨텍스트 관리 |
| **useSSE** | SSE 연결 관리, 자동 재연결 |
| **useOrders** | 주문 목록 조회 및 실시간 업데이트 |

### 2.4 상태 스토어 (Zustand)

| 스토어 | 책임 |
|---|---|
| **cartStore** | 장바구니 상태 (localStorage 영속화) |
| **orderStore** | 주문 목록, 실시간 상태 업데이트 |
| **tableStore** | 매장/테이블 컨텍스트 |

---

## 3. 프론트엔드 컴포넌트 — Admin App (React + TypeScript)

### 3.1 페이지 컴포넌트

| 컴포넌트 | 책임 | 관련 스토리 |
|---|---|---|
| **LoginPage** | 관리자 로그인 화면 | US-A01 |
| **DashboardPage** | 실시간 주문 대시보드 (테이블 그리드) | US-A03 |
| **TableDetailPage** | 테이블별 주문 상세 보기 | US-A04 |
| **TableManagePage** | 테이블 등록/관리 | US-A06 |
| **MenuManagePage** | 메뉴 CRUD 관리 | US-A10, A11 |
| **MenuFormPage** | 메뉴 등록/수정 폼 | US-A10, A12 |
| **OrderHistoryPage** | 과거 주문 내역 조회 | US-A09 |

### 3.2 공통 컴포넌트

| 컴포넌트 | 책임 |
|---|---|
| **TableCard** | 대시보드 테이블 카드 (번호, 총액, 최신 주문, 강조 표시) |
| **OrderItem** | 주문 아이템 (상태 변경 버튼 포함) |
| **OrderStatusButton** | 주문 상태 변경 버튼 (다음 단계) |
| **MenuListItem** | 메뉴 목록 아이템 (수정/삭제 버튼) |
| **ImageUploader** | 이미지 업로드 컴포넌트 |
| **DateFilter** | 날짜 필터링 컴포넌트 |
| **TableFilter** | 테이블별 필터링 컴포넌트 |
| **SideNav** | 사이드 네비게이션 (대시보드, 테이블, 메뉴, 이력) |
| **ConfirmDialog** | 확인 팝업 (삭제, 이용 완료 등) |
| **Toast** | 성공/실패 피드백 토스트 |

### 3.3 커스텀 훅

| 훅 | 책임 |
|---|---|
| **useAuth** | 인증 상태 관리, JWT 토큰 관리, 자동 로그아웃 |
| **useSSE** | SSE 연결 관리 (매장 단위), 자동 재연결 |
| **useDashboard** | 대시보드 데이터 관리, 실시간 업데이트 |
| **useOrders** | 주문 CRUD, 상태 변경 |
| **useMenus** | 메뉴 CRUD |
| **useTables** | 테이블 관리 |

### 3.4 상태 스토어 (Zustand)

| 스토어 | 책임 |
|---|---|
| **authStore** | 인증 상태, JWT 토큰, 만료 관리 |
| **dashboardStore** | 대시보드 테이블/주문 실시간 상태 |
| **menuStore** | 메뉴 목록 상태 |
| **tableStore** | 테이블 목록 상태 |

---

## 4. 컴포넌트 수 요약

| 영역 | 컴포넌트 수 |
|---|---|
| 백엔드 Router | 6 |
| 백엔드 Service | 7 |
| 백엔드 Domain | 5 |
| 백엔드 Repository | 6 |
| 백엔드 인프라/공통 | 6 |
| Customer App 페이지 | 6 |
| Customer App 공통 | 9 |
| Customer App 훅/스토어 | 7 |
| Admin App 페이지 | 7 |
| Admin App 공통 | 10 |
| Admin App 훅/스토어 | 10 |
| **합계** | **79** |
