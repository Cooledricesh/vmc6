# Phase 0: Django 프로젝트 초기화 및 개발 환경 설정 - 구현 완료 보고서

## 1. 개요

대학교 데이터 시각화 대시보드 MVP 프로젝트의 Phase 0 (프로젝트 기본 설정)을 완료했습니다.

- **프로젝트명**: vmc6 (University Data Visualization Dashboard)
- **기술 스택**: Django 4.2.7 + PostgreSQL (Supabase) + Chart.js
- **개발 환경**: Python 3.9, macOS
- **프로덕션**: Railway
- **완료 일시**: 2025-11-02

## 2. 완료된 작업

### 2.1 가상환경 및 패키지 설치 ✓

#### 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 설치된 패키지 (requirements.txt)
```
Django==4.2.7
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.1.3
openpyxl==3.1.2
xlrd==2.0.1
django-extensions==3.2.3
dj-database-url==2.1.0
```

### 2.2 Django 프로젝트 구조 생성 ✓

```
vmc6/
├── apps/                          # 5개 Django 앱
│   ├── __init__.py
│   ├── core/                      # 공통 기능 (constants, decorators, validators, exceptions, middleware)
│   ├── authentication/            # 사용자 인증 (User 모델, 로그인, 회원가입, 권한)
│   ├── data_upload/              # 파일 업로드 (파서, 검증, Django Admin 커스터마이징)
│   ├── analytics/                # 데이터 분석 (집계, 필터, Chart.js 직렬화)
│   └── utils/                    # 유틸리티 (날짜, 숫자, 차트, 내보내기 헬퍼)
│
├── config/                        # Django 설정
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py                   # production 환경으로 설정됨
│   ├── urls.py                   # 메인 URL 라우팅
│   └── settings/
│       ├── __init__.py
│       ├── base.py               # 기본 설정 (모든 환경 공용)
│       ├── local.py              # 로컬 개발 환경 설정
│       └── production.py         # Railway 프로덕션 환경 설정
│
├── templates/                     # Django 템플릿 디렉토리 생성
│   ├── base/                     # 기본 레이아웃 (생성 예정)
│   ├── components/               # 재사용 컴포넌트 (생성 예정)
│   └── messages/                 # 메시지 템플릿 (생성 예정)
│
├── static/                        # 정적 파일 디렉토리
│   ├── css/                      # 스타일시트 (생성 예정)
│   └── js/                       # JavaScript (생성 예정)
│
├── logs/                          # 로그 디렉토리
│   └── .gitkeep
│
├── supabase/                      # Supabase 설정
│   ├── migrations/               # DB 스키마 마이그레이션
│   └── config.toml               # Supabase 로컬 설정
│
├── docs/                          # 프로젝트 문서
│   ├── requirements.md
│   ├── prd.md
│   ├── database.md
│   ├── userflow.md
│   └── common-modules.md
│
├── manage.py                      # Django 관리 스크립트 (config.settings.local 사용)
├── requirements.txt               # Python 의존성
├── .env                           # 환경 변수 (로컬)
├── .gitignore                     # Git 무시 파일
├── CLAUDE.md                      # 개발 가이드
└── SETUP.md                       # 초기화 가이드
```

### 2.3 Django 설정 파일 구조 (config/settings/) ✓

#### base.py (기본 설정 - 모든 환경 공용)
```python
# 주요 설정:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'apps.core',
    'apps.authentication',
    'apps.data_upload',
    'apps.analytics',
    'apps.utils',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SUPABASE_DB_NAME', 'postgres'),
        'USER': os.environ.get('SUPABASE_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('SUPABASE_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '54322'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 프로젝트 전체 템플릿 디렉토리
        'APP_DIRS': True,
        ...
    },
]

# 국제화 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# 정적/미디어 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 로깅 설정 (4개 로거: django, authentication, data_upload, analytics)
```

#### local.py (로컬 개발 환경)
```python
# 특징:
DEBUG = True
ALLOWED_HOSTS = ['*']

# Supabase 로컬 DB (포트 54322)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('SUPABASE_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '54322'),
        ...
    }
}

# 개발용 이메일 (콘솔 출력)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 로깅 레벨: DEBUG
```

#### production.py (프로덕션 환경 - Railway)
```python
# 특징:
DEBUG = False

# HTTPS 보안 설정
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# DATABASE_URL 지원 (Railway)
DATABASES['default'] = dj_database_url.config(
    default=os.environ.get('DATABASE_URL'),
    conn_max_age=600,
    conn_health_checks=True,
)

# SMTP 이메일 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# WhiteNoise 정적 파일 처리
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 로깅 레벨: WARNING (성능 최적화)
```

### 2.4 환경 변수 설정 ✓

#### .env 파일 (로컬 개발용)
```bash
# Django
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Supabase 로컬 DB
SUPABASE_DB_HOST=127.0.0.1
SUPABASE_DB_PORT=54322
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=postgres

# 프로덕션 환경 변수 (주석 처리, 필요시 활성화)
# DATABASE_URL=postgresql://...
# SUPABASE_URL=https://...
# EMAIL_HOST, EMAIL_PORT, etc.
```

**특징:**
- `python-dotenv`로 자동 로드 (config/settings/base.py)
- `.gitignore`에 포함되어 있어 민감 정보 보호
- 로컬/프로덕션 환경 자동 구분

### 2.5 Django 설정 검증 ✓

```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

**검증 내용:**
- 5개 프로젝트 앱 모두 정상 로드됨
- 데이터베이스 설정 정상
- 템플릿 설정 정상
- 미들웨어 설정 정상
- 권한/인증 설정 정상

### 2.6 파일 구조 완성 ✓

**생성된 디렉토리:**
- apps/ (5개 앱 + migrations/)
- config/settings/ (base, local, production)
- templates/ (base, components, messages)
- static/ (css, js)
- logs/

**생성된 파일:**
- requirements.txt
- .env
- SETUP.md (초기화 가이드)
- PHASE0_IMPLEMENTATION_SUMMARY.md (이 파일)

## 3. 기술 스택 확인

### 백엔드
- Django 4.2.7: 안정적인 LTS 버전
- PostgreSQL 14+: Supabase 기반
- Python 3.9+: 최신 안정 버전

### 데이터 처리
- Pandas 2.1.3: CSV/Excel 파싱
- openpyxl 3.1.2: Excel 파일 쓰기
- xlrd 2.0.1: Excel 파일 읽기

### 프론트엔드 (Phase 1~에서 생성)
- Django 템플릿: 서버사이드 렌더링
- Chart.js: 데이터 시각화 (CDN)
- Bootstrap 5: 스타일링 (선택사항)

### 배포
- Railway: 클라우드 호스팅
- WhiteNoise: 정적 파일 서빙
- Gunicorn: WSGI 앱 서버

## 4. 주요 설계 결정

### 4.1 Supabase-First 아키텍처
- **Schema는 Supabase 마이그레이션으로 관리** (`supabase/migrations/*.sql`)
- **Django 모델은 `managed = False`로 설정** (Django가 스키마 변경 안 함)
- **Django migrations는 내장 앱(admin, auth, sessions)에만 사용**

### 4.2 설정 파일 3단계 구조
- base.py: 모든 환경 공용
- local.py: 로컬 개발 (DEBUG=True, ALLOWED_HOSTS=['*'])
- production.py: Railway (DEBUG=False, HTTPS, WhiteNoise)

### 4.3 환경 변수 관리
- python-dotenv로 .env 파일 자동 로드
- 민감 정보 분리 (시크릿키, DB 비밀번호 등)
- 로컬/프로덕션 환경 자동 구분

### 4.4 로깅 설정
- 4개 로거 (django, authentication, data_upload, analytics)
- 콘솔 + 파일 핸들러
- 환경별 로그 레벨 구분 (LOCAL: DEBUG, PROD: WARNING)

## 5. 다음 단계 (Phase 1)

### 즉시 필요한 작업
1. **Supabase 로컬 환경 시작**
   ```bash
   supabase start
   ```

2. **Django 마이그레이션 실행**
   ```bash
   python manage.py migrate
   ```

3. **슈퍼유저 생성**
   ```bash
   python manage.py createsuperuser
   ```

4. **개발 서버 시작**
   ```bash
   python manage.py runserver
   ```

### Phase 1: Core 모듈 구현 (우선순위: 최고)
1. BaseModel 구현 (apps/core/models.py)
2. 상수 정의 (apps/core/constants.py)
3. 공통 Validator (apps/core/validators.py)
4. 커스텀 예외 (apps/core/exceptions.py)
5. 권한 체크 데코레이터 (apps/core/decorators.py)
6. 인증 미들웨어 (apps/core/middleware.py)

**예상 소요 시간**: 2일

## 6. 보안 체크리스트

### 현재 상태
- [x] .env 파일이 .gitignore에 포함됨
- [x] SECRET_KEY가 환경 변수로 분리됨
- [x] 프로덕션 설정에서 DEBUG = False
- [x] ALLOWED_HOSTS가 환경별로 구분됨

### 프로덕션 배포 전 확인사항
- [ ] SECRET_KEY를 안전한 값으로 변경
- [ ] ALLOWED_HOSTS에 실제 도메인 설정
- [ ] DATABASE_URL 설정 (Railway에서 제공)
- [ ] HTTPS 인증서 설정 (Let's Encrypt)
- [ ] 이메일 서버 설정 (SMTP)

## 7. 주의사항

### 중요: Supabase 마이그레이션
```python
# ✓ 올바른 방법: Supabase 마이그레이션으로 스키마 변경
# supabase/migrations/20251102000000_add_column.sql 생성

# ✗ 잘못된 방법: Django 마이그레이션으로 스키마 변경
# python manage.py makemigrations  # 금지!
```

### Django 모델 규칙
```python
class User(models.Model):
    class Meta:
        db_table = 'users'         # Supabase 테이블명과 일치
        managed = False            # Django가 스키마 관리 안 함

    # managed = False일 때:
    # - CREATE TABLE: Django가 하지 않음
    # - ALTER TABLE: Django가 하지 않음
    # - DROP TABLE: Django가 하지 않음
```

## 8. 문제 해결 가이드

### PostgreSQL 연결 실패
```
psycopg2.OperationalError: connection to server at "127.0.0.1", port 54322 failed
```

**해결:**
```bash
# Supabase 상태 확인
supabase status

# Supabase 재시작
supabase stop
supabase start

# 포트 충돌 확인
lsof -i :54322
```

### 앱 import 실패
```
ModuleNotFoundError: No module named 'apps.core'
```

**해결:**
1. apps.py의 name이 올바른지 확인 (예: `name = 'apps.core'`)
2. __init__.py 파일 확인

### 환경 변수 인식 안 됨
**해결:**
1. .env 파일이 프로젝트 루트에 있는지 확인
2. load_dotenv() 위치 확인 (config/settings/base.py)

## 9. 참고 자료

### 프로젝트 문서
- `/Users/seunghyun/Test/vmc6/CLAUDE.md` - 전체 개발 가이드
- `/Users/seunghyun/Test/vmc6/SETUP.md` - 초기화 및 실행 가이드
- `/Users/seunghyun/Test/vmc6/docs/common-modules.md` - 공통 모듈 아키텍처
- `/Users/seunghyun/Test/vmc6/docs/database.md` - 데이터베이스 설계

### 외부 자료
- Django 공식 문서: https://docs.djangoproject.com/en/4.2/
- Supabase 공식 문서: https://supabase.com/docs
- PostgreSQL 공식 문서: https://www.postgresql.org/docs/

## 10. 파일 목록 및 경로

### 핵심 설정 파일
| 파일 | 경로 | 설명 |
|------|------|------|
| manage.py | `/Users/seunghyun/Test/vmc6/manage.py` | Django 관리 스크립트 |
| base.py | `/Users/seunghyun/Test/vmc6/config/settings/base.py` | 기본 설정 |
| local.py | `/Users/seunghyun/Test/vmc6/config/settings/local.py` | 로컬 개발 설정 |
| production.py | `/Users/seunghyun/Test/vmc6/config/settings/production.py` | 프로덕션 설정 |
| wsgi.py | `/Users/seunghyun/Test/vmc6/config/wsgi.py` | WSGI 앱 (production) |
| .env | `/Users/seunghyun/Test/vmc6/.env` | 환경 변수 |
| requirements.txt | `/Users/seunghyun/Test/vmc6/requirements.txt` | Python 의존성 |

### 프로젝트 앱
| 앱 | 경로 | 용도 |
|----|------|------|
| core | `/Users/seunghyun/Test/vmc6/apps/core/` | 공통 기능 |
| authentication | `/Users/seunghyun/Test/vmc6/apps/authentication/` | 인증/인가 |
| data_upload | `/Users/seunghyun/Test/vmc6/apps/data_upload/` | 파일 업로드 |
| analytics | `/Users/seunghyun/Test/vmc6/apps/analytics/` | 데이터 분석 |
| utils | `/Users/seunghyun/Test/vmc6/apps/utils/` | 유틸리티 |

## 11. 요약

### 완료 상황
- ✓ 가상환경 생성 및 패키지 설치
- ✓ Django 프로젝트 구조 생성
- ✓ 5개 프로젝트 앱 생성
- ✓ config/settings/ 3단계 설정 구조
- ✓ 환경 변수 설정
- ✓ Django 설정 검증 (System check: OK)
- ✓ 디렉토리 구조 완성

### 대기 중인 작업
- ⏳ Supabase 로컬 환경 시작
- ⏳ Django 마이그레이션 실행
- ⏳ 슈퍼유저 생성
- ⏳ 개발 서버 테스트

### 상태
**Phase 0 완료** → **Phase 1 대기 중**

다음: Core 모듈 구현 (Phase 1)

---

**작성일**: 2025-11-02
**작성자**: Claude Code
**상태**: ✓ 완료
