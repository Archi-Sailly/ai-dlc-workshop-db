# 테이블오더 서비스 - Unit of Work 정의서

## 설계 결정사항

| 항목 | 결정 |
|---|---|
| 배포 모델 | 모놀리스 (Backend 1개 + Frontend 2개 = 3개 배포 단위) |
| 개발 순서 | 데이터 모델 우선 (DB 스키마 → API → UI) |
| 백엔드 모듈 분리 | 도메인 기준 (주문, 메뉴, 테이블/세션, 인증, SSE) — 논리적 모듈 |

---

## 유닛 목록 요약

| # | 유닛 | 유형 | 기술 스택 | 스토리 수 |
|---|---|---|---|---|
| U1 | Database Schema | 데이터 모델 | PostgreSQL + Alembic | — (기반) |
| U2 | Backend API | 모놀리스 백엔드 | FastAPI + SQLAlchemy + JWT + SSE | 22 (전체) |
| U3 | Customer App | 프론트엔드 | React + TypeScript + Zustand | 8 |
| U4 | Admin App | 프론트엔드 | React + TypeScript + Zustand | 14 |

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
backend/
  app/
    models/
      __init__.py
      store.py           # Store 모델
      admin_user.py      # AdminUser 모델
      table.py           # Table 모델
      session.py         # Session 모델
      order.py           # Order, OrderItem 모델
      menu.py            # Menu, Category 모델
      login_attempt.py   # LoginAttempt 모델
  alembic/
    versions/            # 마이그레이션 파일
    env.py
  alembic.ini
  seed.py                # 시드 데이터
```

**개발 순서**: 1단계 (최우선 — 백엔드의 기반)

---

### U2: Backend API (모놀리스)
**유형**: 모놀리스 백엔드 애플리케이션
**책임**: 모든 비즈니스 로직, API 엔드포인트, 인증, SSE를 단일 FastAPI 애플리케이션으로 제공

**범위**:
- **인증 모듈**: 관리자 로그인, JWT 토큰 발급/검증, bcrypt 해싱, 로그인 시도 제한
- **메뉴 모듈**: 메뉴 CRUD, 카테고리 관리, 이미지 업로드, 노출 순서 관리
- **테이블/세션 모듈**: 테이블 등록/관리, 세션 라이프사이클 (자동 생성, 이용 완료)
- **주문 모듈**: 주문 생성, 상태 변경(4단계), 삭제(상태 제한), 대시보드 데이터, 주문 내역 조회
- **SSE 모듈**: SSE 연결 관리, 이벤트 발행, 구독자 관리, 하트비트
- **공통**: JWT 미들웨어, CORS, 에러 핸들링, 파일 서빙

**내부 모듈 구조** (도메인 기준 논리적 분리):
- 인증 (Auth): Router, Service, Domain, Repository
- 메뉴 (Menu): Router, Service, Domain, Repository + FileService
- 테이블/세션 (Table/Session): Router, Service, Domain, Repository
- 주문 (Order): Router, Service, Domain, Repository
- SSE: Router, Service, Manager

**모듈 간 통신**: 동일 프로세스 내 **함수 호출** (HTTP 오버헤드 없음)
- OrderService → SessionService.get_or_create_session() (직접 함수 호출)
- OrderService → SSEService.publish_event() (직접 함수 호출)
- SessionService → SSEService.publish_event() (직접 함수 호출)
- MenuService → FileService.upload_image() (직접 함수 호출)

**컴포넌트**: 
- Router 6개: CustomerRouter, AdminAuthRouter, AdminOrderRouter, AdminTableRouter, AdminMenuRouter, SSERouter
- Service 7개: OrderService, MenuService, TableService, SessionService, AuthService, SSEService, FileService
- Domain 5개: OrderDomain, SessionDomain, MenuDomain, AuthDomain, TableDomain
- Repository 6개: OrderRepository, MenuRepository, TableRepository, SessionRepository, StoreRepository, AdminUserRepository
- 인프라 6개: Database, AlembicMigration, JWTMiddleware, CORSMiddleware, ErrorHandler, SSEManager

**기술 스택**: FastAPI, SQLAlchemy ORM, PyJWT, bcrypt, sse-starlette, python-multipart

**산출물**:
```
backend/
  app/
    routers/
      customer.py          # 고객용 API
      admin_auth.py        # 관리자 인증 API
      admin_order.py       # 관리자 주문 관리 API
      admin_table.py       # 관리자 테이블 관리 API
      admin_menu.py        # 관리자 메뉴 관리 API
      sse.py               # SSE 엔드포인트
    services/
      order_service.py
      menu_service.py
      table_service.py
      session_service.py
      auth_service.py
      sse_service.py
      file_service.py
    domain/
      order_domain.py
      session_domain.py
      menu_domain.py
      auth_domain.py
      table_domain.py
    repositories/
      order_repository.py
      menu_repository.py
      table_repository.py
      session_repository.py
      store_repository.py
      admin_user_repository.py
    models/               # SQLAlchemy 모델 (U1에서 정의)
    schemas/              # Pydantic 스키마 (요청/응답)
      auth_schemas.py
      order_schemas.py
      menu_schemas.py
      table_schemas.py
      session_schemas.py
      sse_schemas.py
    middleware/
      jwt_middleware.py
    config.py
    database.py           # DB 연결 설정
    main.py               # FastAPI 앱 엔트리포인트
  uploads/                # 이미지 저장 디렉토리
  tests/
  requirements.txt
```

**개발 순서**: 2단계 (DB 스키마 완성 후)

---

### U3: Customer App
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

**개발 순서**: 3단계 (백엔드 API 완성 후)

---

### U4: Admin App
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

**개발 순서**: 3단계 (백엔드 API 완성 후, Customer App과 병렬)

---

## 코드 조직 전략 (Greenfield — 모놀리스)

### 전체 디렉토리 구조

```
/ (workspace root)
├── backend/                     # U1 + U2: 모놀리스 백엔드
│   ├── app/
│   │   ├── routers/             # API 엔드포인트 (도메인별 분리)
│   │   ├── services/            # 비즈니스 오케스트레이션
│   │   ├── domain/              # 도메인 규칙
│   │   ├── repositories/        # 데이터 접근
│   │   ├── models/              # SQLAlchemy ORM 모델
│   │   ├── schemas/             # Pydantic 요청/응답 스키마
│   │   ├── middleware/          # JWT 등 미들웨어
│   │   ├── config.py            # 설정
│   │   ├── database.py          # DB 연결
│   │   └── main.py              # FastAPI 앱 엔트리포인트
│   ├── alembic/                 # DB 마이그레이션
│   ├── uploads/                 # 이미지 저장
│   ├── tests/
│   ├── alembic.ini
│   ├── seed.py
│   └── requirements.txt
│
├── frontend/                    # U3 + U4: 프론트엔드
│   ├── customer-app/
│   └── admin-app/
│
├── aidlc-docs/                  # AI-DLC 문서 (코드 아님)
└── aidlc-workshop/              # 워크숍 프로젝트 (코드 아님)
```

### 모듈 간 통신 방식
- **백엔드 내부**: 동일 프로세스 내 직접 함수 호출 (Service → Service, Service → SSEService)
- **프론트엔드 → 백엔드**: HTTP REST + SSE (단일 백엔드 서버 주소)
- **SSE 이벤트**: 트랜잭션 커밋 후 SSEService.publish_event() 직접 호출

### 모놀리스의 장점 (이 프로젝트에서)
- 단일 프로세스로 배포/운영 단순
- 서비스 간 통신이 함수 호출이므로 네트워크 오버헤드 없음
- 트랜잭션 관리가 단일 DB 세션으로 간결
- 도메인별 논리적 모듈 분리로 코드 정리는 유지

---

## 개발 순서 로드맵

```
단계 1: U1 (Database Schema)
  │
  ▼
단계 2: U2 (Backend API — 모놀리스)
  │
  ▼
단계 3: U3 (Customer App) + U4 (Admin App)  [병렬]
```
