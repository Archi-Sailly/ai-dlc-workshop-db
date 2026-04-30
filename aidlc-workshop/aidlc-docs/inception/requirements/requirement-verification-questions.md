# 테이블오더 서비스 - 요구사항 명확화 질문

아래 질문들에 대해 [Answer]: 태그 뒤에 선택지 문자를 입력해 주세요.
제공된 선택지가 맞지 않으면 마지막 옵션(Other)을 선택하고 설명을 추가해 주세요.

---

## Question 1
백엔드 기술 스택으로 어떤 것을 선호하시나요?

A) Node.js + Express (JavaScript/TypeScript)
B) Node.js + NestJS (TypeScript)
C) Python + FastAPI
D) Java + Spring Boot
E) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question 2
프론트엔드 기술 스택으로 어떤 것을 선호하시나요?

A) React (JavaScript/TypeScript)
B) Next.js (React 기반 풀스택 프레임워크)
C) Vue.js
D) Vanilla HTML/CSS/JavaScript
E) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3
데이터베이스로 어떤 것을 사용하시겠습니까?

A) PostgreSQL (관계형 데이터베이스)
B) MySQL (관계형 데이터베이스)
C) MongoDB (NoSQL Document)
D) DynamoDB (AWS NoSQL)
E) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4
배포 환경은 어디를 대상으로 하시나요?

A) AWS (EC2, ECS, Lambda 등)
B) 로컬 서버 / On-premises
C) Docker 컨테이너 (배포 환경 미정)
D) 아직 결정하지 않음 (개발 환경만 우선 구성)
E) Other (please describe after [Answer]: tag below)

[Answer]: B (로컬)

## Question 5
매장(Store) 관리 구조는 어떻게 되나요? (멀티테넌시)

A) 단일 매장만 지원 (하나의 서버에 하나의 매장)
B) 다중 매장 지원 (하나의 서버에 여러 매장, 각 매장 독립 데이터)
C) 아직 결정하지 않음 (MVP는 단일 매장, 추후 확장 고려)
D) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 6
메뉴 이미지 관리는 어떻게 하시겠습니까?

A) 외부 URL 링크만 사용 (이미지 업로드 기능 없음)
B) 서버에 직접 파일 업로드 (로컬 파일 시스템 저장)
C) 클라우드 스토리지 업로드 (S3 등)
D) 아직 결정하지 않음 (MVP에서는 URL만 사용)
E) Other (please describe after [Answer]: tag below)

[Answer]: B(로컬 파일 시스템 저장)

## Question 7
고객용 태블릿 UI의 주요 사용 디바이스 크기는?

A) 10인치 이상 태블릿 전용
B) 7~10인치 태블릿 중심 (모바일도 고려)
C) 반응형 디자인 (태블릿 + 모바일 + 데스크톱 모두 지원)
D) Other (please describe after [Answer]: tag below)

[Answer]: B(태블릿 + 모바일)

## Question 8
관리자 대시보드의 주요 사용 디바이스는?

A) 데스크톱/노트북 전용
B) 태블릿도 지원하는 반응형 디자인
C) 모든 디바이스 지원 (데스크톱 + 태블릿 + 모바일)
D) Other (please describe after [Answer]: tag below)

[Answer]: C(데스크톱+태블릿+모바일 전부)

## Question 9
주문 상태 변경 흐름은 어떻게 되나요?

A) 대기중 → 준비중 → 완료 (3단계)
B) 대기중 → 접수 → 준비중 → 완료 (4단계)
C) 대기중 → 완료 (2단계, 단순화)
D) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 10
동시 접속 규모 예상은 어떻게 되나요? (하나의 매장 기준)

A) 소규모 (테이블 10개 이하, 동시 주문 5건 이하)
B) 중규모 (테이블 10~30개, 동시 주문 10~20건)
C) 대규모 (테이블 30개 이상, 동시 주문 20건 이상)
D) 아직 결정하지 않음 (MVP 기준 소규모로 시작)
E) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 11
테이블 비밀번호의 용도와 보안 수준은?

A) 단순 식별용 (4자리 숫자 PIN)
B) 보안 인증용 (영문+숫자 조합, 최소 8자)
C) 관리자가 설정하는 간단한 코드 (자유 형식)
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 12
고객 주문 내역의 실시간 상태 업데이트(SSE)를 고객 화면에도 적용하시겠습니까?

A) 예 - 고객 화면에서도 주문 상태를 실시간으로 업데이트
B) 아니오 - 고객 화면은 페이지 새로고침 시에만 업데이트 (관리자 화면만 SSE)
C) 선택사항으로 두고 MVP에서는 새로고침 방식, 추후 SSE 추가
D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 13: Security Extensions
이 프로젝트에 보안 확장 규칙(Security Extension Rules)을 적용하시겠습니까?

A) 예 — 모든 SECURITY 규칙을 blocking constraint로 적용 (프로덕션 수준 애플리케이션에 권장)
B) 아니오 — 모든 SECURITY 규칙 건너뛰기 (PoC, 프로토타입, 실험적 프로젝트에 적합)
C) Other (please describe after [Answer]: tag below)

[Answer]: B
