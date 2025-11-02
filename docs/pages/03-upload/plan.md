# TDD 기반 구현 계획: 데이터 업로드
## University Data Visualization Dashboard

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 1.0
- **대상 기능**: Django Admin 파일 업로드, Pandas 파싱, 데이터 검증
- **관련 Use Cases**: UC-03 (데이터 업로드), UC-12 (업로드 이력)
- **관련 문서**: `/docs/database.md`, `/docs/userflow.md`, `/docs/common-modules.md`

---

## 1. TDD 개발 프로세스 개요

### 1.1 핵심 원칙
- **Red → Green → Refactor** 사이클 철저히 준수
- **테스트 먼저 작성** (Test First)
- **최소한의 코드로 통과** (YAGNI 원칙)
- **작은 단위로 커밋** (Small Commits)
- **FIRST 원칙 적용** (Fast, Independent, Repeatable, Self-validating, Timely)
- **AAA 패턴 사용** (Arrange, Act, Assert)

### 1.2 테스트 피라미드 전략
```
            /\
           /  \  Acceptance Tests (10%)
          /____\  - Django Admin 업로드 플로우
         /      \  - End-to-End 시나리오
        / Integ. \ Integration Tests (20%)
       /__________\ - Admin + Parser + DB
      /            \ - Signal + Validation
     /    Unit      \ Unit Tests (70%)
    /________________\ - Parser, Validator 단위 테스트
```

**예상 테스트 케이스 수:**
- Unit Tests: ~70개 (Parser 40, Validator 30)
- Integration Tests: ~20개 (Admin 통합 테스트)
- Acceptance Tests: ~8개 (4개 데이터 타입 × 2 시나리오)
- **총 예상**: ~98개 테스트

---

## 2. 구현 우선순위 및 순서

### 2.1 우선순위 (높음 → 낮음)

| 우선순위 | 기능 | 이유 | 예상 소요 시간 |
|---------|------|------|--------------|
| 1 | UploadHistory 모델 | 업로드 이력 추적 필수 | 2시간 |
| 2 | 데이터 Validator | 데이터 무결성 보장 | 6시간 |
| 3 | BaseParser | 모든 파서의 기반 | 3시간 |
| 4 | DepartmentKPIParser | 핵심 지표 | 4시간 |
| 5 | PublicationParser | 연구 성과 | 4시간 |
| 6 | ResearchBudgetParser | 재정 데이터 (복잡) | 6시간 |
| 7 | StudentParser | 학사 데이터 | 4시간 |
| 8 | Django Admin 커스터마이징 | UI 통합 | 5시간 |
| 9 | 업로드 후처리 Signal | 자동화 | 2시간 |

**총 예상 시간**: 36시간 (4~5일)

---

### 2.2 개발 순서 (TDD 사이클별)

#### Phase 1: UploadHistory 모델 (2시간)

```
Cycle 1: 기본 필드 정의
  Red   → test_upload_history_creation() 작성
  Green → UploadHistory 모델 기본 필드 정의
  Refactor → Meta 옵션 추가

Cycle 2: FK 관계 설정
  Red   → test_upload_history_user_relation() 작성
  Green → user_id FK 추가
  Refactor → on_delete 정책 확인

Cycle 3: 상태별 쿼리 메서드
  Red   → test_get_successful_uploads() 작성
  Green → 모델 매니저 메서드 구현
  Refactor → 없음

Cycle 4: 최근 업로드 조회
  Red   → test_get_recent_uploads() 작성
  Green → 정렬 및 제한 쿼리 추가
  Refactor → 인덱스 최적화 검토
```

---

#### Phase 2: 데이터 Validator (6시간)

##### 2.1 공통 Validator
```
Cycle 1: 필수 컬럼 검증
  Red   → test_validate_required_columns() 작성
  Green → validate_required_columns() 함수 구현
  Refactor → 에러 메시지 개선

Cycle 2: 데이터 타입 검증
  Red   → test_validate_data_types() 작성
  Green → validate_data_types() 함수 구현
  Refactor → Pandas dtype 활용

Cycle 3: 값 범위 검증
  Red   → test_validate_value_ranges() 작성
  Green → validate_value_ranges() 함수 구현
  Refactor → CHECK 제약조건과 일치시키기

Cycle 4: 중복 검증
  Red   → test_validate_duplicates() 작성
  Green → validate_duplicates() 함수 구현
  Refactor → DB 쿼리 최적화
```

##### 2.2 DepartmentKPI Validator
```
Cycle 1: 스키마 검증
  Red   → test_validate_department_kpi_schema() 작성
  Green → validate_department_kpi_data() 함수 구현
  Refactor → 없음

Cycle 2: 취업률 범위 검증 (0~100%)
  Red   → test_employment_rate_range() 작성
  Green → 범위 체크 로직 추가
  Refactor → 없음

Cycle 3: 음수 검증 (교원 수, 수입액 등)
  Red   → test_negative_values_rejected() 작성
  Green → 음수 체크 로직 추가
  Refactor → 없음

Cycle 4: 연도 유효성 검증
  Red   → test_evaluation_year_range() 작성
  Green → 연도 범위 체크 (2000~2100)
  Refactor → 상수 정의 분리
```

##### 2.3 Publication Validator
```
Cycle 1: 필수 필드 검증
  Red   → test_publication_required_fields() 작성
  Green → validate_publication_data() 함수 구현
  Refactor → 없음

Cycle 2: 논문ID 유니크 검증
  Red   → test_publication_id_uniqueness() 작성
  Green → 중복 체크 로직 추가
  Refactor → DB 쿼리로 확인

Cycle 3: 저널 등급 검증
  Red   → test_journal_grade_validation() 작성
  Green → 허용된 등급 리스트 체크
  Refactor → 상수 활용

Cycle 4: Impact Factor 음수 검증
  Red   → test_impact_factor_positive() 작성
  Green → 음수 체크 추가
  Refactor → 없음

Cycle 5: 날짜 형식 검증
  Red   → test_publication_date_format() 작성
  Green → Pandas to_datetime() 활용
  Refactor → 에러 메시지 개선
```

##### 2.4 ResearchBudget Validator
```
Cycle 1: 필수 필드 검증
  Red   → test_research_budget_required_fields() 작성
  Green → validate_research_budget_data() 함수 구현
  Refactor → 없음

Cycle 2: 집행ID 유니크 검증
  Red   → test_execution_id_uniqueness() 작성
  Green → 중복 체크 로직 추가
  Refactor → 없음

Cycle 3: 총연구비 양수 검증
  Red   → test_total_budget_positive() 작성
  Green → 양수 체크 로직 추가
  Refactor → 없음

Cycle 4: 집행금액 음수 검증
  Red   → test_execution_amount_non_negative() 작성
  Green → 음수 체크 추가
  Refactor → 없음

Cycle 5: 상태 값 검증
  Red   → test_execution_status_validation() 작성
  Green → 허용된 상태 리스트 체크
  Refactor → 상수 활용

Cycle 6: 과제별 예산 초과 검증
  Red   → test_execution_not_exceeds_budget() 작성
  Green → 과제별 집행금액 합계 vs 총연구비 비교
  Refactor → 경고 메시지 개선
```

##### 2.5 Student Validator
```
Cycle 1: 필수 필드 검증
  Red   → test_student_required_fields() 작성
  Green → validate_student_data() 함수 구현
  Refactor → 없음

Cycle 2: 학번 유니크 검증
  Red   → test_student_number_uniqueness() 작성
  Green → 중복 체크 로직 추가
  Refactor → 없음

Cycle 3: 학년 범위 검증 (0~4)
  Red   → test_grade_range() 작성
  Green → 범위 체크 로직 추가
  Refactor → 없음

Cycle 4: 과정구분 검증
  Red   → test_program_type_validation() 작성
  Green → 허용된 과정 리스트 체크
  Refactor → 상수 활용

Cycle 5: 학적상태 검증
  Red   → test_enrollment_status_validation() 작성
  Green → 허용된 상태 리스트 체크
  Refactor → 없음

Cycle 6: 성별 검증
  Red   → test_gender_validation() 작성
  Green → 허용된 성별 리스트 체크
  Refactor → 없음

Cycle 7: 이메일 형식 검증 (선택 필드)
  Red   → test_email_format_validation() 작성
  Green → 정규식 검증 추가
  Refactor → 없음
```

---

#### Phase 3: BaseParser (3시간)

```
Cycle 1: 파일 읽기 기능
  Red   → test_base_parser_reads_file() 작성
  Green → read_file() 메서드 구현 (Pandas)
  Refactor → 인코딩 자동 감지 추가

Cycle 2: 확장자 검증
  Red   → test_validate_file_extension() 작성
  Green → validate_extension() 메서드 구현
  Refactor → 상수 활용

Cycle 3: 파일 크기 검증
  Red   → test_validate_file_size() 작성
  Green → validate_size() 메서드 구현 (최대 50MB)
  Refactor → 없음

Cycle 4: 에러 핸들링
  Red   → test_parse_handles_errors() 작성
  Green → try-except 블록 추가
  Refactor → 커스텀 예외 클래스 사용

Cycle 5: 추상 메서드 정의
  Red   → test_base_parser_is_abstract() 작성
  Green → ABC 상속, abstractmethod 정의
  Refactor → 없음
```

---

#### Phase 4: DepartmentKPIParser (4시간)

```
Cycle 1: CSV 컬럼 매핑
  Red   → test_parse_department_kpi_columns() 작성
  Green → parse() 메서드에서 컬럼명 매핑
  Refactor → 매핑 딕셔너리 상수화

Cycle 2: 데이터 정제 (공백, NaN)
  Red   → test_clean_department_kpi_data() 작성
  Green → clean_data() 메서드 구현
  Refactor → Pandas fillna(), strip() 활용

Cycle 3: 타입 변환
  Red   → test_convert_data_types() 작성
  Green → astype() 활용하여 타입 변환
  Refactor → 없음

Cycle 4: 검증 통합
  Red   → test_parse_validates_data() 작성
  Green → Validator 호출 추가
  Refactor → 에러 처리 개선

Cycle 5: DB 저장 (bulk_create)
  Red   → test_save_to_db_bulk_create() 작성
  Green → save_to_db() 메서드 구현
  Refactor → batch_size 최적화

Cycle 6: 중복 처리 전략
  Red   → test_handle_duplicates() 작성
  Green → ignore_conflicts 옵션 추가
  Refactor → 없음
```

---

#### Phase 5: PublicationParser (4시간)

```
Cycle 1: CSV 컬럼 매핑
  Red   → test_parse_publication_columns() 작성
  Green → parse() 메서드에서 컬럼명 매핑
  Refactor → 매핑 딕셔너리 상수화

Cycle 2: 날짜 파싱
  Red   → test_parse_publication_date() 작성
  Green → Pandas to_datetime() 활용
  Refactor → 다양한 날짜 형식 지원

Cycle 3: 참여저자 처리 (세미콜론 구분)
  Red   → test_parse_co_authors() 작성
  Green → split(';') 처리 추가
  Refactor → 공백 제거

Cycle 4: NULL 허용 필드 처리
  Red   → test_parse_nullable_fields() 작성
  Green → fillna() 또는 None 유지
  Refactor → 없음

Cycle 5: 검증 및 저장
  Red   → test_parse_publication_validates_and_saves() 작성
  Green → Validator 호출 + bulk_create
  Refactor → 트랜잭션 추가
```

---

#### Phase 6: ResearchBudgetParser (6시간)

```
Cycle 1: CSV 컬럼 매핑 (복합 데이터)
  Red   → test_parse_research_budget_columns() 작성
  Green → parse() 메서드에서 컬럼명 매핑
  Refactor → 매핑 딕셔너리 상수화

Cycle 2: 과제 정보 추출 및 중복 제거
  Red   → test_extract_unique_projects() 작성
  Green → groupby('과제번호').first() 활용
  Refactor → 없음

Cycle 3: ResearchProject 저장 (UPSERT)
  Red   → test_save_research_projects() 작성
  Green → get_or_create() 또는 update_or_create() 사용
  Refactor → 트랜잭션 처리

Cycle 4: ExecutionRecord 저장
  Red   → test_save_execution_records() 작성
  Green → project FK 연결 후 bulk_create
  Refactor → 외래키 참조 최적화

Cycle 5: 과제번호 → project_id 매핑
  Red   → test_map_project_number_to_id() 작성
  Green → ResearchProject 조회 후 ID 매핑
  Refactor → 딕셔너리 캐싱

Cycle 6: 트랜잭션 원자성 보장
  Red   → test_transaction_rollback_on_error() 작성
  Green → @transaction.atomic 데코레이터 적용
  Refactor → 없음

Cycle 7: 검증 통합
  Red   → test_parse_research_budget_validates() 작성
  Green → Validator 호출 추가
  Refactor → 에러 메시지 개선
```

---

#### Phase 7: StudentParser (4시간)

```
Cycle 1: CSV 컬럼 매핑
  Red   → test_parse_student_columns() 작성
  Green → parse() 메서드에서 컬럼명 매핑
  Refactor → 매핑 딕셔너리 상수화

Cycle 2: 학년 타입 변환 (0 처리)
  Red   → test_parse_student_grade() 작성
  Green → astype(int) 처리
  Refactor → 0 (대학원) 확인

Cycle 3: 선택 필드 처리 (지도교수, 이메일)
  Red   → test_parse_optional_fields() 작성
  Green → fillna('') 또는 None 유지
  Refactor → 없음

Cycle 4: 검증 및 저장
  Red   → test_parse_student_validates_and_saves() 작성
  Green → Validator 호출 + bulk_create
  Refactor → 트랜잭션 추가
```

---

#### Phase 8: Django Admin 커스터마이징 (5시간)

```
Cycle 1: UploadHistory Admin 등록
  Red   → test_upload_history_admin_registered() 작성
  Green → UploadHistoryAdmin 클래스 생성 및 등록
  Refactor → list_display, list_filter 추가

Cycle 2: 파일 업로드 필드 추가 (InlineModelAdmin)
  Red   → test_admin_file_upload_field_exists() 작성
  Green → 각 모델 Admin에 file 필드 추가
  Refactor → help_text 추가

Cycle 3: save_model() 오버라이드
  Red   → test_save_model_triggers_parser() 작성
  Green → save_model()에서 파일 파싱 로직 호출
  Refactor → try-except 에러 처리

Cycle 4: 성공 메시지 표시
  Red   → test_admin_shows_success_message() 작성
  Green → self.message_user() 호출
  Refactor → 저장된 행 수 표시

Cycle 5: 실패 메시지 및 에러 로그
  Red   → test_admin_shows_error_message() 작성
  Green → ValidationError 발생 시 메시지 표시
  Refactor → UploadHistory에 에러 기록

Cycle 6: 업로드 이력 자동 기록
  Red   → test_admin_creates_upload_history() 작성
  Green → save_model()에서 UploadHistory 생성
  Refactor → 트랜잭션 처리
```

---

#### Phase 9: 업로드 후처리 Signal (2시간)

```
Cycle 1: post_save Signal 등록
  Red   → test_signal_triggers_on_save() 작성
  Green → @receiver(post_save) 데코레이터 사용
  Refactor → 없음

Cycle 2: 파일 파싱 트리거
  Red   → test_signal_calls_parser() 작성
  Green → signal handler에서 파서 호출
  Refactor → 조건 분기 (파일 존재 시만)

Cycle 3: UploadHistory 기록
  Red   → test_signal_creates_upload_history() 작성
  Green → UploadHistory.objects.create()
  Refactor → 중복 방지 (Admin에서 이미 생성 시)

Cycle 4: 비동기 처리 (선택적)
  Red   → test_signal_runs_async() 작성
  Green → Celery 태스크로 변환 (향후)
  Refactor → 현재는 동기 처리
```

---

## 3. 기능별 테스트 시나리오

### 3.1 UploadHistory 모델 테스트 (Unit Tests)

#### 테스트 파일: `apps/data_upload/tests/test_models.py`

```python
from django.test import TestCase
from apps.data_upload.models import UploadHistory
from apps.authentication.models import User


class UploadHistoryModelTest(TestCase):
    """UploadHistory 모델 단위 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.user = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )

    # Cycle 1
    def test_upload_history_creation(self):
        """
        Given: 필수 필드
        When: UploadHistory 생성
        Then: 정상 생성됨
        """
        # Arrange & Act
        history = UploadHistory.objects.create(
            user=self.user,
            file_name='test.xlsx',
            file_size=1024,
            data_type='department_kpi',
            status='success',
            rows_processed=10,
        )

        # Assert
        self.assertIsNotNone(history.id)
        self.assertEqual(history.file_name, 'test.xlsx')
        self.assertEqual(history.status, 'success')

    # Cycle 2
    def test_upload_history_user_relation(self):
        """
        Given: User FK
        When: UploadHistory 생성
        Then: User와 연결됨
        """
        # Arrange & Act
        history = UploadHistory.objects.create(
            user=self.user,
            file_name='test.xlsx',
            file_size=1024,
            data_type='department_kpi',
            status='success',
        )

        # Assert
        self.assertEqual(history.user.id, self.user.id)
        self.assertEqual(history.user.email, 'admin@university.ac.kr')

    # Cycle 3
    def test_get_successful_uploads(self):
        """
        Given: 여러 업로드 이력 (성공/실패)
        When: 성공한 이력만 조회
        Then: status='success'인 이력만 반환
        """
        # Arrange
        UploadHistory.objects.create(
            user=self.user,
            file_name='success1.xlsx',
            file_size=1024,
            data_type='department_kpi',
            status='success',
        )
        UploadHistory.objects.create(
            user=self.user,
            file_name='failed.xlsx',
            file_size=2048,
            data_type='publication',
            status='failed',
            error_message='Invalid data',
        )
        UploadHistory.objects.create(
            user=self.user,
            file_name='success2.xlsx',
            file_size=512,
            data_type='student',
            status='success',
        )

        # Act
        successful_uploads = UploadHistory.objects.filter(status='success')

        # Assert
        self.assertEqual(successful_uploads.count(), 2)

    # Cycle 4
    def test_get_recent_uploads(self):
        """
        Given: 여러 업로드 이력
        When: 최근 업로드 조회 (최신 5개)
        Then: upload_date 기준 최신순 5개 반환
        """
        # Arrange
        for i in range(10):
            UploadHistory.objects.create(
                user=self.user,
                file_name=f'file{i}.xlsx',
                file_size=1024,
                data_type='department_kpi',
                status='success',
            )

        # Act
        recent = UploadHistory.objects.all().order_by('-upload_date')[:5]

        # Assert
        self.assertEqual(recent.count(), 5)
        self.assertEqual(recent[0].file_name, 'file9.xlsx')
```

---

### 3.2 Validator 테스트 (Unit Tests)

#### 테스트 파일: `apps/data_upload/tests/test_validators.py`

```python
from django.test import TestCase
import pandas as pd
from apps.data_upload.validators import (
    validate_required_columns,
    validate_data_types,
    validate_department_kpi_data,
    validate_publication_data,
    validate_research_budget_data,
    validate_student_data,
)
from apps.core.exceptions import DataValidationError


class CommonValidatorTest(TestCase):
    """공통 Validator 단위 테스트"""

    # Cycle 1
    def test_validate_required_columns(self):
        """
        Given: 필수 컬럼이 누락된 DataFrame
        When: validate_required_columns() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': ['a', 'b'],
        })
        required = ['col1', 'col2', 'col3']

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_required_columns(df, required)

        self.assertIn('col3', str(context.exception))

    def test_validate_required_columns_success(self):
        """
        Given: 모든 필수 컬럼이 존재하는 DataFrame
        When: validate_required_columns() 호출
        Then: 에러 없음
        """
        # Arrange
        df = pd.DataFrame({
            'col1': [1, 2],
            'col2': ['a', 'b'],
            'col3': [3.0, 4.0],
        })
        required = ['col1', 'col2', 'col3']

        # Act & Assert
        # 에러 발생하지 않아야 함
        validate_required_columns(df, required)

    # Cycle 2
    def test_validate_data_types(self):
        """
        Given: 잘못된 데이터 타입의 DataFrame
        When: validate_data_types() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            'year': ['2025', '2024'],  # 문자열 (int 기대)
            'rate': [88.5, 90.0],
        })
        type_map = {
            'year': int,
            'rate': float,
        }

        # Act & Assert
        with self.assertRaises(DataValidationError):
            validate_data_types(df, type_map)


class DepartmentKPIValidatorTest(TestCase):
    """DepartmentKPI Validator 단위 테스트"""

    # Cycle 1
    def test_validate_department_kpi_schema(self):
        """
        Given: 올바른 스키마의 KPI 데이터
        When: validate_department_kpi_data() 호출
        Then: 에러 없음
        """
        # Arrange
        df = pd.DataFrame({
            '평가년도': [2025, 2025],
            '단과대학': ['공과대학', '인문대학'],
            '학과': ['컴퓨터공학과', '영어영문학과'],
            '졸업생 취업률 (%)': [88.5, 85.0],
            '전임교원 수 (명)': [17, 15],
            '초빙교원 수 (명)': [5, 3],
            '연간 기술이전 수입액 (억원)': [13.5, 10.0],
            '국제학술대회 개최 횟수': [4, 2],
        })

        # Act & Assert
        # 에러 발생하지 않아야 함
        validate_department_kpi_data(df)

    # Cycle 2
    def test_employment_rate_range(self):
        """
        Given: 취업률이 100% 초과
        When: validate_department_kpi_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '평가년도': [2025],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [105.0],  # 100 초과
            '전임교원 수 (명)': [17],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_department_kpi_data(df)

        self.assertIn('취업률', str(context.exception))
        self.assertIn('100', str(context.exception))

    # Cycle 3
    def test_negative_values_rejected(self):
        """
        Given: 음수 값 (교원 수)
        When: validate_department_kpi_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '평가년도': [2025],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [88.5],
            '전임교원 수 (명)': [-5],  # 음수
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_department_kpi_data(df)

        self.assertIn('음수', str(context.exception))

    # Cycle 4
    def test_evaluation_year_range(self):
        """
        Given: 유효하지 않은 평가년도 (1999)
        When: validate_department_kpi_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '평가년도': [1999],  # 2000 미만
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [88.5],
            '전임교원 수 (명)': [17],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_department_kpi_data(df)

        self.assertIn('평가년도', str(context.exception))


class PublicationValidatorTest(TestCase):
    """Publication Validator 단위 테스트"""

    # Cycle 2
    def test_publication_id_uniqueness(self):
        """
        Given: 중복된 논문ID
        When: validate_publication_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '논문ID': ['PUB-25-001', 'PUB-25-001'],  # 중복
            '게재일': ['2025-06-15', '2025-07-20'],
            '단과대학': ['공과대학', '공과대학'],
            '학과': ['컴퓨터공학과', '컴퓨터공학과'],
            '논문제목': ['Paper 1', 'Paper 2'],
            '주저자': ['Author A', 'Author B'],
            '참여저자': ['', ''],
            '학술지명': ['Journal A', 'Journal B'],
            '저널등급': ['SCIE', 'KCI'],
            'Impact Factor': [10.6, None],
            '과제연계여부': ['Y', 'N'],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_publication_data(df)

        self.assertIn('중복', str(context.exception))

    # Cycle 3
    def test_journal_grade_validation(self):
        """
        Given: 유효하지 않은 저널 등급
        When: validate_publication_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '논문ID': ['PUB-25-001'],
            '게재일': ['2025-06-15'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '논문제목': ['Paper 1'],
            '주저자': ['Author A'],
            '참여저자': [''],
            '학술지명': ['Journal A'],
            '저널등급': ['INVALID'],  # 유효하지 않은 등급
            'Impact Factor': [10.6],
            '과제연계여부': ['Y'],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_publication_data(df)

        self.assertIn('저널등급', str(context.exception))


class ResearchBudgetValidatorTest(TestCase):
    """ResearchBudget Validator 단위 테스트"""

    # Cycle 3
    def test_total_budget_positive(self):
        """
        Given: 총연구비가 0 이하
        When: validate_research_budget_data() 호출
        Then: DataValidationError 발생
        """
        # Arrange
        df = pd.DataFrame({
            '집행ID': ['T2301001'],
            '과제번호': ['NRF-2023-015'],
            '과제명': ['AI 연구'],
            '연구책임자': ['이서연'],
            '소속학과': ['컴퓨터공학과'],
            '지원기관': ['한국연구재단'],
            '총연구비': [0],  # 0 이하
            '집행일자': ['2023-03-15'],
            '집행항목': ['연구장비 도입'],
            '집행금액': [30000000],
            '상태': ['집행완료'],
            '비고': [''],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_research_budget_data(df)

        self.assertIn('총연구비', str(context.exception))

    # Cycle 6
    def test_execution_not_exceeds_budget(self):
        """
        Given: 과제의 집행금액 합계가 총연구비 초과
        When: validate_research_budget_data() 호출
        Then: DataValidationError 또는 경고
        """
        # Arrange
        df = pd.DataFrame({
            '집행ID': ['T2301001', 'T2301002'],
            '과제번호': ['NRF-2023-015', 'NRF-2023-015'],
            '과제명': ['AI 연구', 'AI 연구'],
            '연구책임자': ['이서연', '이서연'],
            '소속학과': ['컴퓨터공학과', '컴퓨터공학과'],
            '지원기관': ['한국연구재단', '한국연구재단'],
            '총연구비': [100000000, 100000000],
            '집행일자': ['2023-03-15', '2023-05-20'],
            '집행항목': ['연구장비 도입', '인건비'],
            '집행금액': [70000000, 50000000],  # 합계 120000000 > 100000000
            '상태': ['집행완료', '집행완료'],
            '비고': ['', ''],
        })

        # Act & Assert
        with self.assertRaises(DataValidationError) as context:
            validate_research_budget_data(df)

        self.assertIn('초과', str(context.exception))
```

---

### 3.3 Parser 테스트 (Unit Tests)

#### 테스트 파일: `apps/data_upload/tests/test_parsers.py`

```python
from django.test import TestCase
import pandas as pd
import os
from apps.data_upload.parsers import (
    BaseParser,
    DepartmentKPIParser,
    PublicationParser,
    ResearchBudgetParser,
    StudentParser,
)
from apps.core.exceptions import InvalidFileFormatError, DataValidationError


class BaseParserTest(TestCase):
    """BaseParser 단위 테스트"""

    # Cycle 1
    def test_base_parser_reads_file(self):
        """
        Given: 유효한 Excel 파일
        When: read_file() 호출
        Then: DataFrame 반환
        """
        # Arrange
        # 테스트용 임시 파일 생성
        df_sample = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        test_file_path = '/tmp/test.xlsx'
        df_sample.to_excel(test_file_path, index=False)

        parser = DepartmentKPIParser()  # 구체 클래스 사용

        # Act
        df = parser.read_file(test_file_path)

        # Assert
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)

        # Cleanup
        os.remove(test_file_path)

    # Cycle 2
    def test_validate_file_extension(self):
        """
        Given: 유효하지 않은 확장자 (.txt)
        When: validate_extension() 호출
        Then: InvalidFileFormatError 발생
        """
        # Arrange
        parser = DepartmentKPIParser()

        # Act & Assert
        with self.assertRaises(InvalidFileFormatError):
            parser.validate_extension('test.txt')

    def test_validate_file_extension_success(self):
        """
        Given: 유효한 확장자 (.xlsx)
        When: validate_extension() 호출
        Then: 에러 없음
        """
        # Arrange
        parser = DepartmentKPIParser()

        # Act & Assert
        # 에러 발생하지 않아야 함
        parser.validate_extension('test.xlsx')

    # Cycle 3
    def test_validate_file_size(self):
        """
        Given: 파일 크기가 50MB 초과
        When: validate_size() 호출
        Then: FileSizeLimitExceededError 발생
        """
        # Arrange
        parser = DepartmentKPIParser()
        large_size = 60 * 1024 * 1024  # 60MB

        # Act & Assert
        from apps.core.exceptions import FileSizeLimitExceededError
        with self.assertRaises(FileSizeLimitExceededError):
            parser.validate_size(large_size)


class DepartmentKPIParserTest(TestCase):
    """DepartmentKPIParser 단위 테스트"""

    # Cycle 1
    def test_parse_department_kpi_columns(self):
        """
        Given: 한글 컬럼명 CSV
        When: parse() 호출
        Then: 영문 컬럼명으로 매핑됨
        """
        # Arrange
        df_sample = pd.DataFrame({
            '평가년도': [2025],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [88.5],
            '전임교원 수 (명)': [17],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })
        test_file = '/tmp/test_kpi.xlsx'
        df_sample.to_excel(test_file, index=False)

        parser = DepartmentKPIParser()

        # Act
        result = parser.parse(test_file)

        # Assert
        self.assertTrue(result['success'])
        self.assertIn('evaluation_year', result['data'].columns)

        # Cleanup
        os.remove(test_file)

    # Cycle 5
    def test_save_to_db_bulk_create(self):
        """
        Given: 파싱된 DataFrame
        When: save_to_db() 호출
        Then: bulk_create로 DB에 저장됨
        """
        # Arrange
        from apps.analytics.models import DepartmentKPI

        df = pd.DataFrame({
            'evaluation_year': [2025],
            'college': ['공과대학'],
            'department': ['컴퓨터공학과'],
            'employment_rate': [88.5],
            'full_time_faculty': [17],
            'visiting_faculty': [5],
            'tech_transfer_income': [13.5],
            'intl_conference_count': [4],
        })

        parser = DepartmentKPIParser()

        # Act
        parser.save_to_db(df)

        # Assert
        self.assertEqual(DepartmentKPI.objects.count(), 1)
        kpi = DepartmentKPI.objects.first()
        self.assertEqual(kpi.department, '컴퓨터공학과')
        self.assertEqual(kpi.employment_rate, 88.5)


class ResearchBudgetParserTest(TestCase):
    """ResearchBudgetParser 단위 테스트 (복잡한 케이스)"""

    # Cycle 2
    def test_extract_unique_projects(self):
        """
        Given: 여러 집행 내역이 포함된 CSV
        When: 과제 정보 추출
        Then: 중복 제거된 과제 리스트 반환
        """
        # Arrange
        df = pd.DataFrame({
            '집행ID': ['T2301001', 'T2301002', 'T2302001'],
            '과제번호': ['NRF-2023-015', 'NRF-2023-015', 'NRF-2023-016'],
            '과제명': ['AI 연구', 'AI 연구', '바이오 연구'],
            '연구책임자': ['이서연', '이서연', '정현우'],
            '소속학과': ['컴퓨터공학과', '컴퓨터공학과', '생명공학과'],
            '지원기관': ['한국연구재단', '한국연구재단', '과기부'],
            '총연구비': [100000000, 100000000, 50000000],
            '집행일자': ['2023-03-15', '2023-05-20', '2023-04-10'],
            '집행항목': ['연구장비 도입', '인건비', '시약 구매'],
            '집행금액': [30000000, 20000000, 10000000],
            '상태': ['집행완료', '집행완료', '집행완료'],
            '비고': ['', '', ''],
        })

        parser = ResearchBudgetParser()

        # Act
        projects = parser.extract_unique_projects(df)

        # Assert
        self.assertEqual(len(projects), 2)
        self.assertIn('NRF-2023-015', projects['project_number'].values)
        self.assertIn('NRF-2023-016', projects['project_number'].values)

    # Cycle 6
    def test_transaction_rollback_on_error(self):
        """
        Given: 검증 실패하는 데이터
        When: parse() 호출
        Then: 트랜잭션 롤백, DB에 저장 안 됨
        """
        # Arrange
        from apps.analytics.models import ResearchProject, ExecutionRecord

        df_sample = pd.DataFrame({
            '집행ID': ['T2301001'],
            '과제번호': ['NRF-2023-015'],
            '과제명': ['AI 연구'],
            '연구책임자': ['이서연'],
            '소속학과': ['컴퓨터공학과'],
            '지원기관': ['한국연구재단'],
            '총연구비': [-100],  # 음수 (검증 실패)
            '집행일자': ['2023-03-15'],
            '집행항목': ['연구장비 도입'],
            '집행금액': [30000000],
            '상태': ['집행완료'],
            '비고': [''],
        })
        test_file = '/tmp/test_budget.xlsx'
        df_sample.to_excel(test_file, index=False)

        parser = ResearchBudgetParser()

        # Act
        result = parser.parse(test_file)

        # Assert
        self.assertFalse(result['success'])
        self.assertEqual(ResearchProject.objects.count(), 0)
        self.assertEqual(ExecutionRecord.objects.count(), 0)

        # Cleanup
        os.remove(test_file)
```

---

### 3.4 Django Admin 통합 테스트 (Integration Tests)

#### 테스트 파일: `apps/data_upload/tests/test_admin.py`

```python
from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from apps.data_upload.admin import UploadHistoryAdmin, DepartmentKPIAdmin
from apps.data_upload.models import UploadHistory
from apps.analytics.models import DepartmentKPI
from apps.authentication.models import User
import pandas as pd
import os


class DepartmentKPIAdminTest(TestCase):
    """DepartmentKPI Admin 통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.site = AdminSite()
        self.admin = DepartmentKPIAdmin(DepartmentKPI, self.site)

        self.user = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
            is_staff=True,
            is_superuser=True,
        )

    # Cycle 1
    def test_upload_history_admin_registered(self):
        """
        Given: UploadHistory 모델
        When: Admin site 조회
        Then: UploadHistoryAdmin 등록됨
        """
        # Arrange & Act
        from django.contrib import admin

        # Assert
        self.assertIn(UploadHistory, admin.site._registry)

    # Cycle 3
    def test_save_model_triggers_parser(self):
        """
        Given: 파일이 업로드된 모델 인스턴스
        When: save_model() 호출
        Then: 파서가 실행되고 데이터 저장됨
        """
        # Arrange
        df_sample = pd.DataFrame({
            '평가년도': [2025],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [88.5],
            '전임교원 수 (명)': [17],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })
        test_file = '/tmp/test_kpi_admin.xlsx'
        df_sample.to_excel(test_file, index=False)

        # Django UploadedFile 시뮬레이션
        from django.core.files.uploadedfile import SimpleUploadedFile
        with open(test_file, 'rb') as f:
            file_content = f.read()

        uploaded_file = SimpleUploadedFile(
            name='test_kpi_admin.xlsx',
            content=file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        obj = DepartmentKPI(file=uploaded_file)

        # Mock request
        class MockRequest:
            user = self.user

        request = MockRequest()

        # Act
        self.admin.save_model(request, obj, None, None)

        # Assert
        self.assertEqual(DepartmentKPI.objects.count(), 1)

        # Cleanup
        os.remove(test_file)

    # Cycle 6
    def test_admin_creates_upload_history(self):
        """
        Given: 파일 업로드 성공
        When: save_model() 호출
        Then: UploadHistory 자동 생성됨
        """
        # Arrange
        df_sample = pd.DataFrame({
            '평가년도': [2025],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [88.5],
            '전임교원 수 (명)': [17],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })
        test_file = '/tmp/test_kpi_history.xlsx'
        df_sample.to_excel(test_file, index=False)

        from django.core.files.uploadedfile import SimpleUploadedFile
        with open(test_file, 'rb') as f:
            file_content = f.read()

        uploaded_file = SimpleUploadedFile(
            name='test_kpi_history.xlsx',
            content=file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        obj = DepartmentKPI(file=uploaded_file)

        class MockRequest:
            user = self.user

        request = MockRequest()

        # Act
        self.admin.save_model(request, obj, None, None)

        # Assert
        self.assertEqual(UploadHistory.objects.count(), 1)
        history = UploadHistory.objects.first()
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.status, 'success')
        self.assertEqual(history.data_type, 'department_kpi')

        # Cleanup
        os.remove(test_file)
```

---

### 3.5 Acceptance Tests (End-to-End)

#### 테스트 파일: `apps/data_upload/tests/test_acceptance.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User
from apps.analytics.models import DepartmentKPI, Publication
from apps.data_upload.models import UploadHistory
import pandas as pd
import os


class DataUploadAcceptanceTest(TestCase):
    """데이터 업로드 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()

    def test_full_upload_flow_department_kpi(self):
        """
        Scenario: 관리자 로그인 → Django Admin 접근 → KPI 파일 업로드 → 검증 → 저장 → 이력 기록
        Given: 관리자 계정
        When: 파일 업로드
        Then: 데이터 저장 및 이력 기록
        """
        # Step 1: 관리자 생성
        admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
            is_staff=True,
            is_superuser=True,
        )
        admin.set_password('admin1234')
        admin.save()

        # Step 2: 로그인
        login_successful = self.client.login(
            username='admin@university.ac.kr',
            password='admin1234'
        )
        self.assertTrue(login_successful)

        # Step 3: 테스트 파일 생성
        df_sample = pd.DataFrame({
            '평가년도': [2025, 2025],
            '단과대학': ['공과대학', '인문대학'],
            '학과': ['컴퓨터공학과', '영어영문학과'],
            '졸업생 취업률 (%)': [88.5, 85.0],
            '전임교원 수 (명)': [17, 15],
            '초빙교원 수 (명)': [5, 3],
            '연간 기술이전 수입액 (억원)': [13.5, 10.0],
            '국제학술대회 개최 횟수': [4, 2],
        })
        test_file = '/tmp/test_kpi_acceptance.xlsx'
        df_sample.to_excel(test_file, index=False)

        # Step 4: Django Admin에서 파일 업로드 (시뮬레이션)
        # (실제 파일 업로드는 브라우저를 통해 이루어지므로, parser 직접 호출)
        from apps.data_upload.parsers import DepartmentKPIParser
        parser = DepartmentKPIParser()
        result = parser.parse(test_file)

        # Step 5: 검증
        self.assertTrue(result['success'])
        self.assertEqual(DepartmentKPI.objects.count(), 2)

        # Step 6: 업로드 이력 기록 확인
        # (실제로는 Admin save_model에서 자동 기록, 여기서는 수동 생성)
        UploadHistory.objects.create(
            user=admin,
            file_name='test_kpi_acceptance.xlsx',
            file_size=os.path.getsize(test_file),
            data_type='department_kpi',
            status='success',
            rows_processed=2,
        )

        history = UploadHistory.objects.first()
        self.assertEqual(history.status, 'success')
        self.assertEqual(history.rows_processed, 2)

        # Cleanup
        os.remove(test_file)

    def test_upload_validation_failure_flow(self):
        """
        Scenario: 잘못된 데이터 업로드 → 검증 실패 → 에러 메시지 → 이력 기록 (failed)
        Given: 유효하지 않은 데이터 파일
        When: 업로드 시도
        Then: 검증 실패, 에러 기록
        """
        # Step 1: 관리자 생성 및 로그인
        admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
            is_staff=True,
            is_superuser=True,
        )

        # Step 2: 잘못된 데이터 파일 생성
        df_invalid = pd.DataFrame({
            '평가년도': [1999],  # 유효하지 않은 연도
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [105.0],  # 100 초과
            '전임교원 수 (명)': [-5],  # 음수
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [13.5],
            '국제학술대회 개최 횟수': [4],
        })
        test_file = '/tmp/test_kpi_invalid.xlsx'
        df_invalid.to_excel(test_file, index=False)

        # Step 3: 파일 업로드 시도
        from apps.data_upload.parsers import DepartmentKPIParser
        parser = DepartmentKPIParser()
        result = parser.parse(test_file)

        # Step 4: 검증 실패 확인
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(DepartmentKPI.objects.count(), 0)

        # Step 5: 업로드 이력 기록 (실패)
        UploadHistory.objects.create(
            user=admin,
            file_name='test_kpi_invalid.xlsx',
            file_size=os.path.getsize(test_file),
            data_type='department_kpi',
            status='failed',
            error_message=result['error'],
        )

        history = UploadHistory.objects.first()
        self.assertEqual(history.status, 'failed')
        self.assertIsNotNone(history.error_message)

        # Cleanup
        os.remove(test_file)
```

---

## 4. AAA 패턴 적용 예제

### 4.1 Validator 테스트 (AAA)

```python
def test_validate_employment_rate_range(self):
    """
    Given: 취업률이 100% 초과하는 데이터
    When: 검증 함수 호출
    Then: DataValidationError 발생
    """
    # Arrange (준비)
    # 1. 잘못된 데이터 준비
    df = pd.DataFrame({
        '평가년도': [2025],
        '단과대학': ['공과대학'],
        '학과': ['컴퓨터공학과'],
        '졸업생 취업률 (%)': [105.0],  # 100 초과
        # ... 기타 필드
    })

    # Act (실행)
    # 검증 함수 호출
    with self.assertRaises(DataValidationError) as context:
        validate_department_kpi_data(df)

    # Assert (검증)
    # 1. 에러 메시지 확인
    self.assertIn('취업률', str(context.exception))
    self.assertIn('100', str(context.exception))
```

---

## 5. FIRST 원칙 적용

### 5.1 Fast (빠른 테스트)
- Validator 테스트: 각 10ms 이하
- Parser 테스트: 각 100ms 이하 (파일 I/O 포함)
- Admin 통합 테스트: 각 300ms 이하

### 5.2 Independent (독립적)
```python
class IndependentParserTest(TestCase):
    def setUp(self):
        """각 테스트마다 독립적으로 실행"""
        # 임시 파일 생성
        self.test_file = self.create_temp_file()

    def tearDown(self):
        """테스트 후 정리"""
        # 임시 파일 삭제
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_parser_a(self):
        """독립적 테스트 A"""
        pass

    def test_parser_b(self):
        """독립적 테스트 B (test_parser_a와 무관)"""
        pass
```

### 5.3 Repeatable (반복 가능)
- 고정된 테스트 데이터 사용
- 임시 파일 경로 고정 (/tmp/test_*.xlsx)
- DB 트랜잭션 롤백 보장

### 5.4 Self-validating (자가 검증)
```python
def test_parser_saves_correct_data(self):
    """파서가 올바른 데이터를 저장하는지 검증 (자가 검증)"""
    # Arrange
    # ... 파일 생성

    # Act
    result = parser.parse(test_file)

    # Assert
    # 명확한 검증
    self.assertTrue(result['success'], "파싱이 성공해야 함")
    self.assertEqual(DepartmentKPI.objects.count(), 2, "2개의 KPI 데이터가 저장되어야 함")
    kpi = DepartmentKPI.objects.first()
    self.assertEqual(kpi.employment_rate, 88.5, "취업률이 88.5%여야 함")
```

### 5.5 Timely (적시성)
- 코드 작성 전 테스트 먼저 작성
- Red → Green → Refactor 사이클 준수

---

## 6. 테스트 실행 계획

### 6.1 테스트 실행 명령어

```bash
# 전체 data_upload 테스트 실행
python manage.py test apps.data_upload

# Unit 테스트만 실행
python manage.py test apps.data_upload.tests.test_validators
python manage.py test apps.data_upload.tests.test_parsers

# Integration 테스트만 실행
python manage.py test apps.data_upload.tests.test_admin

# Acceptance 테스트만 실행
python manage.py test apps.data_upload.tests.test_acceptance

# 코드 커버리지 측정
coverage run --source='apps.data_upload' manage.py test apps.data_upload
coverage report
coverage html
```

### 6.2 테스트 실행 시간 예상

| 테스트 유형 | 개수 | 예상 시간 | 비고 |
|------------|------|----------|------|
| Unit (Validator) | 30 | 1초 | 빠른 검증 로직 |
| Unit (Parser) | 40 | 6초 | 파일 I/O 포함 |
| Integration (Admin) | 20 | 8초 | DB + 파일 처리 |
| Acceptance | 8 | 5초 | 전체 플로우 |
| **총합** | **98** | **20초** | 충분히 빠름 |

---

## 7. 커밋 전략

### 7.1 작은 단위 커밋

```bash
# Phase 2 Cycle 1 완료 후
git add apps/data_upload/validators.py apps/data_upload/tests/test_validators.py
git commit -m "test: 필수 컬럼 검증 로직 테스트 및 구현

- Red: test_validate_required_columns() 작성
- Green: validate_required_columns() 함수 구현
- Refactor: 에러 메시지 개선
"

# Phase 4 Cycle 5 완료 후
git add apps/data_upload/parsers.py apps/data_upload/tests/test_parsers.py
git commit -m "test: DepartmentKPIParser bulk_create 테스트 및 구현

- Red: test_save_to_db_bulk_create() 작성
- Green: save_to_db() 메서드에서 bulk_create() 호출
- Refactor: batch_size 최적화 (1000)
"
```

---

## 8. 체크리스트

### 8.1 각 Cycle 완료 시
- [ ] Red: 실패하는 테스트 작성
- [ ] 테스트 실행하여 실패 확인
- [ ] Green: 최소한의 코드로 통과
- [ ] 테스트 실행하여 성공 확인
- [ ] Refactor: 코드 개선
- [ ] 모든 테스트 재실행
- [ ] 커밋

### 8.2 Phase 완료 시
- [ ] 해당 Phase 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상
- [ ] 파일 I/O 에러 처리 확인
- [ ] 트랜잭션 롤백 동작 확인
- [ ] 문서 업데이트
- [ ] 다음 Phase 진행

### 8.3 전체 완료 시
- [ ] 모든 테스트 통과 (Unit + Integration + Acceptance)
- [ ] 코드 커버리지 85% 이상
- [ ] Django Admin UI 수동 테스트
- [ ] 대용량 파일 업로드 성능 테스트
- [ ] 보안 검토 (파일 검증, 권한 체크)
- [ ] Pull Request 생성

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성<br>- 데이터 업로드 TDD 구현 계획<br>- 98개 테스트 시나리오<br>- Validator, Parser, Admin 테스트<br>- 4개 데이터 타입 파서 구현 계획 | Claude Code |

---

## 10. 참고 문서

- [TDD 가이드라인](/Users/seunghyun/Test/vmc6/docs/tdd.md)
- [Database Schema](/Users/seunghyun/Test/vmc6/docs/database.md)
- [UC-03: 데이터 업로드](/Users/seunghyun/Test/vmc6/docs/usecases/03-data-upload/spec.md)
- [UC-12: 업로드 이력](/Users/seunghyun/Test/vmc6/docs/usecases/12-upload-history/spec.md)
- [공통 모듈 문서](/Users/seunghyun/Test/vmc6/docs/common-modules.md)

---

**문서 작성 완료**
**다음 작업**: Phase 1 (UploadHistory 모델) 구현 시작
