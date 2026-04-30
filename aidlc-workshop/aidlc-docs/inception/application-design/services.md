# 테이블오더 서비스 - 서비스 레이어 설계서

---

## 1. 서비스 개요

서비스 레이어는 Router(API)와 Domain/Repository 사이에서 비즈니스 오케스트레이션을 담당합니다. 트랜잭션 경계를 관리하고, 여러 도메인/리포지토리를 조합하여 유스케이스를 실행합니다.

```
Router → Service → Domain (규칙 검증) → Repository (데이터 접근)
                 ↘ SSEService (이벤트 발행)
```

---

## 2. 서비스 정의

### 2.1 OrderService

**책임**: 주문 생성, 상태 변경, 삭제의 전체 흐름 오케스트레이션

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `create_order` | SessionService.get_or_create_session → OrderDomain.calculate_total → OrderRepository.create → SSEService.publish_event | Yes |
| `update_order_status` | OrderRepository.get_by_id → OrderDomain.validate_status_transition → OrderRepository.update_status → SSEService.publish_event | Yes |
| `delete_order` | OrderRepository.get_by_id → OrderDomain.can_delete → OrderRepository.delete → SSEService.publish_event | Yes |
| `get_orders_by_session` | SessionService.get_active_session → OrderRepository.get_by_session | No |
| `get_dashboard_data` | TableRepository.get_by_store → OrderRepository.get_active_orders_by_store → 집계 | No |
| `get_order_history` | OrderRepository.get_history | No |

**의존성**: SessionService, OrderDomain, OrderRepository, SSEService

---

### 2.2 MenuService

**책임**: 메뉴 CRUD 및 카테고리 관리, 이미지 파일 처리 포함

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `create_menu` | MenuDomain.validate_menu_data → FileService.upload_image → MenuRepository.create | Yes |
| `update_menu` | MenuDomain.validate_menu_data → FileService.upload_image (교체 시) → MenuRepository.update | Yes |
| `delete_menu` | MenuRepository.get_by_id → MenuRepository.delete → FileService.delete_image | Yes |
| `reorder_menus` | MenuRepository.update_sort_orders | Yes |
| `get_menus` | MenuRepository.get_by_store | No |
| `get_menu_detail` | MenuRepository.get_by_id | No |
| `get_categories` | CategoryRepository 조회 | No |
| `create_category` | CategoryRepository 생성 | Yes |

**의존성**: MenuDomain, MenuRepository, FileService

---

### 2.3 TableService

**책임**: 테이블 등록, 유효성 검증, URL 생성

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `validate_table` | StoreRepository.exists → TableRepository.get_by_store_and_number | No |
| `create_table` | TableDomain.validate_table_number → TableRepository.exists (중복 체크) → TableRepository.create | Yes |
| `get_tables` | TableRepository.get_by_store | No |
| `get_table_url` | TableDomain.generate_table_url | No |

**의존성**: TableDomain, TableRepository, StoreRepository

---

### 2.4 SessionService

**책임**: 세션 라이프사이클 관리 (생성, 조회, 종료)

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `get_or_create_session` | SessionRepository.get_active → SessionDomain.should_create_new_session → SessionRepository.create (필요 시) | Yes |
| `get_active_session` | SessionRepository.get_active | No |
| `complete_session` | SessionRepository.get_active → SessionDomain.can_complete_session → SessionRepository.complete → SSEService.publish_event | Yes |

**의존성**: SessionDomain, SessionRepository, SSEService

---

### 2.5 AuthService

**책임**: 관리자 인증, JWT 토큰 관리, 로그인 시도 제한

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `login` | AuthDomain.is_login_blocked → AdminUserRepository.get_by_username → AuthDomain.verify_password → AuthDomain.create_jwt_token → AdminUserRepository.record_login_attempt | Yes |
| `verify_token` | AuthDomain.decode_jwt_token → AdminUserRepository.get_by_username | No |
| `check_login_attempts` | AdminUserRepository.get_recent_attempts → AuthDomain.is_login_blocked | No |

**의존성**: AuthDomain, AdminUserRepository

---

### 2.6 SSEService

**책임**: SSE 연결 관리, 이벤트 발행, 구독자 관리

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `subscribe_table` | 연결 등록 → AsyncGenerator 반환 (테이블 단위) | No |
| `subscribe_store` | 연결 등록 → AsyncGenerator 반환 (매장 단위) | No |
| `publish_event` | 구독자 조회 → 이벤트 전달 (테이블 + 매장 구독자) | No |
| `disconnect` | 연결 해제 → 리소스 정리 | No |

**의존성**: 없음 (독립 인프라 컴포넌트)

**SSE 이벤트 타입**:
- `order_created` — 신규 주문 생성
- `order_status_changed` — 주문 상태 변경
- `order_deleted` — 주문 삭제
- `session_completed` — 세션 종료 (이용 완료)

**구독 구조**:
```
고객 (테이블 단위): /sse/stores/{store_id}/tables/{table_number}/orders
  → 해당 테이블의 주문 이벤트만 수신

관리자 (매장 단위): /sse/stores/{store_id}/orders
  → 매장 전체 테이블의 주문 이벤트 수신
```

---

### 2.7 FileService

**책임**: 이미지 파일 업로드, 저장, 삭제, URL 생성

| 메서드 | 오케스트레이션 흐름 | 트랜잭션 |
|---|---|---|
| `upload_image` | 파일 검증 → 고유 파일명 생성 → 로컬 파일 시스템 저장 → 경로 반환 | No |
| `delete_image` | 파일 존재 확인 → 파일 삭제 | No |
| `get_image_url` | 파일 경로 → 서빙 URL 변환 | No |

**의존성**: 없음 (독립 유틸리티)

**저장 구조**:
```
uploads/
  stores/{store_id}/
    menus/
      {uuid}_{original_filename}.{ext}
```

---

## 3. 트랜잭션 경계 정책

| 정책 | 설명 |
|---|---|
| **단위** | Service 메서드 단위로 트랜잭션 관리 |
| **전파** | 하나의 Service 메서드 내에서 단일 트랜잭션 |
| **롤백** | 예외 발생 시 자동 롤백 |
| **SSE 발행** | 트랜잭션 커밋 후 SSE 이벤트 발행 (데이터 일관성 보장) |
| **파일 업로드** | DB 트랜잭션 실패 시 업로드된 파일 정리 (보상 트랜잭션) |

---

## 4. 서비스 간 호출 규칙

```
OrderService ──→ SessionService (세션 조회/생성) [직접 함수 호출]
OrderService ──→ SSEService (이벤트 발행) [직접 함수 호출]
SessionService ─→ SSEService (세션 종료 이벤트) [직접 함수 호출]
MenuService ───→ FileService (이미지 처리) [직접 함수 호출]
```

**규칙**:
1. Service → Service 호출은 최소화 (순환 의존 방지)
2. OrderService → SessionService 호출만 허용 (주문 생성 시 세션 필요)
3. SSEService는 이벤트 발행 전용으로 다른 서비스에서 단방향 호출
4. FileService는 유틸리티 성격으로 MenuService에서만 호출
5. 모든 서비스 간 호출은 동일 프로세스 내 직접 함수 호출 (모놀리스 — HTTP 오버헤드 없음)
