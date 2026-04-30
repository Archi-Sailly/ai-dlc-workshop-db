# 테이블오더 서비스 - Unit of Work 의존성 매트릭스

---

## 1. 유닛 간 의존성 매트릭스

| 유닛 (행 → 열에 의존) | U1 DB | U2 Auth | U3 Menu | U4 Table/Session | U5 Order | U6 SSE | U7 Customer | U8 Admin |
|---|---|---|---|---|---|---|---|---|
| **U1 Database Schema** | — | | | | | | | |
| **U2 Auth Service** | ✅ | — | | | | | | |
| **U3 Menu Service** | ✅ | | — | | | | | |
| **U4 Table & Session** | ✅ | | | — | | | | |
| **U5 Order Service** | ✅ | | | ✅ | — | ✅ | | |
| **U6 SSE Service** | | | | | | — | | |
| **U7 Customer App** | | | ✅ | ✅ | ✅ | ✅ | — | |
| **U8 Admin App** | | ✅ | ✅ | ✅ | ✅ | ✅ | | — |

### 의존성 설명

| 의존 관계 | 유형 | 설명 |
|---|---|---|
| U2 → U1 | 데이터 | admin_users, login_attempts 테이블 사용 |
| U3 → U1 | 데이터 | menus, categories 테이블 사용 |
| U4 → U1 | 데이터 | tables, sessions, stores 테이블 사용 |
| U5 → U1 | 데이터 | orders, order_items 테이블 사용 |
| U5 → U4 | 서비스 | 주문 생성 시 세션 조회/생성 API 호출 |
| U5 → U6 | 서비스 | 주문 이벤트 발행 (HTTP POST) |
| U7 → U3 | API | 메뉴 조회 API 호출 |
| U7 → U4 | API | 테이블 유효성 검증, 세션 조회 API 호출 |
| U7 → U5 | API | 주문 생성, 주문 내역 조회 API 호출 |
| U7 → U6 | SSE | 주문 상태 실시간 업데이트 구독 |
| U8 → U2 | API | 로그인, 토큰 검증 API 호출 |
| U8 → U3 | API | 메뉴 CRUD API 호출 |
| U8 → U4 | API | 테이블 관리, 세션 종료 API 호출 |
| U8 → U5 | API | 주문 관리, 대시보드, 상태 변경 API 호출 |
| U8 → U6 | SSE | 실시간 주문 대시보드 구독 |

---

## 2. 개발 순서 및 선행 조건

### 단계별 개발 계획

```
┌─────────────────────────────────────────────────────────┐
│ 단계 1: 기반 인프라                                       │
│                                                          │
│  ┌──────────────────────┐                                │
│  │  U1: Database Schema  │                                │
│  │  선행 조건: 없음       │                                │
│  └──────────┬───────────┘                                │
└─────────────┼───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│ 단계 2: 핵심 도메인 서비스 (병렬)                          │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │
│  │ U2: Auth    │  │ U3: Menu   │  │ U4: Table/Session│   │
│  │ 선행: U1    │  │ 선행: U1   │  │ 선행: U1         │   │
│  └────────────┘  └────────────┘  └──────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 단계 3: 통합 서비스 (병렬)                                │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ U5: Order         │  │ U6: SSE          │             │
│  │ 선행: U1, U4      │  │ 선행: 없음 (독립) │             │
│  └──────────────────┘  └──────────────────┘             │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 단계 4: 프론트엔드 (병렬)                                 │
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ U7: Customer App  │  │ U8: Admin App    │             │
│  │ 선행: U3,U4,U5,U6 │  │ 선행: U2~U6 전체 │             │
│  └──────────────────┘  └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 선행 조건 상세

| 유닛 | 선행 유닛 | 이유 |
|---|---|---|
| U1 | 없음 | 기반 인프라, 최우선 개발 |
| U2 | U1 | admin_users, login_attempts 테이블 필요 |
| U3 | U1 | menus, categories 테이블 필요 |
| U4 | U1 | tables, sessions, stores 테이블 필요 |
| U5 | U1, U4 | orders 테이블 + 세션 서비스 API 필요 |
| U6 | 없음 | 독립 인프라 (인메모리 연결 관리), 단 U5와 통합 테스트 시 U5 필요 |
| U7 | U3, U4, U5, U6 | 메뉴/테이블/주문/SSE API 모두 필요 |
| U8 | U2, U3, U4, U5, U6 | 인증 포함 모든 백엔드 API 필요 |

---

## 3. 통합 포인트

### 3.1 서비스 간 내부 통신

| 호출자 | 대상 | 엔드포인트 | 방식 | 용도 |
|---|---|---|---|---|
| U5 (Order) | U4 (Table/Session) | `GET /internal/sessions/active` | HTTP REST | 주문 생성 시 활성 세션 조회 |
| U5 (Order) | U4 (Table/Session) | `POST /internal/sessions` | HTTP REST | 첫 주문 시 세션 자동 생성 |
| U5 (Order) | U6 (SSE) | `POST /internal/events` | HTTP REST | 주문 이벤트 발행 |
| U4 (Table/Session) | U6 (SSE) | `POST /internal/events` | HTTP REST | 세션 종료 이벤트 발행 |

### 3.2 프론트엔드 → 백엔드 통신

| 프론트엔드 | 백엔드 서비스 | 프로토콜 | 인증 |
|---|---|---|---|
| U7 (Customer) | U3 (Menu) | HTTP REST | 없음 |
| U7 (Customer) | U4 (Table/Session) | HTTP REST | 없음 |
| U7 (Customer) | U5 (Order) | HTTP REST | 없음 |
| U7 (Customer) | U6 (SSE) | SSE | 없음 |
| U8 (Admin) | U2 (Auth) | HTTP REST | 없음 (로그인) |
| U8 (Admin) | U3 (Menu) | HTTP REST | JWT |
| U8 (Admin) | U4 (Table/Session) | HTTP REST | JWT |
| U8 (Admin) | U5 (Order) | HTTP REST | JWT |
| U8 (Admin) | U6 (SSE) | SSE | JWT |

### 3.3 API Gateway 고려사항
- MVP 단계에서는 각 서비스가 개별 포트로 실행
- 프론트엔드에서 서비스별 base URL 설정으로 라우팅
- 향후 API Gateway (nginx 등) 도입 가능

---

## 4. 공유 리소스

| 리소스 | 공유 범위 | 위치 |
|---|---|---|
| PostgreSQL DB | U1~U5 (모든 백엔드) | 단일 DB 인스턴스 |
| SQLAlchemy 모델 | U2~U5 | `database/models/` (공유 참조) |
| JWT 검증 유틸 | U2 (발급), U3~U5 (검증) | `shared/jwt_utils.py` |
| DB 연결 설정 | U2~U5 | `shared/db_config.py` |
| 공유 스키마 | U5↔U4, U5↔U6 | `shared/schemas/` |

---

## 5. 순환 의존 검증

```
U1 → (없음)
U2 → U1
U3 → U1
U4 → U1
U5 → U1, U4, U6
U6 → (없음)
U7 → U3, U4, U5, U6
U8 → U2, U3, U4, U5, U6
```

**결과**: 순환 의존 없음 ✅
- 모든 의존성이 단방향
- U5 → U4 (세션 조회), U5 → U6 (이벤트 발행) 모두 단방향
- U4 → U6 (세션 종료 이벤트) 단방향
