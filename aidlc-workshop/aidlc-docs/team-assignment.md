# 테이블오더 서비스 - 팀 역할 분배

## 구성: 4인 (백엔드 2 + 프론트엔드 2)

> **아키텍처**: 모놀리스 (Backend 1개 + Frontend 2개 = 3개 배포 단위)
> **유닛 구조**: U1(DB Schema) + U2(Backend API 모놀리스) + U3(Customer App) + U4(Admin App)

---

## 팀원별 담당

### 팀원 A — 백엔드 (DB + Order 모듈 + SSE 모듈)

| 담당 | 유닛/모듈 | 단계 | 스토리 |
|---|---|---|---|
| Database Schema | U1 | 1단계 | 기반 인프라 |
| Order 모듈 | U2 내부 | 2단계 | US-C07, C08, A03, A04, A05, A07, A09 (7개) |
| SSE 모듈 | U2 내부 | 2단계 | US-C09, A03 (2개) |

**핵심 기술**: PostgreSQL, SQLAlchemy, Alembic, FastAPI, SSE
**작업 흐름**:
- 단계 1: DB 스키마 설계 + Alembic 마이그레이션 + 시드 데이터 + `backend/app/database.py` (DB 연결 설정)
- 단계 2-전반: 팀원 B 지원 (코드 리뷰), `backend/app/main.py` 앱 엔트리포인트 + 공통 미들웨어(CORS, ErrorHandler) 셋업
- 단계 2-후반: Order 모듈 + SSE 모듈 개발 (동일 `backend/app/` 내에서 작업)

> **참고**: US-A09(과거 주문 내역 조회)는 Order 모듈이 주 담당이지만, Session 모듈의 sessions 테이블에서 "이용 완료 시각"을 JOIN으로 가져와야 합니다. 팀원 B와 SessionRepository 인터페이스 합의 필요.

---

### 팀원 B — 백엔드 (Auth 모듈 + Menu 모듈 + Table/Session 모듈)

| 담당 | 유닛/모듈 | 단계 | 스토리 |
|---|---|---|---|
| Auth 모듈 | U2 내부 | 2단계 | US-A01, A02 (2개) |
| Menu 모듈 | U2 내부 | 2단계 | US-C03, A10, A11, A12, A13, A14 (6개) |
| Table/Session 모듈 | U2 내부 | 2단계 | US-C01, A06, A08 (3개) |

**핵심 기술**: FastAPI, JWT, bcrypt, SQLAlchemy, 파일 업로드 (UploadFile)
**작업 흐름**:
- 단계 1: 팀원 A의 DB 스키마 리뷰 참여
- 단계 2-전반: Auth 모듈 먼저 완성 (JWT 미들웨어 → `backend/app/middleware/jwt_middleware.py`)
- 단계 2-후반: Menu 모듈 + Table/Session 모듈 병렬 개발

---

### 팀원 C — 프론트엔드 (Customer App)

| 담당 | 유닛 | 단계 | 스토리 |
|---|---|---|---|
| Customer App | U3 | 3단계 | US-C01, C03, C04, C05, C06, C07, C08, C09 (8개) |

**핵심 기술**: React, TypeScript, Zustand, SSE (EventSource), localStorage
**컴포넌트**: 페이지 6 + 공통 UI 9 + 훅 4 + 스토어 3 = **22개**
**작업 흐름**:
- 단계 1: 프로젝트 초기 설정 (`frontend/customer-app/` — Vite, 라우팅, Zustand 스토어 구조, 공통 컴포넌트)
- 단계 2: Mock API 기반 UI 개발 (장바구니는 백엔드 불필요, 즉시 개발 가능)
- 단계 3: 백엔드 API 연동 + SSE 통합 (단일 백엔드 서버 주소 설정)

---

### 팀원 D — 프론트엔드 (Admin App)

| 담당 | 유닛 | 단계 | 스토리 |
|---|---|---|---|
| Admin App | U4 | 3단계 | US-A01~A14 전체 (14개) |

**핵심 기술**: React, TypeScript, Zustand, SSE, JWT 인터셉터, 이미지 업로드
**컴포넌트**: 페이지 7 + 공통 UI 10 + 훅 6 + 스토어 4 = **27개**
**작업 흐름**:
- 단계 1: 프로젝트 초기 설정 (`frontend/admin-app/` — Vite, 라우팅, 인증 흐름, SideNav 레이아웃)
- 단계 2: Mock API 기반 UI 개발 (로그인 화면, 대시보드 레이아웃, 메뉴 관리 폼)
- 단계 3: 백엔드 API 연동 + SSE 통합 + JWT 인터셉터 (단일 백엔드 서버 주소 설정)

---

## 단계별 타임라인

```
단계 1                단계 2                              단계 3
──────────────────────────────────────────────────────────────────────

팀원A  [U1: DB 스키마]  [U2: main.py 셋업 → Order+SSE 모듈]  [통합 테스트]
팀원B  [DB 리뷰]       [U2: Auth → Menu+Table/Session 모듈]  [통합 테스트]
팀원C  [프로젝트 셋업]  [Mock UI: 장바구니/메뉴/주문]          [U3: API 연동]
팀원D  [프로젝트 셋업]  [Mock UI: 로그인/대시보드/메뉴관리]     [U4: API 연동]
```

> **참고**: 마이크로서비스(4단계)에서 모놀리스(3단계)로 전환되면서 백엔드 개발이 단계 2에 통합되었습니다. 팀원 A와 B는 동일 `backend/app/` 코드베이스에서 도메인 모듈별로 분업합니다.

---

## 작업량 비교

| 팀원 | 유닛/모듈 | 스토리 수 | 컴포넌트 수 | 비고 |
|---|---|---|---|---|
| A | U1 + U2(Order, SSE) | 9 | 백엔드 ~15 | DB 설계 + 가장 복잡한 주문 로직 + SSE |
| B | U2(Auth, Menu, Table/Session) | 11 | 백엔드 ~20 | 모듈 수 많지만 개별 복잡도 낮음 |
| C | U3 (Customer App) | 8 | 프론트 22 | 장바구니(localStorage) 독립 개발 가능 |
| D | U4 (Admin App) | 14 | 프론트 27 | 스토리 수 최다, 대시보드 SSE 복잡 |

---

## 협업 포인트

### 백엔드 ↔ 백엔드 (A ↔ B) — 동일 코드베이스 내 협업

모놀리스 구조이므로 팀원 A와 B는 **동일 `backend/app/` 디렉토리**에서 작업합니다.

- **코드 충돌 방지**: 도메인 모듈별로 디렉토리가 분리되어 있으므로 (routers/, services/, domain/, repositories/) 파일 수준 충돌은 적음. 단, `main.py`, `database.py`, `config.py` 등 공통 파일은 팀원 A가 초기 셋업 후 양쪽이 라우터 등록 시 조율 필요.
- **DB 모델**: 팀원 A가 `backend/app/models/` 설계, 팀원 B가 리뷰 후 양쪽 모듈에서 import하여 사용
- **JWT 미들웨어**: 팀원 B가 Auth 모듈에서 `backend/app/middleware/jwt_middleware.py` 생성 → 팀원 A의 AdminOrderRouter에서도 사용
- **모듈 간 함수 호출 인터페이스**: OrderService → SessionService 호출 시그니처를 A와 B가 합의 (HTTP가 아닌 Python 함수 시그니처)
- **US-A09 크로스 모듈**: 팀원 A(Order)가 팀원 B(Session)의 SessionRepository 또는 sessions 테이블 JOIN 방식 합의

### 백엔드 ↔ 프론트엔드 (A,B ↔ C,D)

- **API 스펙 공유**: 단계 2 시작 시 API 엔드포인트 목록 + Pydantic 스키마(`backend/app/schemas/`) 공유
- **단일 서버 주소**: 모놀리스이므로 프론트엔드는 하나의 base URL만 설정 (서비스별 URL 분리 불필요)
- **Mock API**: 프론트엔드 팀이 단계 2에서 사용할 Mock 데이터 정의
- **SSE 이벤트 포맷**: 팀원 A(SSE 모듈)가 이벤트 타입/데이터 포맷 정의 → 팀원 C, D에게 공유

### 프론트엔드 ↔ 프론트엔드 (C ↔ D)

- **공통 타입 정의**: API 응답 타입, 주문 상태 enum 등 공유
- **공통 컴포넌트**: ConfirmDialog, LoadingSpinner 등 중복 컴포넌트 한쪽에서 만들어 공유 가능
