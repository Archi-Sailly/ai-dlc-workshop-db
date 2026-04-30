# 테이블오더 서비스 - 팀 역할 분배

## 구성: 4인 (백엔드 2 + 프론트엔드 2)

---

## 팀원별 담당

### 팀원 A — 백엔드 (DB + Order + SSE)

| 유닛 | 단계 | 스토리 |
|---|---|---|
| U1: Database Schema | 1단계 | 기반 인프라 |
| U5: Order Service | 3단계 | US-C07, C08, A03, A04, A05, A07 (6개) |
| U6: SSE Service | 3단계 | US-C09, A03 (2개) |

**핵심 기술**: PostgreSQL, SQLAlchemy, Alembic, FastAPI, SSE
**작업 흐름**:
- 단계 1: DB 스키마 설계 + Alembic 마이그레이션 + 시드 데이터
- 단계 2: 팀원 B 지원 (코드 리뷰, 공유 라이브러리 정비)
- 단계 3: Order Service + SSE Service 병렬 개발

---

### 팀원 B — 백엔드 (Auth + Menu + Table/Session)

| 유닛 | 단계 | 스토리 |
|---|---|---|
| U2: Auth Service | 2단계 | US-A01, A02 (2개) |
| U3: Menu Service | 2단계 | US-C03, A10, A11, A12, A13, A14 (6개) |
| U4: Table & Session Service | 2단계 | US-C01, A06, A08 (3개) |

**핵심 기술**: FastAPI, JWT, bcrypt, SQLAlchemy, 파일 업로드
**작업 흐름**:
- 단계 1: 팀원 A의 DB 스키마 리뷰 참여
- 단계 2: Auth → Menu → Table/Session 순차 개발 (Auth 먼저 완성하여 JWT 미들웨어 공유)
- 단계 3: 통합 테스트 지원, API 문서 정리

---

### 팀원 C — 프론트엔드 (Customer App)

| 유닛 | 단계 | 스토리 |
|---|---|---|
| U7: Customer App | 4단계 | US-C01, C03, C04, C05, C06, C07, C08, C09 (8개) |

**핵심 기술**: React, TypeScript, Zustand, SSE (EventSource), localStorage
**컴포넌트**: 페이지 6 + 공통 UI 9 + 훅 4 + 스토어 3 = **22개**
**작업 흐름**:
- 단계 1~2: 프로젝트 초기 설정 (Vite, 라우팅, Zustand 스토어 구조, 공통 컴포넌트)
- 단계 2~3: Mock API 기반 UI 개발 (장바구니는 백엔드 불필요, 즉시 개발 가능)
- 단계 4: 백엔드 API 연동 + SSE 통합

---

### 팀원 D — 프론트엔드 (Admin App)

| 유닛 | 단계 | 스토리 |
|---|---|---|
| U8: Admin App | 4단계 | US-A01~A14 전체 (14개) |

**핵심 기술**: React, TypeScript, Zustand, SSE, JWT 인터셉터, 이미지 업로드
**컴포넌트**: 페이지 7 + 공통 UI 10 + 훅 6 + 스토어 4 = **27개**
**작업 흐름**:
- 단계 1~2: 프로젝트 초기 설정 (Vite, 라우팅, 인증 흐름, SideNav 레이아웃)
- 단계 2~3: Mock API 기반 UI 개발 (로그인 화면, 대시보드 레이아웃, 메뉴 관리 폼)
- 단계 4: 백엔드 API 연동 + SSE 통합 + JWT 인터셉터

---

## 단계별 타임라인

```
단계 1                단계 2                    단계 3                단계 4
─────────────────────────────────────────────────────────────────────────────

팀원A  [U1: DB 스키마]  [리뷰/공유 라이브러리]     [U5: Order + U6: SSE]  [통합 테스트]
팀원B  [DB 리뷰]       [U2: Auth→U3: Menu→U4: T&S] [통합 테스트/API 문서]  [통합 테스트]
팀원C  [프로젝트 셋업]  [Mock UI: 장바구니/메뉴]    [Mock UI: 주문/내역]   [U7: API 연동]
팀원D  [프로젝트 셋업]  [Mock UI: 로그인/레이아웃]  [Mock UI: 대시보드/메뉴] [U8: API 연동]
```

---

## 작업량 비교

| 팀원 | 유닛 수 | 스토리 수 | 컴포넌트 수 | 비고 |
|---|---|---|---|---|
| A | 3 (U1, U5, U6) | 8 | 백엔드 ~15 | 가장 복잡한 주문 로직 + DB 설계 |
| B | 3 (U2, U3, U4) | 11 | 백엔드 ~20 | 서비스 수 많지만 개별 복잡도 낮음 |
| C | 1 (U7) | 8 | 프론트 22 | 장바구니(localStorage) 독립 개발 가능 |
| D | 1 (U8) | 14 | 프론트 27 | 스토리 수 최다, 대시보드 SSE 복잡 |

---

## 협업 포인트

### 백엔드 ↔ 백엔드 (A ↔ B)
- **공유 라이브러리**: `shared/jwt_utils.py`, `shared/db_config.py` — 팀원 A가 단계 1에서 생성, 팀원 B가 단계 2에서 사용
- **DB 모델**: 팀원 A가 설계, 팀원 B가 리뷰 후 양쪽 서비스에서 공유
- **서비스 간 통신**: U5(Order) → U4(Table/Session) 내부 API — A와 B가 인터페이스 합의 필요

### 백엔드 ↔ 프론트엔드 (A,B ↔ C,D)
- **API 스펙 공유**: 단계 2 시작 시 API 엔드포인트 목록 + 요청/응답 스키마 공유
- **Mock API**: 프론트엔드 팀이 단계 2~3에서 사용할 Mock 데이터 정의
- **SSE 이벤트 포맷**: 팀원 A(U6)가 이벤트 타입/데이터 포맷 정의 → 팀원 C, D에게 공유

### 프론트엔드 ↔ 프론트엔드 (C ↔ D)
- **공통 타입 정의**: API 응답 타입, 주문 상태 enum 등 공유
- **공통 컴포넌트**: ConfirmDialog, LoadingSpinner 등 중복 컴포넌트 한쪽에서 만들어 공유 가능
