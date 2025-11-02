# Phase 0: Django 프로젝트 초기화 및 개발 환경 설정

이 문서는 Django 프로젝트의 초기 설정 과정을 설명합니다.

## 완료된 작업

### 1. 가상환경 생성 및 패키지 설치 ✓
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**설치된 패키지:**
- Django 4.2.7
- psycopg2-binary 2.9.9 (PostgreSQL 드라이버)
- python-dotenv 1.0.0 (환경 변수 관리)
- pandas 2.1.3 (데이터 처리)
- openpyxl 3.1.2 (Excel 파일 처리)
- xlrd 2.0.1 (Excel 읽기)
- django-extensions 3.2.3 (Django 유틸리티)
- dj-database-url 2.1.0 (DATABASE_URL 파싱)

### 2. Django 프로젝트 구조 생성 ✓

```
vmc6/
├── apps/                           # Django 앱 디렉토리
│   ├── __init__.py
│   ├── core/                       # 핵심 공통 기능 모듈
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   ├── decorators.py          # 권한 체크 데코레이터
│   │   ├── validators.py          # 공통 검증 로직
│   │   ├── exceptions.py          # 커스텀 예외
│   │   ├── constants.py           # 상수 정의
│   │   ├── middleware.py          # 커스텀 미들웨어
│   │   └── migrations/
│   │
│   ├── authentication/             # 인증/인가 모듈
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py              # User 모델
│   │   ├── forms.py               # 로그인, 회원가입 폼
│   │   ├── views.py               # 인증 뷰
│   │   ├── backends.py            # 커스텀 인증 백엔드
│   │   ├── permissions.py         # 권한 체크 로직
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   ├── data_upload/                # 데이터 업로드 모듈
│   │   ├── __init__.py
│   │   ├── admin.py               # Django Admin 커스터마이징
│   │   ├── apps.py
│   │   ├── models.py              # UploadHistory 모델
│   │   ├── forms.py
│   │   ├── views.py
│   │   ├── parsers.py             # Excel/CSV 파싱
│   │   ├── validators.py          # 데이터 검증
│   │   ├── signals.py             # 업로드 후처리
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   ├── analytics/                  # 데이터 분석 및 시각화
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py              # KPI, Publication 등 데이터 모델
│   │   ├── views.py               # 시각화 뷰
│   │   ├── aggregators.py         # 데이터 집계
│   │   ├── filters.py             # 필터링 로직
│   │   ├── serializers.py         # Chart.js 직렬화
│   │   ├── tests.py
│   │   └── migrations/
│   │
│   └── utils/                      # 유틸리티 모듈
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── date_helpers.py        # 날짜 헬퍼
│       ├── number_helpers.py      # 숫자 포맷팅
│       ├── chart_helpers.py       # Chart.js 헬퍼
│       ├── export_helpers.py      # CSV/Excel 내보내기
│       ├── tests.py
│       └── migrations/
│
├── config/                          # Django 설정
│   ├── __init__.py
│   ├── wsgi.py                     # WSGI 애플리케이션
│   ├── asgi.py                     # ASGI 애플리케이션
│   ├── urls.py                     # URL 라우팅
│   └── settings/
│       ├── __init__.py
│       ├── base.py                 # 기본 설정 (모든 환경 공용)
│       ├── local.py                # 로컬 개발 환경 설정
│       └── production.py           # 프로덕션 환경 설정
│
├── templates/                       # Django 템플릿
│   ├── base/
│   │   ├── base.html               # 전체 레이아웃 기본
│   │   ├── base_dashboard.html     # 대시보드 레이아웃
│   │   └── base_auth.html          # 인증 페이지 레이아웃
│   │
│   ├── components/                 # 재사용 컴포넌트
│   │   ├── navbar.html             # 네비게이션 바
│   │   ├── sidebar.html            # 사이드바 메뉴
│   │   ├── footer.html             # 푸터
│   │   ├── filter_panel.html       # 필터 패널
│   │   ├── kpi_card.html           # KPI 카드
│   │   ├── chart_wrapper.html      # 차트 래퍼
│   │   ├── data_table.html         # 데이터 테이블
│   │   └── pagination.html         # 페이지네이션
│   │
│   └── messages/                   # 메시지 템플릿
│       ├── success.html
│       ├── error.html
│       └── warning.html
│
├── static/                          # 정적 파일
│   ├── css/
│   │   ├── base.css               # 기본 스타일
│   │   ├── components.css         # 컴포넌트 스타일
│   │   ├── dashboard.css          # 대시보드 스타일
│   │   └── charts.css             # 차트 스타일
│   │
│   └── js/
│       ├── chart-config.js        # Chart.js 기본 설정
│       ├── filter-handler.js      # 필터 핸들러
│       ├── table-handler.js       # 테이블 정렬/검색
│       └── utils.js               # 유틸리티 함수
│
├── logs/                            # 로그 디렉토리
│   └── .gitkeep
│
├── media/                           # 업로드 파일 저장소 (생성 예정)
│
├── staticfiles/                     # 수집된 정적 파일 (생성 예정)
│
├── supabase/                        # Supabase 설정
│   ├── migrations/                 # DB 마이그레이션 (Supabase 관리)
│   │   └── 20251102000000_initial_schema.sql
│   └── config.toml
│
├── docs/                            # 문서
│   ├── requirements.md
│   ├── prd.md
│   ├── database.md
│   ├── userflow.md
│   ├── common-modules.md
│   ├── technical_suggestion.md
│   └── pages/
│
├── manage.py                        # Django 관리 명령어
├── requirements.txt                 # Python 의존성
├── .env                             # 환경 변수 (로컬)
├── .env.local                       # Supabase 환경 변수 (선택)
├── .gitignore                       # Git 무시 파일
├── CLAUDE.md                        # 개발 가이드
└── SETUP.md                         # 이 파일

```

### 3. Django 설정 파일 구조 생성 ✓

**config/settings/ 디렉토리 구조:**

- `base.py`: 모든 환경에서 공용되는 기본 설정
  - DATABASE: PostgreSQL (Supabase)
  - INSTALLED_APPS: 5개 프로젝트 앱 + django_extensions
  - TEMPLATES: templates/ 디렉토리 설정
  - STATIC/MEDIA: 정적 파일 및 미디어 설정
  - LOGGING: 로깅 설정

- `local.py`: 로컬 개발 환경 설정
  - DEBUG = True
  - ALLOWED_HOSTS = ['*']
  - Supabase 로컬 DB (포트 54322)
  - 콘솔 이메일 백엔드
  - DEBUG 레벨 로깅

- `production.py`: 프로덕션 환경 설정
  - DEBUG = False
  - HTTPS 보안 설정 (HSTS, SSL 리디렉션)
  - Railway DATABASE_URL 지원
  - SMTP 이메일 설정
  - WhiteNoise 정적 파일 처리

### 4. 환경 변수 설정 ✓

`.env` 파일 생성 (로컬 개발 용):
```bash
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

SUPABASE_DB_HOST=127.0.0.1
SUPABASE_DB_PORT=54322
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=postgres
```

**환경 변수의 역할:**
- Django 설정에서 `os.environ.get()`으로 읽어옴
- 로컬/프로덕션 환경을 구분하여 자동 적용
- 민감 정보(SECRET_KEY, DB 비밀번호 등)를 코드에서 분리

### 5. Django 설정 검증 ✓

```bash
source venv/bin/activate
python manage.py check
# Output: System check identified no issues (0 silenced).
```

## 다음 단계: Supabase 연결 및 마이그레이션

### 1. Supabase 로컬 환경 시작

```bash
# Supabase 시작
supabase start

# 포트 확인:
# - PostgreSQL: 54322
# - Supabase Studio (GUI): http://127.0.0.1:54323
# - API Gateway: 54321
```

### 2. Django 마이그레이션 실행

```bash
# Django 내장 앱 마이그레이션만 실행 (admin, auth, sessions, etc.)
python manage.py migrate

# 마이그레이션 상태 확인
python manage.py showmigrations
```

### 3. 슈퍼유저 생성

```bash
# Django admin 접근용 슈퍼유저 생성
python manage.py createsuperuser

# 프롬프트:
# Username: admin
# Email: admin@example.com
# Password: ****
```

### 4. 개발 서버 시작

```bash
python manage.py runserver

# 접근 주소:
# - 앱: http://127.0.0.1:8000
# - Django Admin: http://127.0.0.1:8000/admin
# - Supabase Studio: http://127.0.0.1:54323
```

## 프로덕션 배포 (Railway)

### 환경 변수 설정 (Railway Dashboard)

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app

DATABASE_URL=postgresql://user:password@host:port/dbname
```

### 배포 명령어

```bash
# staticfiles 수집
python manage.py collectstatic --noinput

# 마이그레이션 실행
python manage.py migrate

# Gunicorn으로 실행 (Procfile 사용)
```

## 주의사항

### 중요: Supabase 마이그레이션

- **Schema는 Supabase 마이그레이션으로 관리** (`supabase/migrations/*.sql`)
- **Django 모델은 `managed = False`로 설정** (Django가 스키마 변경하지 않음)
- Django migrations는 내장 앱(admin, auth, sessions)에만 사용

### 보안 체크리스트

- [ ] `.env` 파일은 `.gitignore`에 포함됨 (안전함)
- [ ] 프로덕션에서 SECRET_KEY 변경
- [ ] 프로덕션에서 DEBUG = False
- [ ] 프로덕션에서 ALLOWED_HOSTS 설정
- [ ] HTTPS 활성화
- [ ] CSRF_COOKIE_SECURE = True (프로덕션)
- [ ] SESSION_COOKIE_SECURE = True (프로덕션)

## 문제 해결

### 1. PostgreSQL 연결 실패

```bash
# Supabase 상태 확인
supabase status

# Supabase 중지 후 재시작
supabase stop
supabase start

# 포트 54322 이미 사용 중인 경우
lsof -i :54322
kill -9 <PID>
```

### 2. Django 앱 import 실패

```bash
# 각 앱의 apps.py에서 name 확인
# 예: name = 'apps.core' (not 'core')

# __init__.py 파일 확인
find apps -type d -exec touch {}/__init__.py \;
```

### 3. 환경 변수 인식 안 됨

```bash
# .env 파일이 프로젝트 루트에 있는지 확인
cat .env

# load_dotenv() 위치 확인 (config/settings/base.py)
```

## 참고 자료

- CLAUDE.md: 프로젝트 전체 개발 가이드
- docs/common-modules.md: 공통 모듈 아키텍처
- docs/database.md: 데이터베이스 설계
- docs/prd.md: 제품 요구사항

---

**작성일**: 2025-11-02
**상태**: Phase 0 완료, Phase 1 대기 중
