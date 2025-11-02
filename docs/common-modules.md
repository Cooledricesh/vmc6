# 공통 모듈 작업 계획서
## 대학교 데이터 시각화 대시보드

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 1.0
- **프로젝트**: 대학교 데이터 시각화 대시보드 MVP
- **기술 스택**: Django + PostgreSQL + Chart.js + Railway

---

## 1. 개요

### 1.1 목적
본 문서는 페이지 단위 개발을 시작하기 전에 구현해야 할 **공통 모듈 및 재사용 가능한 컴포넌트**를 정의합니다. 모든 공통 모듈은 특정 페이지에 의존적이지 않으며, 프로젝트 전반에 걸쳐 재사용될 수 있도록 설계되었습니다.

### 1.2 설계 원칙
- **오버엔지니어링 방지**: 문서에 명시된 기능만 구현
- **MVP 우선**: 개발 속도 극대화를 위한 단순성 유지
- **병렬 개발 지원**: 페이지별 개발이 독립적으로 진행될 수 있도록 공통 로직 분리
- **재사용성**: DRY(Don't Repeat Yourself) 원칙 준수

### 1.3 프로젝트 기술 스택 확인
- **백엔드**: Django (Python) + Django 템플릿
- **데이터베이스**: PostgreSQL (Supabase)
- **프론트엔드**: Django 템플릿 + Chart.js
- **인증**: Django 세션 기반 인증
- **데이터 처리**: Pandas
- **배포**: Railway

### 1.4 Supabase 데이터베이스 설정
본 프로젝트는 PostgreSQL 기반의 Supabase를 데이터베이스로 사용합니다.

#### 1.4.1 Supabase 환경
- **프로젝트 ID**: vmc6
- **로컬 개발**: Supabase CLI를 통한 로컬 환경
- **프로덕션**: Supabase 클라우드 (https://vqwhekzhmhczdwrrbjke.supabase.co)

#### 1.4.2 환경 변수 (.env.local)
```.env
NEXT_PUBLIC_SUPABASE_URL=https://vqwhekzhmhczdwrrbjke.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
```

#### 1.4.3 데이터베이스 스키마
- **마이그레이션 파일**: `supabase/migrations/20251102000000_initial_schema.sql`
- **테이블 수**: 7개 (users, upload_history, department_kpi, publications, research_projects, execution_records, students)
- **뷰**: 3개 (v_project_execution_rate, v_department_student_stats, v_publication_stats)

#### 1.4.4 Supabase CLI 주요 명령어
```bash
# 로컬 Supabase 시작
supabase start

# 로컬 Supabase 중지
supabase stop

# 마이그레이션 적용
supabase db push

# 데이터베이스 리셋 (마이그레이션 재적용)
supabase db reset

# Supabase Studio 접속 (로컬)
# http://127.0.0.1:54323

# 원격 데이터베이스와 동기화
supabase db pull
```

#### 1.4.5 Django 데이터베이스 설정
Django에서 Supabase PostgreSQL에 연결하기 위한 설정은 다음과 같습니다:

**config/settings/base.py**:
```python
import os
from pathlib import Path

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('SUPABASE_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '54322'),
    }
}
```

**로컬 환경** (`config/settings/local.py`):
```python
# Supabase 로컬 개발 환경
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '54322',  # Supabase 로컬 DB 포트
    }
}
```

**프로덕션 환경** (`config/settings/production.py`):
```python
import dj_database_url

# Railway 또는 Supabase 프로덕션 환경
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

#### 1.4.6 마이그레이션 전략
1. **Supabase 우선**: 스키마 변경은 Supabase 마이그레이션 파일 (`supabase/migrations/*.sql`)로 관리
2. **Django는 읽기 전용**: Django ORM은 기존 테이블 구조를 읽기만 하며, 스키마 변경은 하지 않음
3. **초기 마이그레이션**: Django의 `python manage.py migrate`는 Django 내장 앱(admin, auth, sessions 등)에만 적용

**Django 모델과 Supabase 테이블 동기화**:
```python
# apps/authentication/models.py
from django.db import models

class User(models.Model):
    """Supabase users 테이블과 매핑"""

    class Meta:
        db_table = 'users'  # Supabase 테이블명과 일치
        managed = False     # Django가 스키마를 관리하지 않음

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 1.4.7 Supabase 로컬 환경 포트
- **PostgreSQL**: 54322
- **API**: 54321
- **Studio (GUI)**: 54323
- **Inbucket (이메일 테스트)**: 54324

---

## 2. 공통 모듈 구성도

```
vmc6/
├── apps/                       # Django 앱 디렉토리
│   ├── core/                   # 핵심 공통 기능
│   │   ├── models.py           # 공통 모델 (BaseModel 등)
│   │   ├── middleware.py       # 인증 미들웨어, 로깅 미들웨어
│   │   ├── decorators.py       # 권한 체크 데코레이터
│   │   ├── validators.py       # 공통 입력 검증 로직
│   │   ├── exceptions.py       # 커스텀 예외 클래스
│   │   └── constants.py        # 상수 정의
│   │
│   ├── authentication/         # 인증/인가 모듈
│   │   ├── models.py           # User 모델
│   │   ├── forms.py            # 로그인, 회원가입 폼
│   │   ├── views.py            # 인증 관련 뷰
│   │   ├── backends.py         # 커스텀 인증 백엔드
│   │   └── permissions.py      # 권한 체크 로직
│   │
│   ├── data_upload/            # 데이터 업로드 모듈
│   │   ├── models.py           # UploadHistory 모델
│   │   ├── parsers.py          # 엑셀/CSV 파싱 로직
│   │   ├── validators.py       # 데이터 검증 로직
│   │   ├── admin.py            # Django Admin 커스터마이징
│   │   └── signals.py          # 업로드 후처리 시그널
│   │
│   ├── analytics/              # 데이터 분석 및 시각화 모듈
│   │   ├── models.py           # 데이터 모델 (KPI, Publication 등)
│   │   ├── aggregators.py      # 데이터 집계 로직
│   │   ├── filters.py          # 필터링 로직
│   │   └── serializers.py      # Chart.js용 데이터 직렬화
│   │
│   └── utils/                  # 유틸리티 모듈
│       ├── date_helpers.py     # 날짜 관련 헬퍼
│       ├── number_helpers.py   # 숫자 포맷팅 헬퍼
│       ├── chart_helpers.py    # Chart.js 설정 헬퍼
│       └── export_helpers.py   # CSV/Excel 내보내기 헬퍼
│
├── templates/                  # Django 템플릿
│   ├── base/                   # 기본 레이아웃
│   │   ├── base.html           # 전체 레이아웃 기본
│   │   ├── base_dashboard.html # 대시보드 레이아웃
│   │   └── base_auth.html      # 인증 페이지 레이아웃
│   │
│   ├── components/             # 재사용 컴포넌트
│   │   ├── navbar.html         # 네비게이션 바
│   │   ├── sidebar.html        # 사이드바 메뉴
│   │   ├── footer.html         # 푸터
│   │   ├── filter_panel.html   # 필터 패널
│   │   ├── kpi_card.html       # KPI 요약 카드
│   │   ├── chart_wrapper.html  # 차트 래퍼
│   │   ├── data_table.html     # 데이터 테이블
│   │   └── pagination.html     # 페이지네이션
│   │
│   └── messages/               # 메시지 템플릿
│       ├── success.html        # 성공 메시지
│       ├── error.html          # 에러 메시지
│       └── warning.html        # 경고 메시지
│
├── static/                     # 정적 파일
│   ├── css/                    # 스타일시트
│   │   ├── base.css            # 기본 스타일
│   │   ├── components.css      # 컴포넌트 스타일
│   │   ├── dashboard.css       # 대시보드 스타일
│   │   └── charts.css          # 차트 스타일
│   │
│   └── js/                     # JavaScript
│       ├── chart-config.js     # Chart.js 기본 설정
│       ├── filter-handler.js   # 필터 핸들러
│       ├── table-handler.js    # 테이블 정렬/검색
│       └── utils.js            # 유틸리티 함수
│
└── config/                     # 설정 파일
    ├── settings/               # Django 설정
    │   ├── base.py             # 기본 설정
    │   ├── local.py            # 로컬 환경 설정
    │   └── production.py       # 프로덕션 설정
    │
    └── logging.py              # 로깅 설정
```

---

## 3. 공통 모듈 상세 설계

### 3.1 Core 모듈

#### 3.1.1 BaseModel (추상 모델)
**목적**: 모든 모델에 공통으로 필요한 필드 제공

**파일**: `apps/core/models.py`

**필드**:
- `created_at`: 생성 일시 (자동)
- `updated_at`: 수정 일시 (자동)

**사용처**: 모든 데이터 모델의 부모 클래스

---

#### 3.1.2 인증 미들웨어
**목적**: 로그인 상태 확인 및 세션 관리

**파일**: `apps/core/middleware.py`

**기능**:
- 세션 유효성 검증
- 비로그인 사용자 리디렉션
- 활성화되지 않은 사용자 차단 (status != 'active')

**적용 범위**: `/dashboard`, `/analytics/*`, `/profile`, `/admin` 등 로그인 필요 페이지

---

#### 3.1.3 권한 체크 데코레이터
**목적**: 뷰 함수에 권한 체크 로직 적용

**파일**: `apps/core/decorators.py`

**데코레이터 목록**:
1. `@login_required`: 로그인 필수
2. `@role_required(['admin'])`: 관리자 전용
3. `@role_required(['admin', 'manager'])`: 관리자 또는 매니저 전용
4. `@active_user_required`: 활성화된 사용자만 (status='active')

**사용 예시**:
```python
@login_required
@role_required(['admin'])
def admin_dashboard(request):
    pass
```

---

#### 3.1.4 공통 Validator
**목적**: 입력 데이터 검증 로직 재사용

**파일**: `apps/core/validators.py`

**함수 목록**:
1. `validate_email(email)`: 이메일 형식 검증
2. `validate_password(password)`: 비밀번호 정책 검증 (최소 4자)
3. `validate_file_extension(filename, allowed_extensions)`: 파일 확장자 검증
4. `validate_file_size(file, max_size_mb)`: 파일 크기 검증 (최대 50MB)
5. `validate_date_range(start_date, end_date)`: 날짜 범위 검증

---

#### 3.1.5 커스텀 예외
**목적**: 에러 핸들링 표준화

**파일**: `apps/core/exceptions.py`

**예외 클래스**:
1. `InvalidFileFormatError`: 잘못된 파일 형식
2. `FileSizeLimitExceededError`: 파일 크기 초과
3. `DataValidationError`: 데이터 검증 실패
4. `PermissionDeniedError`: 권한 부족
5. `UserNotActiveError`: 사용자 비활성화 상태

---

#### 3.1.6 상수 정의
**목적**: 프로젝트 전체에서 사용되는 상수 중앙 관리

**파일**: `apps/core/constants.py`

**상수 목록**:
```python
# 사용자 역할
USER_ROLES = [
    ('admin', '관리자'),
    ('manager', '매니저'),
    ('viewer', '일반 사용자'),
]

# 사용자 상태
USER_STATUS = [
    ('pending', '승인 대기'),
    ('active', '활성'),
    ('inactive', '비활성'),
]

# 데이터 타입
DATA_TYPES = [
    ('department_kpi', '학과별 KPI'),
    ('publication', '논문 게재 목록'),
    ('research_budget', '연구비 집행 데이터'),
    ('student', '학생 명단'),
]

# 업로드 상태
UPLOAD_STATUS = [
    ('success', '성공'),
    ('failed', '실패'),
]

# 파일 업로드 설정
MAX_UPLOAD_SIZE_MB = 50
ALLOWED_FILE_EXTENSIONS = ['.xlsx', '.xls', '.csv']

# 저널 등급
JOURNAL_GRADES = ['SCIE', 'KCI', 'SCOPUS', 'KCI후보', '기타']

# 집행 상태
EXECUTION_STATUS = ['집행완료', '처리중']

# 학적 상태
ENROLLMENT_STATUS = ['재학', '휴학', '졸업']

# 과정 구분
PROGRAM_TYPES = ['학사', '석사', '박사']

# 성별
GENDER_CHOICES = [('남', '남'), ('여', '여')]
```

---

### 3.2 Authentication 모듈

#### 3.2.1 User 모델
**목적**: 사용자 인증 및 권한 관리

**파일**: `apps/authentication/models.py`

**필드**:
- `email`: 이메일 (UNIQUE, 로그인 ID)
- `password`: 해싱된 비밀번호
- `name`: 사용자 이름
- `department`: 소속 부서/학과
- `position`: 직책
- `role`: 역할 (admin, manager, viewer)
- `status`: 상태 (pending, active, inactive)

**메서드**:
- `is_admin()`: 관리자 여부 확인
- `is_active_user()`: 활성 사용자 여부 확인
- `can_access_department(department)`: 특정 학과 데이터 접근 권한 확인

---

#### 3.2.2 인증 폼
**목적**: 로그인 및 회원가입 폼 제공

**파일**: `apps/authentication/forms.py`

**폼 목록**:
1. `LoginForm`: 로그인 폼 (email, password)
2. `SignupForm`: 회원가입 폼 (email, password, password_confirm, name, department, position)
3. `ProfileUpdateForm`: 프로필 수정 폼
4. `PasswordChangeForm`: 비밀번호 변경 폼

**검증 로직**:
- 이메일 중복 체크
- 비밀번호 정책 검증
- 비밀번호 일치 확인

---

#### 3.2.3 인증 뷰
**목적**: 로그인, 회원가입, 로그아웃 뷰 제공

**파일**: `apps/authentication/views.py`

**뷰 목록**:

0. **`index_view()`**: 루트 페이지 핸들러
   - **URL**: `/`
   - **기능**:
     - 인증 상태 확인 (`request.user.is_authenticated`)
     - 미인증 사용자: `login_view()` 호출 (동일한 로그인 템플릿 렌더링)
     - 인증된 사용자: `/dashboard`로 리디렉션
   - **사용 예시**:
     ```python
     def index_view(request):
         """루트 페이지 - 인증 상태에 따라 분기"""
         if request.user.is_authenticated:
             return redirect('dashboard')
         return login_view(request)
     ```

1. **`login_view()`**: 로그인 뷰
   - **URL**: `/login`, `/` (미인증 시)
   - **기능**: 이메일과 비밀번호로 로그인
   - **템플릿**: `authentication/login.html`

2. **`signup_view()`**: 회원가입 뷰
   - **URL**: `/signup`
   - **기능**: 신규 사용자 등록 (status='pending')

3. **`logout_view()`**: 로그아웃 뷰
   - **URL**: `/logout`
   - **기능**: 세션 삭제 및 로그인 페이지로 리디렉션

---

#### 3.2.4 권한 체크 로직
**목적**: 사용자별 데이터 접근 권한 확인

**파일**: `apps/authentication/permissions.py`

**함수 목록**:
1. `can_view_all_departments(user)`: 전체 학과 조회 권한 (admin, manager만)
2. `can_upload_data(user)`: 데이터 업로드 권한 (admin만)
3. `can_approve_users(user)`: 사용자 승인 권한 (admin만)
4. `get_accessible_departments(user)`: 사용자가 접근 가능한 학과 목록 반환

**사용 예시**:
```python
if can_view_all_departments(request.user):
    departments = Department.objects.all()
else:
    departments = [request.user.department]
```

---

### 3.3 Data Upload 모듈

#### 3.3.1 파일 파서
**목적**: 엑셀/CSV 파일을 파싱하여 데이터베이스에 저장

**파일**: `apps/data_upload/parsers.py`

**클래스 목록**:
1. `BaseParser`: 추상 파서 클래스
2. `DepartmentKPIParser`: 학과별 KPI 데이터 파서
3. `PublicationParser`: 논문 게재 데이터 파서
4. `ResearchBudgetParser`: 연구비 집행 데이터 파서
5. `StudentParser`: 학생 명단 파서

**공통 메서드**:
- `parse(file)`: 파일 파싱
- `validate_schema(df)`: 스키마 검증 (필수 컬럼 확인)
- `clean_data(df)`: 데이터 정제 (공백 제거, 형변환 등)
- `save_to_db(df)`: 데이터베이스 저장 (bulk_create 활용)

**에러 처리**:
- 파싱 실패 시 상세 오류 메시지 반환 (행번호, 컬럼명, 오류 내용)
- 부분 실패 시 롤백 처리

---

#### 3.3.2 데이터 Validator
**목적**: 업로드된 데이터의 유효성 검증

**파일**: `apps/data_upload/validators.py`

**함수 목록**:
1. `validate_department_kpi_data(df)`: 학과별 KPI 검증
2. `validate_publication_data(df)`: 논문 데이터 검증
3. `validate_research_budget_data(df)`: 연구비 데이터 검증
4. `validate_student_data(df)`: 학생 데이터 검증

**검증 항목**:
- 필수 컬럼 존재 여부
- 데이터 타입 (숫자, 날짜, 문자열 등)
- 값의 범위 (취업률 0~100%, 금액 > 0 등)
- 중복 검사 (유니크 제약조건)
- 외래키 참조 무결성 (과제번호 존재 여부 등)

---

#### 3.3.3 Django Admin 커스터마이징
**목적**: 파일 업로드 UI를 Django Admin에 통합

**파일**: `apps/data_upload/admin.py`

**커스터마이징 내용**:
1. 파일 업로드 필드 추가
2. 업로드 후 자동 파싱 로직 연결 (save_model 오버라이드)
3. 업로드 이력 자동 기록
4. 성공/실패 메시지 표시
5. 실패 시 오류 로그 다운로드 링크 제공

---

#### 3.3.4 업로드 후처리 Signal
**목적**: 파일 업로드 완료 후 자동 처리

**파일**: `apps/data_upload/signals.py`

**시그널**:
- `post_save` 시그널을 활용하여 파일 업로드 감지
- 파싱 및 검증 로직 실행
- UploadHistory 모델에 결과 기록

---

### 3.4 Analytics 모듈

#### 3.4.1 데이터 Aggregator
**목적**: 시각화를 위한 데이터 집계 로직

**파일**: `apps/analytics/aggregators.py`

**클래스 목록**:
1. `DepartmentKPIAggregator`: 학과별 KPI 집계
2. `PublicationAggregator`: 논문 게재 통계
3. `ResearchBudgetAggregator`: 연구비 집행 통계
4. `StudentAggregator`: 학생 현황 통계

**공통 메서드**:
- `get_summary_stats()`: 요약 통계 (총합, 평균, 최대/최소)
- `get_trend_data(years)`: 추이 데이터 (연도별)
- `get_comparison_data(departments)`: 비교 데이터 (학과별)
- `get_distribution_data(category)`: 분포 데이터 (카테고리별)

**반환 형식**:
- Chart.js에서 바로 사용 가능한 JSON 형식

---

#### 3.4.2 필터링 로직
**목적**: 사용자 필터 조건에 따른 데이터 필터링

**파일**: `apps/analytics/filters.py`

**함수 목록**:
1. `filter_by_date_range(queryset, start_date, end_date)`: 날짜 범위 필터
2. `filter_by_department(queryset, departments)`: 학과 필터
3. `filter_by_college(queryset, colleges)`: 단과대학 필터
4. `filter_by_journal_grade(queryset, grades)`: 저널 등급 필터
5. `filter_by_enrollment_status(queryset, statuses)`: 학적 상태 필터

**특징**:
- Django ORM Q 객체 활용
- 다중 필터 조합 지원
- 권한에 따른 자동 필터링 (일반 사용자는 소속 학과만)

---

#### 3.4.3 Chart.js용 데이터 Serializer
**목적**: Django 쿼리셋을 Chart.js 형식으로 변환

**파일**: `apps/analytics/serializers.py`

**함수 목록**:
1. `to_bar_chart_data(queryset, label_field, value_field)`: 막대 그래프 데이터
2. `to_line_chart_data(queryset, x_field, y_field)`: 라인 차트 데이터
3. `to_pie_chart_data(queryset, label_field, value_field)`: 파이 차트 데이터
4. `to_multi_dataset_chart_data(queryset, ...)`: 다중 데이터셋 차트

**반환 형식**:
```json
{
  "labels": ["공과대학", "인문대학", "사범대학"],
  "datasets": [{
    "label": "논문 게재 수",
    "data": [45, 32, 28],
    "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56"]
  }]
}
```

---

### 3.5 Utils 모듈

#### 3.5.1 날짜 헬퍼
**목적**: 날짜 관련 유틸리티 함수

**파일**: `apps/utils/date_helpers.py`

**함수 목록**:
1. `get_current_year()`: 현재 연도
2. `get_recent_years(n)`: 최근 N년 리스트
3. `format_date(date, format)`: 날짜 포맷팅
4. `parse_date(date_string)`: 문자열을 날짜로 변환
5. `get_academic_year()`: 현재 학년도 계산

---

#### 3.5.2 숫자 헬퍼
**목적**: 숫자 포맷팅 유틸리티

**파일**: `apps/utils/number_helpers.py`

**함수 목록**:
1. `format_number(num, decimal_places)`: 숫자 포맷팅 (천단위 구분)
2. `format_currency(amount)`: 통화 포맷팅 (억원, 만원)
3. `format_percentage(value)`: 퍼센트 포맷팅
4. `calculate_growth_rate(current, previous)`: 증감률 계산

---

#### 3.5.3 차트 헬퍼
**목적**: Chart.js 설정 헬퍼

**파일**: `apps/utils/chart_helpers.py`

**함수 목록**:
1. `get_default_chart_options()`: 기본 차트 옵션
2. `get_chart_colors(count)`: 차트 색상 팔레트 생성
3. `get_responsive_chart_config()`: 반응형 차트 설정

---

#### 3.5.4 내보내기 헬퍼
**목적**: CSV/Excel 내보내기 기능

**파일**: `apps/utils/export_helpers.py`

**함수 목록**:
1. `export_to_csv(queryset, fields, filename)`: CSV 내보내기
2. `export_to_excel(queryset, fields, filename)`: Excel 내보내기

---

### 3.6 템플릿 컴포넌트

#### 3.6.1 Base 레이아웃
**파일**: `templates/base/base.html`

**포함 요소**:
- `<head>` 설정 (메타태그, CSS, JS 라이브러리)
- Chart.js CDN
- Bootstrap 5 CDN (선택적)
- `{% block content %}` 블록

---

#### 3.6.2 Dashboard 레이아웃
**파일**: `templates/base/base_dashboard.html`

**상속**: `base.html`

**포함 요소**:
- 네비게이션 바
- 사이드바 메뉴
- 푸터
- `{% block dashboard_content %}` 블록

---

#### 3.6.3 재사용 컴포넌트

##### 3.6.3.1 네비게이션 바
**파일**: `templates/components/navbar.html`

**기능**:
- 로고 및 프로젝트명
- 사용자 정보 (이름, 소속)
- 로그아웃 버튼
- 프로필 링크

---

##### 3.6.3.2 사이드바 메뉴
**파일**: `templates/components/sidebar.html`

**메뉴 항목**:
1. 대시보드 (/dashboard)
2. 데이터 분석
   - 학과별 KPI (/analytics/department-kpi)
   - 논문 게재 (/analytics/publications)
   - 연구비 집행 (/analytics/research-budget)
   - 학생 현황 (/analytics/students)
3. 데이터 관리 (관리자 전용)
   - 데이터 업로드 (/admin)
   - 업로드 이력 (/data/history)
4. 사용자 관리 (관리자 전용)
   - 사용자 승인 (/admin/users/approval)
5. 내 정보
   - 프로필 (/profile)

**권한별 표시**:
- 일반 사용자: 대시보드, 데이터 분석, 내 정보만 표시
- 관리자: 전체 메뉴 표시

---

##### 3.6.3.3 필터 패널
**파일**: `templates/components/filter_panel.html`

**입력 요소**:
- 날짜 범위 선택
- 학과 선택 (드롭다운)
- 카테고리 선택 (체크박스)
- 적용/초기화 버튼

**기능**:
- 필터 값 변경 시 AJAX 요청으로 데이터 갱신
- URL 쿼리 파라미터 유지

---

##### 3.6.3.4 KPI 카드
**파일**: `templates/components/kpi_card.html`

**표시 내용**:
- 제목
- 현재 값
- 전년 대비 증감률
- 추세 아이콘 (↑, ↓, →)

**CSS 클래스**:
- `.kpi-card`
- `.kpi-value`
- `.kpi-change`
- `.kpi-trend`

---

##### 3.6.3.5 차트 래퍼
**파일**: `templates/components/chart_wrapper.html`

**구조**:
```html
<div class="chart-container">
  <div class="chart-header">
    <h3>{{ title }}</h3>
    <button class="chart-download">이미지 저장</button>
  </div>
  <canvas id="{{ chart_id }}"></canvas>
</div>
```

---

##### 3.6.3.6 데이터 테이블
**파일**: `templates/components/data_table.html`

**기능**:
- 정렬 가능한 컬럼 헤더
- 행 선택 (체크박스)
- 페이지네이션
- 검색 기능

---

##### 3.6.3.7 페이지네이션
**파일**: `templates/components/pagination.html`

**요소**:
- 이전/다음 버튼
- 페이지 번호
- 페이지 크기 선택

---

### 3.7 정적 파일

#### 3.7.1 CSS

##### 3.7.1.1 base.css
**파일**: `static/css/base.css`

**내용**:
- 전역 스타일 (폰트, 색상 변수)
- 리셋 CSS
- 기본 레이아웃

---

##### 3.7.1.2 components.css
**파일**: `static/css/components.css`

**내용**:
- 네비게이션 바 스타일
- 사이드바 스타일
- 버튼 스타일
- 카드 스타일
- 폼 요소 스타일

---

##### 3.7.1.3 charts.css
**파일**: `static/css/charts.css`

**내용**:
- 차트 컨테이너 스타일
- 반응형 차트 설정

---

#### 3.7.2 JavaScript

##### 3.7.2.1 chart-config.js
**파일**: `static/js/chart-config.js`

**내용**:
- Chart.js 기본 설정
- 공통 차트 옵션
- 색상 팔레트

**예시**:
```javascript
const CHART_COLORS = {
  primary: '#4e73df',
  success: '#1cc88a',
  info: '#36b9cc',
  warning: '#f6c23e',
  danger: '#e74a3b',
};

const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'bottom',
    },
    tooltip: {
      enabled: true,
    },
  },
};
```

---

##### 3.7.2.2 filter-handler.js
**파일**: `static/js/filter-handler.js`

**기능**:
- 필터 변경 이벤트 핸들링
- AJAX 요청으로 데이터 갱신
- URL 쿼리 파라미터 업데이트

---

##### 3.7.2.3 table-handler.js
**파일**: `static/js/table-handler.js`

**기능**:
- 테이블 정렬
- 테이블 검색
- 행 선택

---

##### 3.7.2.4 utils.js
**파일**: `static/js/utils.js`

**함수 목록**:
1. `formatNumber(num)`: 숫자 포맷팅
2. `formatDate(date)`: 날짜 포맷팅
3. `showMessage(type, message)`: 메시지 표시
4. `downloadChart(chartId, filename)`: 차트 이미지 다운로드

---

### 3.8 설정 파일

#### 3.8.1 Django 설정

##### 3.8.1.1 base.py
**파일**: `config/settings/base.py`

**주요 설정**:
- `INSTALLED_APPS`: Django 앱 목록
- `MIDDLEWARE`: 미들웨어 설정
- `TEMPLATES`: 템플릿 엔진 설정
- `DATABASES`: 데이터베이스 설정 (PostgreSQL)
- `AUTH_USER_MODEL`: 커스텀 User 모델 지정
- `STATIC_URL`, `MEDIA_URL`: 정적 파일 설정

---

##### 3.8.1.2 local.py
**파일**: `config/settings/local.py`

**주요 설정**:
- `DEBUG = True`
- 개발용 데이터베이스 설정 (Supabase 로컬)
- 개발용 이메일 백엔드

---

##### 3.8.1.3 production.py
**파일**: `config/settings/production.py`

**주요 설정**:
- `DEBUG = False`
- `ALLOWED_HOSTS`: Railway 도메인
- 프로덕션 데이터베이스 설정 (Supabase)
- 보안 설정 (HTTPS, HSTS 등)

---

#### 3.8.2 로깅 설정
**파일**: `config/logging.py`

**로거 목록**:
1. `django`: Django 기본 로그
2. `apps.data_upload`: 데이터 업로드 로그
3. `apps.authentication`: 인증 로그
4. `apps.analytics`: 데이터 분석 로그

**핸들러**:
- Console 핸들러 (개발 환경)
- File 핸들러 (프로덕션 환경)

---

## 4. 우선순위 및 작업 순서

### Phase 0: 프로젝트 기본 설정 (최우선)
**예상 소요 시간**: 1일

#### 0.1 Django 프로젝트 생성
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Django 및 필수 패키지 설치
pip install django psycopg2-binary python-dotenv pandas django-extensions
```

#### 0.2 Django 프로젝트 구조 생성
```bash
# Django 프로젝트 생성
django-admin startproject config .

# Django 앱 생성
python manage.py startapp core apps/core
python manage.py startapp authentication apps/authentication
python manage.py startapp data_upload apps/data_upload
python manage.py startapp analytics apps/analytics
python manage.py startapp utils apps/utils

# 디렉토리 구조 생성
mkdir -p templates/base templates/components templates/messages
mkdir -p static/css static/js
mkdir -p config/settings
```

#### 0.3 Supabase 데이터베이스 연결
```bash
# 로컬 Supabase 시작 (이미 연결되어 있음)
supabase start

# 마이그레이션 적용 확인
supabase db reset  # 스키마 재적용
```

#### 0.4 Django 데이터베이스 설정
**config/settings/base.py** 파일에 다음 추가:
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Supabase PostgreSQL 연결
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '54322',
    }
}

# Django 앱 등록
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 프로젝트 앱
    'apps.core',
    'apps.authentication',
    'apps.data_upload',
    'apps.analytics',
    'apps.utils',
]

# 커스텀 User 모델 지정 (Phase 2에서 구현)
# AUTH_USER_MODEL = 'authentication.User'
```

#### 0.5 환경 변수 설정
**.env** 파일 생성:
```env
# Django 설정
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase 로컬 DB
SUPABASE_DB_HOST=127.0.0.1
SUPABASE_DB_PORT=54322
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=postgres

# Supabase API (선택적)
SUPABASE_URL=https://vqwhekzhmhczdwrrbjke.supabase.co
SUPABASE_ANON_KEY=<from .env.local>
SUPABASE_SERVICE_ROLE_KEY=<from .env.local>
```

#### 0.6 Django 초기 마이그레이션
```bash
# Django 내장 앱 마이그레이션만 실행 (admin, auth, sessions 등)
python manage.py migrate

# Supabase 테이블은 이미 존재하므로 managed=False로 설정
```

#### 0.7 requirements.txt 작성
```txt
Django==4.2.7
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.1.3
openpyxl==3.1.2
xlrd==2.0.1
django-extensions==3.2.3
dj-database-url==2.1.0  # 프로덕션용
```

#### 0.8 프로젝트 구조 확인
```
vmc6/
├── apps/
│   ├── core/
│   ├── authentication/
│   ├── data_upload/
│   ├── analytics/
│   └── utils/
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
├── static/
├── supabase/
│   ├── migrations/
│   │   └── 20251102000000_initial_schema.sql
│   └── config.toml
├── .env
├── .env.local
├── manage.py
└── requirements.txt
```

#### 0.9 개발 서버 실행 테스트
```bash
# Django 개발 서버 실행
python manage.py runserver

# Supabase Studio 접속 (데이터 확인)
# http://127.0.0.1:54323
```

---

### Phase 1: Core 모듈 (우선순위: 최고)
**예상 소요 시간**: 2일

1. BaseModel 구현
2. 상수 정의 (constants.py)
3. 공통 Validator 구현
4. 커스텀 예외 정의
5. 권한 체크 데코레이터
6. 인증 미들웨어

**의존성**: 모든 다른 모듈이 Core 모듈에 의존

---

### Phase 2: Authentication 모듈 (우선순위: 최고)
**예상 소요 시간**: 2일

1. User 모델 구현
2. 인증 폼 (LoginForm, SignupForm)
3. 권한 체크 로직
4. 인증 뷰 (로그인, 회원가입, 로그아웃)
5. 인증 템플릿 (base_auth.html, 로그인 페이지, 회원가입 페이지)

**의존성**: Core 모듈

---

### Phase 3: 템플릿 기본 구조 (우선순위: 높음)
**예상 소요 시간**: 2일

1. base.html, base_dashboard.html 구현
2. 네비게이션 바, 사이드바 컴포넌트
3. 푸터 컴포넌트
4. 기본 CSS (base.css, components.css)

**의존성**: Authentication 모듈

---

### Phase 4: Data Upload 모듈 (우선순위: 높음)
**예상 소요 시간**: 3일

1. 데이터 모델 구현 (department_kpi, publications, research_projects, execution_records, students)
2. UploadHistory 모델
3. 파일 파서 (각 데이터 타입별)
4. 데이터 Validator
5. Django Admin 커스터마이징
6. 업로드 후처리 Signal

**의존성**: Core, Authentication 모듈

---

### Phase 5: Analytics 모듈 기본 (우선순위: 중간)
**예상 소요 시간**: 2일

1. 데이터 Aggregator (기본 통계)
2. 필터링 로직
3. Chart.js용 데이터 Serializer

**의존성**: Data Upload 모듈

---

### Phase 6: Utils 모듈 (우선순위: 중간)
**예상 소요 시간**: 1일

1. 날짜 헬퍼
2. 숫자 헬퍼
3. 차트 헬퍼
4. 내보내기 헬퍼

**의존성**: 없음 (독립적)

---

### Phase 7: 재사용 템플릿 컴포넌트 (우선순위: 중간)
**예상 소요 시간**: 2일

1. 필터 패널
2. KPI 카드
3. 차트 래퍼
4. 데이터 테이블
5. 페이지네이션

**의존성**: 템플릿 기본 구조

---

### Phase 8: JavaScript 유틸리티 (우선순위: 낮음)
**예상 소요 시간**: 1일

1. chart-config.js
2. filter-handler.js
3. table-handler.js
4. utils.js

**의존성**: 템플릿 컴포넌트

---

## 5. 검증 기준

각 모듈은 다음 기준을 충족해야 합니다:

### 5.1 코드 품질
- [ ] PEP 8 스타일 가이드 준수
- [ ] Docstring 작성 (모든 함수, 클래스)
- [ ] 타입 힌팅 (Python 3.9+)

### 5.2 테스트
- [ ] 유닛 테스트 작성 (핵심 로직)
- [ ] 테스트 커버리지 80% 이상

### 5.3 문서화
- [ ] 각 모듈의 README.md 작성
- [ ] API 문서화 (함수, 클래스 설명)

### 5.4 재사용성
- [ ] 특정 페이지에 의존하지 않음
- [ ] 파라미터화 가능
- [ ] 다른 모듈과의 결합도 낮음

---

## 6. 페이지별 개발 준비 완료 체크리스트

공통 모듈 개발이 완료되면, 각 페이지는 다음을 사용할 수 있어야 합니다:

### 6.1 인증 페이지 (로그인, 회원가입)
- [x] User 모델
- [x] 인증 폼 (LoginForm, SignupForm)
- [x] 인증 템플릿 (base_auth.html)
- [x] 공통 Validator (이메일, 비밀번호)

### 6.2 대시보드 페이지
- [x] base_dashboard.html
- [x] 네비게이션 바, 사이드바
- [x] KPI 카드 컴포넌트
- [x] 차트 래퍼 컴포넌트
- [x] 데이터 Aggregator
- [x] Chart.js 기본 설정

### 6.3 시각화 페이지 (학과별 KPI, 논문, 연구비, 학생)
- [x] base_dashboard.html
- [x] 필터 패널 컴포넌트
- [x] 차트 래퍼 컴포넌트
- [x] 데이터 테이블 컴포넌트
- [x] 페이지네이션 컴포넌트
- [x] 데이터 Aggregator
- [x] 필터링 로직
- [x] Chart.js용 Serializer
- [x] 내보내기 헬퍼

### 6.4 데이터 업로드 페이지 (Django Admin)
- [x] Django Admin 커스터마이징
- [x] 파일 파서
- [x] 데이터 Validator
- [x] UploadHistory 모델

### 6.5 사용자 관리 페이지 (프로필, 관리자)
- [x] User 모델
- [x] ProfileUpdateForm
- [x] PasswordChangeForm
- [x] 권한 체크 데코레이터

---

## 7. 주의사항 및 제약사항

### 7.1 Django Admin 활용
- **MVP 범위**: 파일 업로드는 Django Admin의 기본 기능만 사용
- **2단계 로드맵**: 사용자 친화적 UI는 향후 개발

### 7.2 인증 방식
- **MVP 범위**: Django 세션 기반 인증 사용
- **2단계 로드맵**: JWT 기반 인증은 API 전환 시 도입

### 7.3 API 개발
- **MVP 범위**: API 개발 없음 (Django 템플릿 렌더링)
- **2단계 로드맵**: Django Rest Framework 도입 예정

### 7.4 프론트엔드 프레임워크
- **MVP 범위**: React 등 프론트엔드 프레임워크 사용 안 함
- **2단계 로드맵**: React 분리 예정

### 7.5 파일 업로드 제한
- 최대 파일 크기: 50MB
- 지원 형식: `.xlsx`, `.xls`, `.csv`

### 7.6 브라우저 지원
- Chrome, Firefox, Safari, Edge 최신 버전

---

## 8. 다음 단계

공통 모듈 개발 완료 후, 다음 순서로 페이지 개발을 진행합니다:

1. **인증 페이지** (로그인, 회원가입)
2. **대시보드 페이지** (전체 KPI 요약)
3. **시각화 페이지** (병렬 개발 가능)
   - 학과별 KPI
   - 논문 게재
   - 연구비 집행
   - 학생 현황
4. **데이터 업로드 페이지** (Django Admin 커스터마이징)
5. **사용자 관리 페이지** (프로필, 관리자)

---

## 9. 문서 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성 | Claude Code |
| 1.1 | 2025-11-02 | Supabase 데이터베이스 설정 상세 추가<br>- 1.4 Supabase 데이터베이스 설정 섹션 추가<br>- Phase 0 Supabase 연결 절차 상세화<br>- Django-Supabase 통합 가이드 추가<br>- 마이그레이션 전략 명시 | Claude Code |

---

## 10. 참고 문서

- [Requirements](/Users/seunghyun/Test/vmc6/docs/requirements.md)
- [PRD](/Users/seunghyun/Test/vmc6/docs/prd.md)
- [UserFlow](/Users/seunghyun/Test/vmc6/docs/userflow.md)
- [Database](/Users/seunghyun/Test/vmc6/docs/database.md)
- [Technical Suggestion](/Users/seunghyun/Test/vmc6/docs/technical_suggestion.md)

---

**문서 작성 완료**
**다음 작업**: Phase 0 (프로젝트 기본 설정) 시작
