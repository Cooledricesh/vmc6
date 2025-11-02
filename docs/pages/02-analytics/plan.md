# TDD 기반 구현 계획: 대시보드 및 시각화 페이지
## University Data Visualization Dashboard

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 1.0
- **대상 기능**: 대시보드, KPI/논문/연구비/학생 시각화
- **관련 Use Cases**: UC-04 (대시보드), UC-05~08 (시각화 페이지)
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
          /____\  - 사용자 시나리오 테스트
         /      \  - End-to-End 플로우
        / Integ. \ Integration Tests (20%)
       /__________\ - 뷰 + Aggregator + DB
      /            \ - Chart.js 데이터 포맷
     /    Unit      \ Unit Tests (70%)
    /________________\ - Aggregator, Serializer, Filter
```

**예상 테스트 케이스 수:**
- Unit Tests: ~60개 (Aggregator 30, Serializer 15, Filter 15)
- Integration Tests: ~25개 (각 페이지당 5개)
- Acceptance Tests: ~8개 (전체 플로우 2개 × 4 페이지)
- **총 예상**: ~93개 테스트

---

## 2. 구현 우선순위 및 순서

### 2.1 우선순위 (높음 → 낮음)

| 우선순위 | 기능 | 이유 | 예상 소요 시간 |
|---------|------|------|--------------|
| 1 | 데이터 Aggregator | 모든 시각화의 핵심 | 6시간 |
| 2 | Chart.js Serializer | 차트 렌더링 필수 | 4시간 |
| 3 | 필터링 로직 | 사용자 경험 핵심 | 3시간 |
| 4 | 대시보드 뷰 | 전체 KPI 요약 | 4시간 |
| 5 | 학과별 KPI 시각화 | 핵심 지표 | 4시간 |
| 6 | 논문 시각화 | 연구 성과 | 4시간 |
| 7 | 연구비 시각화 | 재정 투명성 | 4시간 |
| 8 | 학생 시각화 | 학사 관리 | 4시간 |

**총 예상 시간**: 33시간 (4~5일)

---

### 2.2 개발 순서 (TDD 사이클별)

#### Phase 1: 데이터 Aggregator (6시간)

##### 1.1 DepartmentKPIAggregator
```
Cycle 1: 기본 집계 - 평균 취업률
  Red   → test_get_average_employment_rate() 작성
  Green → get_average_employment_rate() 메서드 구현
  Refactor → 쿼리 최적화 (aggregate 사용)

Cycle 2: 학과별 집계
  Red   → test_get_kpi_by_department() 작성
  Green → get_kpi_by_department(departments) 구현
  Refactor → 필터링 로직 함수로 분리

Cycle 3: 연도별 추이
  Red   → test_get_kpi_trend_by_year() 작성
  Green → get_kpi_trend_by_year(years) 구현
  Refactor → 윈도우 함수 활용

Cycle 4: 단과대학별 비교
  Red   → test_get_kpi_by_college() 작성
  Green → get_kpi_by_college() 구현
  Refactor → DRY 원칙 적용
```

##### 1.2 PublicationAggregator
```
Cycle 1: 총 논문 수 집계
  Red   → test_get_total_publication_count() 작성
  Green → get_total_publication_count() 구현
  Refactor → 없음

Cycle 2: 저널 등급별 분포
  Red   → test_get_publications_by_journal_grade() 작성
  Green → get_publications_by_journal_grade() 구현
  Refactor → 상수 정의 분리

Cycle 3: 평균 Impact Factor
  Red   → test_get_average_impact_factor() 작성
  Green → get_average_impact_factor(journal_grade=None) 구현
  Refactor → NULL 처리 개선

Cycle 4: 주저자별 통계
  Red   → test_get_publications_by_first_author() 작성
  Green → get_publications_by_first_author(limit=10) 구현
  Refactor → Pagination 고려
```

##### 1.3 ResearchBudgetAggregator
```
Cycle 1: 총 연구비 및 집행금액
  Red   → test_get_total_budget_and_execution() 작성
  Green → get_total_budget_and_execution() 구현
  Refactor → 뷰 활용 (v_project_execution_rate)

Cycle 2: 학과별 연구비 집계
  Red   → test_get_budget_by_department() 작성
  Green → get_budget_by_department() 구현
  Refactor → 쿼리 최적화

Cycle 3: 집행항목별 분포
  Red   → test_get_execution_by_category() 작성
  Green → get_execution_by_category() 구현
  Refactor → 정규화 함수 추가

Cycle 4: 집행률 계산
  Red   → test_get_execution_rate_by_project() 작성
  Green → get_execution_rate_by_project() 구현
  Refactor → CASE WHEN 활용
```

##### 1.4 StudentAggregator
```
Cycle 1: 총 학생 수 및 재학률
  Red   → test_get_total_students_and_enrollment_rate() 작성
  Green → get_total_students_and_enrollment_rate() 구현
  Refactor → 뷰 활용 (v_department_student_stats)

Cycle 2: 학년별 분포
  Red   → test_get_students_by_grade() 작성
  Green → get_students_by_grade() 구현
  Refactor → 없음

Cycle 3: 학과별 학생 수
  Red   → test_get_students_by_department() 작성
  Green → get_students_by_department() 구현
  Refactor → 정렬 옵션 추가

Cycle 4: 입학년도별 추이
  Red   → test_get_students_by_admission_year() 작성
  Green → get_students_by_admission_year(years) 구현
  Refactor → 쿼리 최적화
```

---

#### Phase 2: Chart.js Serializer (4시간)

```
Cycle 1: 막대 그래프 데이터 변환
  Red   → test_to_bar_chart_data() 작성
  Green → to_bar_chart_data(queryset, label, value) 구현
  Refactor → 색상 팔레트 적용

Cycle 2: 라인 차트 데이터 변환
  Red   → test_to_line_chart_data() 작성
  Green → to_line_chart_data(queryset, x, y) 구현
  Refactor → 다중 시리즈 지원

Cycle 3: 파이 차트 데이터 변환
  Red   → test_to_pie_chart_data() 작성
  Green → to_pie_chart_data(queryset, label, value) 구현
  Refactor → 비율 계산 추가

Cycle 4: 다중 데이터셋 차트
  Red   → test_to_multi_dataset_chart_data() 작성
  Green → to_multi_dataset_chart_data() 구현
  Refactor → 범용성 개선

Cycle 5: 듀얼 축 차트 (연구비용)
  Red   → test_to_dual_axis_chart_data() 작성
  Green → to_dual_axis_chart_data() 구현
  Refactor → 차트 옵션 포함
```

---

#### Phase 3: 필터링 로직 (3시간)

```
Cycle 1: 날짜 범위 필터
  Red   → test_filter_by_date_range() 작성
  Green → filter_by_date_range(qs, start, end) 구현
  Refactor → NULL 처리 추가

Cycle 2: 학과 필터
  Red   → test_filter_by_department() 작성
  Green → filter_by_department(qs, depts) 구현
  Refactor → 리스트 입력 지원

Cycle 3: 단과대학 필터
  Red   → test_filter_by_college() 작성
  Green → filter_by_college(qs, colleges) 구현
  Refactor → 없음

Cycle 4: 권한별 필터링
  Red   → test_apply_user_permission_filter() 작성
  Green → apply_user_permission_filter(qs, user) 구현
  Refactor → permissions.py와 통합

Cycle 5: 다중 필터 조합
  Red   → test_apply_multiple_filters() 작성
  Green → apply_multiple_filters(qs, filters) 구현
  Refactor → 빌더 패턴 적용
```

---

#### Phase 4: 대시보드 뷰 (4시간)

```
Cycle 1: 대시보드 기본 렌더링
  Red   → test_dashboard_view_renders_template() 작성
  Green → dashboard_view() 함수 구현 (GET)
  Refactor → 없음

Cycle 2: KPI 요약 카드 데이터
  Red   → test_dashboard_view_includes_kpi_summary() 작성
  Green → 각 Aggregator 호출하여 요약 데이터 생성
  Refactor → 중복 코드 제거

Cycle 3: 권한별 데이터 필터링
  Red   → test_dashboard_view_filters_by_user_role() 작성
  Green → apply_user_permission_filter() 호출
  Refactor → 데코레이터 적용

Cycle 4: 최근 업데이트 정보
  Red   → test_dashboard_view_shows_recent_uploads() 작성
  Green → UploadHistory 쿼리 추가
  Refactor → 쿼리 최적화

Cycle 5: 주요 추이 그래프 데이터
  Red   → test_dashboard_view_includes_trend_charts() 작성
  Green → Serializer 호출하여 차트 데이터 생성
  Refactor → 템플릿 컨텍스트 정리
```

---

#### Phase 5: 학과별 KPI 시각화 (4시간)

```
Cycle 1: KPI 페이지 기본 렌더링
  Red   → test_department_kpi_view_renders_template() 작성
  Green → department_kpi_view() 함수 구현
  Refactor → 없음

Cycle 2: 필터 파라미터 처리
  Red   → test_department_kpi_view_applies_filters() 작성
  Green → 쿼리 파라미터 파싱 및 필터 적용
  Refactor → 기본값 설정

Cycle 3: 학과별 취업률 차트
  Red   → test_department_kpi_view_employment_rate_chart() 작성
  Green → DepartmentKPIAggregator + Serializer 호출
  Refactor → 템플릿에 데이터 전달

Cycle 4: 연도별 추이 차트
  Red   → test_department_kpi_view_trend_chart() 작성
  Green → 추이 데이터 생성 및 직렬화
  Refactor → 없음

Cycle 5: 권한별 접근 제어
  Red   → test_department_kpi_view_viewer_sees_own_dept() 작성
  Green → 권한 체크 및 필터링 추가
  Refactor → 데코레이터 활용
```

---

#### Phase 6: 논문 시각화 (4시간)

```
Cycle 1: 논문 페이지 기본 렌더링
  Red   → test_publications_view_renders_template() 작성
  Green → publications_view() 함수 구현
  Refactor → 없음

Cycle 2: 저널 등급별 분포 파이 차트
  Red   → test_publications_view_journal_grade_pie_chart() 작성
  Green → PublicationAggregator + to_pie_chart_data() 호출
  Refactor → 색상 매핑 추가

Cycle 3: 학과별 논문 수 막대 그래프
  Red   → test_publications_view_department_bar_chart() 작성
  Green → 학과별 집계 + to_bar_chart_data() 호출
  Refactor → 정렬 옵션 추가

Cycle 4: 연도별 추이 라인 차트
  Red   → test_publications_view_trend_line_chart() 작성
  Green → 추이 데이터 + to_line_chart_data() 호출
  Refactor → 없음

Cycle 5: 주저자별 통계 테이블
  Red   → test_publications_view_first_author_table() 작성
  Green → 주저자별 집계 데이터 전달
  Refactor → 페이지네이션 추가
```

---

#### Phase 7: 연구비 시각화 (4시간)

```
Cycle 1: 연구비 페이지 기본 렌더링
  Red   → test_research_budget_view_renders_template() 작성
  Green → research_budget_view() 함수 구현
  Refactor → 없음

Cycle 2: 지원기관별 분포 파이 차트
  Red   → test_research_budget_view_funding_agency_pie() 작성
  Green → ResearchBudgetAggregator + to_pie_chart_data() 호출
  Refactor → 없음

Cycle 3: 집행항목별 막대 그래프
  Red   → test_research_budget_view_expense_category_bar() 작성
  Green → 집행항목별 집계 + to_bar_chart_data() 호출
  Refactor → 정규화 함수 적용

Cycle 4: 연도별 예산/집행 듀얼 축 차트
  Red   → test_research_budget_view_dual_axis_chart() 작성
  Green → to_dual_axis_chart_data() 호출
  Refactor → 집행률 표시 추가

Cycle 5: 과제별 집행률 테이블
  Red   → test_research_budget_view_execution_rate_table() 작성
  Green → v_project_execution_rate 뷰 쿼리
  Refactor → 정렬 및 필터링 옵션
```

---

#### Phase 8: 학생 시각화 (4시간)

```
Cycle 1: 학생 페이지 기본 렌더링
  Red   → test_students_view_renders_template() 작성
  Green → students_view() 함수 구현
  Refactor → 없음

Cycle 2: 학년별 분포 파이 차트
  Red   → test_students_view_grade_distribution_pie() 작성
  Green → StudentAggregator + to_pie_chart_data() 호출
  Refactor → 없음

Cycle 3: 학과별 재학생 수 막대 그래프
  Red   → test_students_view_department_bar_chart() 작성
  Green → 학과별 집계 + to_bar_chart_data() 호출
  Refactor → 없음

Cycle 4: 입학년도별 추이 라인 차트
  Red   → test_students_view_admission_year_trend() 작성
  Green → 입학년도별 집계 + to_line_chart_data() 호출
  Refactor → 없음

Cycle 5: 학적상태별 통계 카드
  Red   → test_students_view_enrollment_status_stats() 작성
  Green → v_department_student_stats 뷰 쿼리
  Refactor → 재학률/휴학률 계산
```

---

## 3. 기능별 테스트 시나리오

### 3.1 데이터 Aggregator 테스트 (Unit Tests)

#### 테스트 파일: `apps/analytics/tests/test_aggregators.py`

```python
from django.test import TestCase
from apps.analytics.models import DepartmentKPI, Publication, ResearchProject, Student
from apps.analytics.aggregators import (
    DepartmentKPIAggregator,
    PublicationAggregator,
    ResearchBudgetAggregator,
    StudentAggregator,
)


class DepartmentKPIAggregatorTest(TestCase):
    """DepartmentKPIAggregator 단위 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        # Arrange: 샘플 KPI 데이터 생성
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=88.5,
            full_time_faculty=17,
            visiting_faculty=5,
            tech_transfer_income=13.5,
            intl_conference_count=4,
        )
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='기계공학과',
            employment_rate=85.0,
            full_time_faculty=15,
            visiting_faculty=3,
            tech_transfer_income=10.0,
            intl_conference_count=2,
        )
        DepartmentKPI.objects.create(
            evaluation_year=2024,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=86.0,
            full_time_faculty=16,
            visiting_faculty=4,
            tech_transfer_income=12.0,
            intl_conference_count=3,
        )

    # Cycle 1
    def test_get_average_employment_rate(self):
        """
        Given: 여러 학과의 KPI 데이터
        When: get_average_employment_rate() 호출
        Then: 평균 취업률 반환
        """
        # Arrange
        aggregator = DepartmentKPIAggregator()

        # Act
        avg_rate = aggregator.get_average_employment_rate(year=2025)

        # Assert
        expected = (88.5 + 85.0) / 2
        self.assertAlmostEqual(avg_rate, expected, places=2)

    # Cycle 2
    def test_get_kpi_by_department(self):
        """
        Given: 특정 학과 필터
        When: get_kpi_by_department() 호출
        Then: 해당 학과의 KPI 데이터 반환
        """
        # Arrange
        aggregator = DepartmentKPIAggregator()

        # Act
        result = aggregator.get_kpi_by_department(
            departments=['컴퓨터공학과'],
            year=2025
        )

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['department'], '컴퓨터공학과')
        self.assertEqual(result[0]['employment_rate'], 88.5)

    # Cycle 3
    def test_get_kpi_trend_by_year(self):
        """
        Given: 여러 연도의 KPI 데이터
        When: get_kpi_trend_by_year() 호출
        Then: 연도별 추이 데이터 반환
        """
        # Arrange
        aggregator = DepartmentKPIAggregator()

        # Act
        trend = aggregator.get_kpi_trend_by_year(
            department='컴퓨터공학과',
            years=[2024, 2025]
        )

        # Assert
        self.assertEqual(len(trend), 2)
        self.assertEqual(trend[0]['year'], 2024)
        self.assertEqual(trend[0]['employment_rate'], 86.0)
        self.assertEqual(trend[1]['year'], 2025)
        self.assertEqual(trend[1]['employment_rate'], 88.5)

    # Cycle 4
    def test_get_kpi_by_college(self):
        """
        Given: 여러 학과의 KPI 데이터
        When: get_kpi_by_college() 호출
        Then: 단과대학별 집계 데이터 반환
        """
        # Arrange
        aggregator = DepartmentKPIAggregator()

        # Act
        result = aggregator.get_kpi_by_college(year=2025)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['college'], '공과대학')
        self.assertEqual(result[0]['total_full_time_faculty'], 17 + 15)
        self.assertAlmostEqual(
            result[0]['avg_employment_rate'],
            (88.5 + 85.0) / 2,
            places=2
        )


class PublicationAggregatorTest(TestCase):
    """PublicationAggregator 단위 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        Publication.objects.create(
            publication_id='PUB-25-001',
            publication_date='2025-06-15',
            college='공과대학',
            department='컴퓨터공학과',
            title='Test Paper 1',
            first_author='이서연',
            journal_name='IEEE IoT Journal',
            journal_grade='SCIE',
            impact_factor=10.6,
            project_linked='Y',
        )
        Publication.objects.create(
            publication_id='PUB-25-002',
            publication_date='2025-07-20',
            college='공과대학',
            department='컴퓨터공학과',
            title='Test Paper 2',
            first_author='정현우',
            journal_name='KCI Journal',
            journal_grade='KCI',
            impact_factor=None,
            project_linked='N',
        )

    # Cycle 1
    def test_get_total_publication_count(self):
        """
        Given: 여러 논문 데이터
        When: get_total_publication_count() 호출
        Then: 총 논문 수 반환
        """
        # Arrange
        aggregator = PublicationAggregator()

        # Act
        count = aggregator.get_total_publication_count()

        # Assert
        self.assertEqual(count, 2)

    # Cycle 2
    def test_get_publications_by_journal_grade(self):
        """
        Given: 여러 저널 등급의 논문
        When: get_publications_by_journal_grade() 호출
        Then: 저널 등급별 논문 수 반환
        """
        # Arrange
        aggregator = PublicationAggregator()

        # Act
        result = aggregator.get_publications_by_journal_grade()

        # Assert
        self.assertEqual(len(result), 2)
        scie = next(r for r in result if r['journal_grade'] == 'SCIE')
        kci = next(r for r in result if r['journal_grade'] == 'KCI')
        self.assertEqual(scie['count'], 1)
        self.assertEqual(kci['count'], 1)

    # Cycle 3
    def test_get_average_impact_factor(self):
        """
        Given: SCIE 논문들의 Impact Factor
        When: get_average_impact_factor() 호출
        Then: 평균 Impact Factor 반환 (NULL 제외)
        """
        # Arrange
        aggregator = PublicationAggregator()

        # Act
        avg_if = aggregator.get_average_impact_factor(journal_grade='SCIE')

        # Assert
        self.assertAlmostEqual(avg_if, 10.6, places=2)

    # Cycle 4
    def test_get_publications_by_first_author(self):
        """
        Given: 여러 주저자의 논문
        When: get_publications_by_first_author() 호출
        Then: 주저자별 논문 수 반환 (상위 N명)
        """
        # Arrange
        aggregator = PublicationAggregator()

        # Act
        result = aggregator.get_publications_by_first_author(limit=10)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn('first_author', result[0])
        self.assertIn('count', result[0])


class ResearchBudgetAggregatorTest(TestCase):
    """ResearchBudgetAggregator 단위 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        from apps.analytics.models import ExecutionRecord

        # 연구 과제 생성
        self.project = ResearchProject.objects.create(
            project_number='NRF-2023-015',
            project_name='AI 연구',
            principal_investigator='이서연',
            department='컴퓨터공학과',
            funding_agency='한국연구재단',
            total_budget=100000000,  # 1억원
        )

        # 집행 내역 생성
        ExecutionRecord.objects.create(
            execution_id='T2301001',
            project=self.project,
            execution_date='2023-03-15',
            expense_category='연구장비 도입',
            amount=30000000,
            status='집행완료',
        )
        ExecutionRecord.objects.create(
            execution_id='T2301002',
            project=self.project,
            execution_date='2023-05-20',
            expense_category='인건비',
            amount=20000000,
            status='집행완료',
        )

    # Cycle 1
    def test_get_total_budget_and_execution(self):
        """
        Given: 연구 과제 및 집행 내역
        When: get_total_budget_and_execution() 호출
        Then: 총 연구비 및 총 집행금액 반환
        """
        # Arrange
        aggregator = ResearchBudgetAggregator()

        # Act
        result = aggregator.get_total_budget_and_execution()

        # Assert
        self.assertEqual(result['total_budget'], 100000000)
        self.assertEqual(result['total_executed'], 50000000)
        self.assertEqual(result['execution_rate'], 50.0)

    # Cycle 2
    def test_get_budget_by_department(self):
        """
        Given: 학과별 연구 과제
        When: get_budget_by_department() 호출
        Then: 학과별 연구비 집계 반환
        """
        # Arrange
        aggregator = ResearchBudgetAggregator()

        # Act
        result = aggregator.get_budget_by_department()

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['department'], '컴퓨터공학과')
        self.assertEqual(result[0]['total_budget'], 100000000)

    # Cycle 3
    def test_get_execution_by_category(self):
        """
        Given: 여러 집행항목
        When: get_execution_by_category() 호출
        Then: 집행항목별 금액 집계 반환
        """
        # Arrange
        aggregator = ResearchBudgetAggregator()

        # Act
        result = aggregator.get_execution_by_category()

        # Assert
        self.assertEqual(len(result), 2)
        equipment = next(r for r in result if r['expense_category'] == '연구장비 도입')
        labor = next(r for r in result if r['expense_category'] == '인건비')
        self.assertEqual(equipment['total_amount'], 30000000)
        self.assertEqual(labor['total_amount'], 20000000)


class StudentAggregatorTest(TestCase):
    """StudentAggregator 단위 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        Student.objects.create(
            student_number='20192101',
            name='정현우',
            college='공과대학',
            department='컴퓨터공학과',
            grade=0,
            program_type='석사',
            enrollment_status='재학',
            gender='남',
            admission_year=2024,
        )
        Student.objects.create(
            student_number='20201234',
            name='김철수',
            college='공과대학',
            department='컴퓨터공학과',
            grade=3,
            program_type='학사',
            enrollment_status='재학',
            gender='남',
            admission_year=2020,
        )
        Student.objects.create(
            student_number='20205678',
            name='이영희',
            college='공과대학',
            department='기계공학과',
            grade=2,
            program_type='학사',
            enrollment_status='휴학',
            gender='여',
            admission_year=2020,
        )

    # Cycle 1
    def test_get_total_students_and_enrollment_rate(self):
        """
        Given: 여러 학적상태의 학생
        When: get_total_students_and_enrollment_rate() 호출
        Then: 총 학생 수 및 재학률 반환
        """
        # Arrange
        aggregator = StudentAggregator()

        # Act
        result = aggregator.get_total_students_and_enrollment_rate()

        # Assert
        self.assertEqual(result['total_students'], 3)
        self.assertEqual(result['enrolled_students'], 2)
        self.assertAlmostEqual(result['enrollment_rate'], 66.67, places=2)

    # Cycle 2
    def test_get_students_by_grade(self):
        """
        Given: 여러 학년의 학생
        When: get_students_by_grade() 호출
        Then: 학년별 학생 수 반환
        """
        # Arrange
        aggregator = StudentAggregator()

        # Act
        result = aggregator.get_students_by_grade()

        # Assert
        self.assertEqual(len(result), 3)
        grade_counts = {r['grade']: r['count'] for r in result}
        self.assertEqual(grade_counts[0], 1)  # 대학원
        self.assertEqual(grade_counts[2], 1)
        self.assertEqual(grade_counts[3], 1)

    # Cycle 3
    def test_get_students_by_department(self):
        """
        Given: 여러 학과의 학생
        When: get_students_by_department() 호출
        Then: 학과별 학생 수 반환
        """
        # Arrange
        aggregator = StudentAggregator()

        # Act
        result = aggregator.get_students_by_department()

        # Assert
        self.assertEqual(len(result), 2)
        dept_counts = {r['department']: r['count'] for r in result}
        self.assertEqual(dept_counts['컴퓨터공학과'], 2)
        self.assertEqual(dept_counts['기계공학과'], 1)
```

---

### 3.2 Chart.js Serializer 테스트 (Unit Tests)

#### 테스트 파일: `apps/analytics/tests/test_serializers.py`

```python
from django.test import TestCase
from apps.analytics.serializers import (
    to_bar_chart_data,
    to_line_chart_data,
    to_pie_chart_data,
    to_multi_dataset_chart_data,
    to_dual_axis_chart_data,
)


class ChartSerializerTest(TestCase):
    """Chart.js Serializer 단위 테스트"""

    # Cycle 1
    def test_to_bar_chart_data(self):
        """
        Given: 딕셔너리 리스트 (label, value)
        When: to_bar_chart_data() 호출
        Then: Chart.js 막대 그래프 형식으로 변환
        """
        # Arrange
        data = [
            {'department': '컴퓨터공학과', 'count': 45},
            {'department': '기계공학과', 'count': 32},
        ]

        # Act
        result = to_bar_chart_data(data, label_field='department', value_field='count')

        # Assert
        self.assertIn('labels', result)
        self.assertIn('datasets', result)
        self.assertEqual(result['labels'], ['컴퓨터공학과', '기계공학과'])
        self.assertEqual(result['datasets'][0]['data'], [45, 32])
        self.assertIn('backgroundColor', result['datasets'][0])

    # Cycle 2
    def test_to_line_chart_data(self):
        """
        Given: 시계열 데이터 (x, y)
        When: to_line_chart_data() 호출
        Then: Chart.js 라인 차트 형식으로 변환
        """
        # Arrange
        data = [
            {'year': 2023, 'employment_rate': 86.0},
            {'year': 2024, 'employment_rate': 87.5},
            {'year': 2025, 'employment_rate': 88.5},
        ]

        # Act
        result = to_line_chart_data(data, x_field='year', y_field='employment_rate')

        # Assert
        self.assertEqual(result['labels'], [2023, 2024, 2025])
        self.assertEqual(result['datasets'][0]['data'], [86.0, 87.5, 88.5])
        self.assertEqual(result['datasets'][0]['borderColor'], '#4e73df')  # 기본 색상

    # Cycle 3
    def test_to_pie_chart_data(self):
        """
        Given: 카테고리별 분포 데이터
        When: to_pie_chart_data() 호출
        Then: Chart.js 파이 차트 형식으로 변환
        """
        # Arrange
        data = [
            {'journal_grade': 'SCIE', 'count': 25},
            {'journal_grade': 'KCI', 'count': 18},
            {'journal_grade': 'SCOPUS', 'count': 12},
        ]

        # Act
        result = to_pie_chart_data(data, label_field='journal_grade', value_field='count')

        # Assert
        self.assertEqual(result['labels'], ['SCIE', 'KCI', 'SCOPUS'])
        self.assertEqual(result['datasets'][0]['data'], [25, 18, 12])
        self.assertEqual(len(result['datasets'][0]['backgroundColor']), 3)

    # Cycle 4
    def test_to_multi_dataset_chart_data(self):
        """
        Given: 여러 시리즈의 데이터
        When: to_multi_dataset_chart_data() 호출
        Then: 다중 데이터셋 차트 형식으로 변환
        """
        # Arrange
        data = [
            {'year': 2023, 'dept_a': 10, 'dept_b': 15},
            {'year': 2024, 'dept_a': 12, 'dept_b': 18},
        ]
        datasets_config = [
            {'label': 'A학과', 'field': 'dept_a', 'color': '#FF6384'},
            {'label': 'B학과', 'field': 'dept_b', 'color': '#36A2EB'},
        ]

        # Act
        result = to_multi_dataset_chart_data(
            data,
            x_field='year',
            datasets_config=datasets_config
        )

        # Assert
        self.assertEqual(result['labels'], [2023, 2024])
        self.assertEqual(len(result['datasets']), 2)
        self.assertEqual(result['datasets'][0]['label'], 'A학과')
        self.assertEqual(result['datasets'][0]['data'], [10, 12])
        self.assertEqual(result['datasets'][1]['label'], 'B학과')
        self.assertEqual(result['datasets'][1]['data'], [15, 18])

    # Cycle 5
    def test_to_dual_axis_chart_data(self):
        """
        Given: 듀얼 축 데이터 (예산 vs 집행률)
        When: to_dual_axis_chart_data() 호출
        Then: 듀얼 축 차트 형식으로 변환
        """
        # Arrange
        data = [
            {'year': 2023, 'budget': 100000000, 'execution_rate': 85.0},
            {'year': 2024, 'budget': 120000000, 'execution_rate': 90.0},
        ]

        # Act
        result = to_dual_axis_chart_data(
            data,
            x_field='year',
            y1_field='budget',
            y2_field='execution_rate',
            y1_label='총 연구비',
            y2_label='집행률 (%)'
        )

        # Assert
        self.assertEqual(result['labels'], [2023, 2024])
        self.assertEqual(len(result['datasets']), 2)
        self.assertEqual(result['datasets'][0]['label'], '총 연구비')
        self.assertEqual(result['datasets'][0]['yAxisID'], 'y1')
        self.assertEqual(result['datasets'][1]['label'], '집행률 (%)')
        self.assertEqual(result['datasets'][1]['yAxisID'], 'y2')
```

---

### 3.3 필터링 로직 테스트 (Unit Tests)

#### 테스트 파일: `apps/analytics/tests/test_filters.py`

```python
from django.test import TestCase
from datetime import date
from apps.analytics.models import Publication, DepartmentKPI
from apps.analytics.filters import (
    filter_by_date_range,
    filter_by_department,
    filter_by_college,
    apply_user_permission_filter,
    apply_multiple_filters,
)
from apps.authentication.models import User


class FilterLogicTest(TestCase):
    """필터링 로직 단위 테스트"""

    def setUp(self):
        """테스트 데이터 생성"""
        # 논문 데이터
        Publication.objects.create(
            publication_id='PUB-25-001',
            publication_date=date(2025, 6, 15),
            college='공과대학',
            department='컴퓨터공학과',
            title='Paper 1',
            first_author='Author A',
            journal_name='Journal A',
            journal_grade='SCIE',
        )
        Publication.objects.create(
            publication_id='PUB-24-001',
            publication_date=date(2024, 3, 10),
            college='인문대학',
            department='영어영문학과',
            title='Paper 2',
            first_author='Author B',
            journal_name='Journal B',
            journal_grade='KCI',
        )

        # 사용자
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.viewer = User.objects.create(
            email='viewer@university.ac.kr',
            name='일반 사용자',
            department='컴퓨터공학과',
            role='viewer',
            status='active',
        )

    # Cycle 1
    def test_filter_by_date_range(self):
        """
        Given: 날짜 범위 필터
        When: filter_by_date_range() 호출
        Then: 해당 범위의 데이터만 반환
        """
        # Arrange
        qs = Publication.objects.all()

        # Act
        result = filter_by_date_range(
            qs,
            date_field='publication_date',
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31)
        )

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().publication_id, 'PUB-25-001')

    # Cycle 2
    def test_filter_by_department(self):
        """
        Given: 학과 필터
        When: filter_by_department() 호출
        Then: 해당 학과의 데이터만 반환
        """
        # Arrange
        qs = Publication.objects.all()

        # Act
        result = filter_by_department(qs, departments=['컴퓨터공학과'])

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().department, '컴퓨터공학과')

    # Cycle 3
    def test_filter_by_college(self):
        """
        Given: 단과대학 필터
        When: filter_by_college() 호출
        Then: 해당 단과대학의 데이터만 반환
        """
        # Arrange
        qs = Publication.objects.all()

        # Act
        result = filter_by_college(qs, colleges=['공과대학'])

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().college, '공과대학')

    # Cycle 4
    def test_apply_user_permission_filter_admin(self):
        """
        Given: admin 사용자
        When: apply_user_permission_filter() 호출
        Then: 모든 데이터 반환
        """
        # Arrange
        qs = Publication.objects.all()

        # Act
        result = apply_user_permission_filter(qs, user=self.admin)

        # Assert
        self.assertEqual(result.count(), 2)

    def test_apply_user_permission_filter_viewer(self):
        """
        Given: viewer 사용자
        When: apply_user_permission_filter() 호출
        Then: 소속 학과 데이터만 반환
        """
        # Arrange
        qs = Publication.objects.all()

        # Act
        result = apply_user_permission_filter(qs, user=self.viewer)

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().department, '컴퓨터공학과')

    # Cycle 5
    def test_apply_multiple_filters(self):
        """
        Given: 여러 필터 조건
        When: apply_multiple_filters() 호출
        Then: 모든 조건을 만족하는 데이터 반환
        """
        # Arrange
        qs = Publication.objects.all()
        filters = {
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 12, 31),
            'colleges': ['인문대학'],
            'departments': ['영어영문학과'],
        }

        # Act
        result = apply_multiple_filters(qs, filters, date_field='publication_date')

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().publication_id, 'PUB-24-001')
```

---

### 3.4 뷰 테스트 (Integration Tests)

#### 테스트 파일: `apps/analytics/tests/test_views.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User
from apps.analytics.models import DepartmentKPI, Publication


class DashboardViewTest(TestCase):
    """대시보드 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.dashboard_url = reverse('dashboard')

        # 활성 사용자 생성
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            status='active',
        )
        self.user.set_password('test1234')
        self.user.save()

        # 샘플 데이터
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=88.5,
            full_time_faculty=17,
        )

    # Cycle 1
    def test_dashboard_view_renders_template(self):
        """
        Given: 로그인된 사용자
        When: GET /dashboard
        Then: 대시보드 템플릿 렌더링
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(self.dashboard_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/dashboard.html')

    # Cycle 2
    def test_dashboard_view_includes_kpi_summary(self):
        """
        Given: 로그인된 사용자
        When: GET /dashboard
        Then: KPI 요약 카드 데이터 포함
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(self.dashboard_url)

        # Assert
        self.assertIn('kpi_summary', response.context)
        self.assertIn('avg_employment_rate', response.context['kpi_summary'])

    # Cycle 3
    def test_dashboard_view_filters_by_user_role(self):
        """
        Given: viewer 사용자 (특정 학과 소속)
        When: GET /dashboard
        Then: 소속 학과 데이터만 표시
        """
        # Arrange
        viewer = User.objects.create(
            email='viewer@university.ac.kr',
            name='Viewer',
            department='기계공학과',
            role='viewer',
            status='active',
        )
        self.client.force_login(viewer)

        # Act
        response = self.client.get(self.dashboard_url)

        # Assert
        # 컴퓨터공학과 데이터는 보이지 않음
        self.assertNotContains(response, '컴퓨터공학과')

    # Cycle 4
    def test_dashboard_view_shows_recent_uploads(self):
        """
        Given: 로그인된 사용자
        When: GET /dashboard
        Then: 최근 업로드 정보 포함
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(self.dashboard_url)

        # Assert
        self.assertIn('recent_uploads', response.context)

    # Cycle 5
    def test_dashboard_view_includes_trend_charts(self):
        """
        Given: 로그인된 사용자
        When: GET /dashboard
        Then: 추이 그래프 데이터 포함
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(self.dashboard_url)

        # Assert
        self.assertIn('trend_chart_data', response.context)
        self.assertIsInstance(response.context['trend_chart_data'], dict)
        self.assertIn('labels', response.context['trend_chart_data'])


class DepartmentKPIViewTest(TestCase):
    """학과별 KPI 시각화 뷰 테스트"""

    def setUp(self):
        self.client = Client()
        self.kpi_url = reverse('department_kpi')

        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            status='active',
        )
        self.client.force_login(self.user)

        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=88.5,
            full_time_faculty=17,
        )

    # Cycle 1
    def test_department_kpi_view_renders_template(self):
        """
        Given: 로그인된 사용자
        When: GET /analytics/department-kpi
        Then: KPI 페이지 렌더링
        """
        # Act
        response = self.client.get(self.kpi_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/department_kpi.html')

    # Cycle 2
    def test_department_kpi_view_applies_filters(self):
        """
        Given: 쿼리 파라미터 (year, department)
        When: GET /analytics/department-kpi?year=2025&department=컴퓨터공학과
        Then: 필터 적용된 데이터 반환
        """
        # Act
        response = self.client.get(self.kpi_url, {
            'year': 2025,
            'department': '컴퓨터공학과',
        })

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn('filtered_data', response.context)

    # Cycle 3
    def test_department_kpi_view_employment_rate_chart(self):
        """
        Given: 로그인된 사용자
        When: GET /analytics/department-kpi
        Then: 취업률 차트 데이터 포함
        """
        # Act
        response = self.client.get(self.kpi_url)

        # Assert
        self.assertIn('employment_rate_chart', response.context)
        chart_data = response.context['employment_rate_chart']
        self.assertIn('labels', chart_data)
        self.assertIn('datasets', chart_data)


class PublicationsViewTest(TestCase):
    """논문 시각화 뷰 테스트"""

    def setUp(self):
        self.client = Client()
        self.publications_url = reverse('publications')

        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            status='active',
        )
        self.client.force_login(self.user)

        Publication.objects.create(
            publication_id='PUB-25-001',
            publication_date='2025-06-15',
            college='공과대학',
            department='컴퓨터공학과',
            title='Test Paper',
            first_author='Author',
            journal_name='Journal',
            journal_grade='SCIE',
        )

    # Cycle 1
    def test_publications_view_renders_template(self):
        """
        Given: 로그인된 사용자
        When: GET /analytics/publications
        Then: 논문 페이지 렌더링
        """
        # Act
        response = self.client.get(self.publications_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/publications.html')

    # Cycle 2
    def test_publications_view_journal_grade_pie_chart(self):
        """
        Given: 로그인된 사용자
        When: GET /analytics/publications
        Then: 저널 등급별 파이 차트 데이터 포함
        """
        # Act
        response = self.client.get(self.publications_url)

        # Assert
        self.assertIn('journal_grade_pie_chart', response.context)
        chart_data = response.context['journal_grade_pie_chart']
        self.assertIn('labels', chart_data)
        self.assertIn('datasets', chart_data)
```

---

### 3.5 Acceptance Tests (End-to-End)

#### 테스트 파일: `apps/analytics/tests/test_acceptance.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User
from apps.analytics.models import DepartmentKPI, Publication


class DashboardAcceptanceTest(TestCase):
    """대시보드 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()

    def test_full_dashboard_flow(self):
        """
        Scenario: 로그인 → 대시보드 조회 → 필터 적용 → 시각화 페이지 이동
        Given: 활성 사용자
        When: 로그인 → 대시보드 → 각 시각화 페이지 순회
        Then: 모든 페이지 정상 렌더링 및 데이터 표시
        """
        # Step 1: 사용자 생성
        user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트 사용자',
            status='active',
        )
        user.set_password('test1234')
        user.save()

        # Step 2: 샘플 데이터 생성
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=88.5,
            full_time_faculty=17,
        )
        Publication.objects.create(
            publication_id='PUB-25-001',
            publication_date='2025-06-15',
            college='공과대학',
            department='컴퓨터공학과',
            title='Test Paper',
            first_author='Author',
            journal_name='Journal',
            journal_grade='SCIE',
        )

        # Step 3: 로그인
        login_successful = self.client.login(
            email='test@university.ac.kr',
            password='test1234'
        )
        self.assertTrue(login_successful)

        # Step 4: 대시보드 접근
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '대시보드')

        # Step 5: 학과별 KPI 페이지 이동
        response = self.client.get(reverse('department_kpi'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '학과별 KPI')

        # Step 6: 논문 페이지 이동
        response = self.client.get(reverse('publications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '논문')

        # Step 7: 필터 적용
        response = self.client.get(reverse('department_kpi'), {
            'year': 2025,
            'department': '컴퓨터공학과',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '88.5')  # 취업률 표시 확인
```

---

## 4. AAA 패턴 적용 예제

### 4.1 Aggregator 테스트 (AAA)

```python
def test_get_average_employment_rate(self):
    """
    Given: 여러 학과의 KPI 데이터
    When: 평균 취업률 계산
    Then: 올바른 평균값 반환
    """
    # Arrange (준비)
    # 1. 테스트 데이터 생성
    DepartmentKPI.objects.create(
        evaluation_year=2025,
        college='공과대학',
        department='컴퓨터공학과',
        employment_rate=88.5,
    )
    DepartmentKPI.objects.create(
        evaluation_year=2025,
        college='공과대학',
        department='기계공학과',
        employment_rate=85.0,
    )
    # 2. Aggregator 인스턴스 생성
    aggregator = DepartmentKPIAggregator()

    # Act (실행)
    # 평균 취업률 계산
    avg_rate = aggregator.get_average_employment_rate(year=2025)

    # Assert (검증)
    # 1. 예상값 계산
    expected = (88.5 + 85.0) / 2
    # 2. 결과 검증
    self.assertAlmostEqual(avg_rate, expected, places=2)
```

---

## 5. FIRST 원칙 적용

### 5.1 Fast (빠른 테스트)
- Aggregator 테스트: 각 50ms 이하
- Serializer 테스트: 각 10ms 이하
- Integration 테스트: 각 200ms 이하

### 5.2 Independent (독립적)
```python
class IndependentAggregatorTest(TestCase):
    def setUp(self):
        """각 테스트마다 독립적으로 실행"""
        # 테스트 데이터 생성
        self.kpi = DepartmentKPI.objects.create(...)

    def test_method_a(self):
        """독립적 테스트 A"""
        # 다른 테스트의 영향 받지 않음
        pass

    def test_method_b(self):
        """독립적 테스트 B"""
        # test_method_a와 무관하게 실행
        pass
```

### 5.3 Repeatable (반복 가능)
- 고정된 테스트 데이터 사용
- 랜덤 값 사용 시 시드 고정
- 외부 API 호출 없음

### 5.4 Self-validating (자가 검증)
```python
def test_chart_serializer_returns_valid_format(self):
    """차트 데이터 형식 검증 (자가 검증)"""
    # Arrange
    data = [{'label': 'A', 'value': 10}]

    # Act
    result = to_bar_chart_data(data, 'label', 'value')

    # Assert
    # 명확한 검증, 수동 확인 불필요
    self.assertIn('labels', result, "labels 필드 필수")
    self.assertIn('datasets', result, "datasets 필드 필수")
    self.assertIsInstance(result['datasets'], list, "datasets는 리스트여야 함")
```

### 5.5 Timely (적시성)
- 코드 작성 전 테스트 먼저 작성
- Red → Green → Refactor 사이클 준수

---

## 6. 테스트 실행 계획

### 6.1 테스트 실행 명령어

```bash
# 전체 analytics 테스트 실행
python manage.py test apps.analytics

# Unit 테스트만 실행
python manage.py test apps.analytics.tests.test_aggregators
python manage.py test apps.analytics.tests.test_serializers
python manage.py test apps.analytics.tests.test_filters

# Integration 테스트만 실행
python manage.py test apps.analytics.tests.test_views

# Acceptance 테스트만 실행
python manage.py test apps.analytics.tests.test_acceptance

# 코드 커버리지 측정
coverage run --source='apps.analytics' manage.py test apps.analytics
coverage report
coverage html
```

### 6.2 테스트 실행 시간 예상

| 테스트 유형 | 개수 | 예상 시간 | 비고 |
|------------|------|----------|------|
| Unit (Aggregator) | 30 | 2초 | DB 쿼리 포함 |
| Unit (Serializer) | 15 | 0.5초 | 순수 함수 |
| Unit (Filter) | 15 | 1초 | DB 쿼리 포함 |
| Integration (Views) | 25 | 8초 | 템플릿 렌더링 |
| Acceptance | 8 | 6초 | 전체 플로우 |
| **총합** | **93** | **17.5초** | 충분히 빠름 |

---

## 7. 커밋 전략

### 7.1 작은 단위 커밋

```bash
# Phase 1 Cycle 1 완료 후
git add apps/analytics/aggregators.py apps/analytics/tests/test_aggregators.py
git commit -m "test: DepartmentKPIAggregator 평균 취업률 계산 테스트 및 구현

- Red: test_get_average_employment_rate() 작성
- Green: get_average_employment_rate() 메서드 구현
- Refactor: Django aggregate() 함수 활용
"

# Phase 2 Cycle 1 완료 후
git add apps/analytics/serializers.py apps/analytics/tests/test_serializers.py
git commit -m "test: Chart.js 막대 그래프 데이터 변환 테스트 및 구현

- Red: test_to_bar_chart_data() 작성
- Green: to_bar_chart_data() 함수 구현
- Refactor: 색상 팔레트 상수 분리
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
- [ ] 쿼리 최적화 검토
- [ ] 문서 업데이트
- [ ] 다음 Phase 진행

### 8.3 전체 완료 시
- [ ] 모든 테스트 통과 (Unit + Integration + Acceptance)
- [ ] 코드 커버리지 85% 이상
- [ ] Chart.js 렌더링 확인 (수동 테스트)
- [ ] 성능 검토 (N+1 쿼리 방지)
- [ ] 보안 검토 (권한 체크)
- [ ] Pull Request 생성

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성<br>- 대시보드 및 시각화 페이지 TDD 구현 계획<br>- 93개 테스트 시나리오<br>- Aggregator, Serializer, Filter 테스트<br>- 5개 시각화 페이지 통합 테스트 | Claude Code |

---

## 10. 참고 문서

- [TDD 가이드라인](/Users/seunghyun/Test/vmc6/docs/tdd.md)
- [Database Schema](/Users/seunghyun/Test/vmc6/docs/database.md)
- [UC-04: 대시보드](/Users/seunghyun/Test/vmc6/docs/usecases/04-dashboard/spec.md)
- [UC-05: 학과별 KPI](/Users/seunghyun/Test/vmc6/docs/usecases/05-department-kpi/spec.md)
- [UC-06: 논문 시각화](/Users/seunghyun/Test/vmc6/docs/usecases/06-publications/spec.md)
- [UC-07: 연구비 시각화](/Users/seunghyun/Test/vmc6/docs/usecases/07-research-budget/spec.md)
- [UC-08: 학생 시각화](/Users/seunghyun/Test/vmc6/docs/usecases/08-students/spec.md)
- [공통 모듈 문서](/Users/seunghyun/Test/vmc6/docs/common-modules.md)

---

**문서 작성 완료**
**다음 작업**: Phase 1 (데이터 Aggregator) 구현 시작
