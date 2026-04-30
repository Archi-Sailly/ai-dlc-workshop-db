# Application Design Plan - 테이블오더 서비스

## 목적
시스템의 주요 컴포넌트를 식별하고, 서비스 레이어를 설계하며, 컴포넌트 간 의존성과 통신 패턴을 정의합니다.

> **참고**: 상세 비즈니스 로직은 Construction 단계의 Functional Design에서 정의됩니다. 이 단계에서는 고수준 컴포넌트 구조와 인터페이스에 집중합니다.

---

## 설계 질문

아래 질문에 `[Answer]:` 태그 뒤에 답변을 작성해 주세요.

### Q1. 백엔드 아키텍처 패턴
FastAPI 백엔드의 레이어 구조를 어떻게 구성할까요?

- **A**: 3-Layer (Router → Service → Repository) — 간결하고 MVP에 적합
- **B**: 4-Layer (Router → Service → Domain → Repository) — 도메인 로직 분리, 확장성 우수

[Answer]: B

### Q2. 프론트엔드 구성 방식
고객 UI와 관리자 UI를 어떻게 구성할까요?

- **A**: 단일 React 앱 (라우팅으로 분리) — 코드 공유 용이, 빌드 단순
- **B**: 별도 React 앱 2개 (Customer App + Admin App) — 독립 배포, 관심사 완전 분리
- **C**: 모노레포 (공유 패키지 + 2개 앱) — 코드 공유 + 독립 빌드 모두 가능

[Answer]: B

### Q3. 상태 관리 라이브러리
React 프론트엔드의 상태 관리를 어떻게 할까요?

- **A**: React Context + useReducer — 외부 의존성 없음, 소규모에 적합
- **B**: Zustand — 경량, 보일러플레이트 최소, SSE 실시간 상태 관리에 적합
- **C**: Redux Toolkit — 대규모 상태 관리, DevTools 지원, 러닝커브 있음

[Answer]: B

### Q4. SSE 이벤트 구조
SSE 이벤트를 어떤 단위로 발행할까요?

- **A**: 매장 단위 (store-level) — 매장 전체 이벤트를 하나의 스트림으로 구독, 클라이언트에서 필터링
- **B**: 테이블 단위 (table-level) — 테이블별 개별 스트림, 서버 부하 분산

[Answer]: B

### Q5. 데이터베이스 마이그레이션 도구
PostgreSQL 스키마 관리를 어떻게 할까요?

- **A**: Alembic (SQLAlchemy 기반) — Python 생태계 표준, 자동 마이그레이션 생성
- **B**: Raw SQL 마이그레이션 스크립트 — 단순, ORM 비의존

[Answer]: A

### Q6. ORM 사용 여부
데이터베이스 접근 방식을 어떻게 할까요?

- **A**: SQLAlchemy (ORM) — 모델 정의, 관계 매핑, 쿼리 빌더
- **B**: SQLAlchemy Core (SQL Expression) — ORM 없이 SQL 표현식 사용
- **C**: asyncpg + Raw SQL — 최고 성능, 직접 SQL 작성

[Answer]: A

### Q7. 이미지 업로드 처리
메뉴 이미지 업로드를 어떻게 처리할까요?

- **A**: FastAPI 내장 파일 업로드 (UploadFile) — 단순, 별도 설정 불필요
- **B**: 별도 파일 서비스 컴포넌트 분리 — 파일 관리 로직 독립, 향후 스토리지 변경 용이

[Answer]: A

---

## 설계 산출물 생성 계획

### Phase 1: 컴포넌트 식별
- [x] 백엔드 컴포넌트 식별 (Router, Service, Repository 레이어별)
- [x] 프론트엔드 컴포넌트 식별 (페이지, 공통 컴포넌트, 훅)
- [x] 인프라 컴포넌트 식별 (DB, SSE, Auth 미들웨어)
- [x] `components.md` 생성

### Phase 2: 컴포넌트 메서드 정의
- [x] 각 백엔드 컴포넌트의 메서드 시그니처 정의
- [x] 각 프론트엔드 컴포넌트의 주요 인터페이스 정의
- [x] 입출력 타입 정의
- [x] `component-methods.md` 생성

### Phase 3: 서비스 레이어 설계
- [x] 서비스 정의 및 책임 범위
- [x] 서비스 간 오케스트레이션 패턴
- [x] 트랜잭션 경계 정의
- [x] `services.md` 생성

### Phase 4: 컴포넌트 의존성 설계
- [x] 의존성 매트릭스 작성
- [x] 통신 패턴 정의 (동기/비동기)
- [x] 데이터 흐름 다이어그램
- [x] `component-dependency.md` 생성

### Phase 5: 통합 문서
- [x] 전체 설계 통합 문서 작성
- [x] `application-design.md` 생성

### Phase 6: 검증
- [x] 요구사항 커버리지 확인 (22개 스토리 100% 커버)
- [x] 유저 스토리 매핑 검증
- [x] 설계 일관성 검증
