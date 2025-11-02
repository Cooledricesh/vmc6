# Django TDD 구현 가이드

## 개요

Django 인증 기능을 TDD(Test-Driven Development) 방식으로 구현하기 위한 완전 가이드입니다.
**46개의 테스트가 이미 작성**되어 있으며, RED → GREEN → REFACTOR 사이클을 따라 구현하면 됩니다.

---

## 📚 목차

1. [5분 빠른 시작](#5분-빠른-시작)
2. [TDD 사이클 이해](#tdd-사이클-이해)
3. [Phase별 구현 로드맵](#phase별-구현-로드맵)
4. [Django TestCase 활용법](#django-testcase-활용법)
5. [실전 명령어 모음](#실전-명령어-모음)
6. [FAQ 및 문제 해결](#faq-및-문제-해결)

---

## 5분 빠른 시작

### Step 1: 첫 테스트 실행 (RED)

```bash
cd /Users/seunghyun/Test/vmc6

# 첫 번째 테스트 실행 - 실패할 것 (정상!)
python manage.py test apps.authentication.tests.test_models.UserModelTest.test_user_creation_with_required_fields
```

**예상 결과**: `ImportError: cannot import name 'User'` - 이게 RED 단계입니다!

### Step 2: User 모델 구현 (GREEN)

`/Users/seunghyun/Test/vmc6/apps/authentication/models.py` 파일 생성:

```python
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    """사용자 모델"""

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    email = models.EmailField(unique=True, db_column='email')
    password = models.CharField(max_length=255, db_column='password')
    name = models.CharField(max_length=100, db_column='name')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        db_column='role'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_column='status'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='department'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='position'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'users'
        managed = False  # Supabase가 스키마 관리

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """비밀번호 해싱"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """비밀번호 검증"""
        return check_password(raw_password, self.password)

    def is_active_user(self):
        """활성 사용자 여부"""
        return self.status == 'active'

    def can_access_department(self, dept_name):
        """학과 접근 권한"""
        if self.role in ['admin', 'manager']:
            return True
        return self.department == dept_name
```

### Step 3: 테스트 재실행 (GREEN 확인)

```bash
# 단일 테스트
python manage.py test apps.authentication.tests.test_models.UserModelTest.test_user_creation_with_required_fields

# 모든 User 모델 테스트
python manage.py test apps.authentication.tests.test_models
```

**예상 결과**: `Ran 8 tests OK` - GREEN 달성!

### Step 4: 커밋

```bash
git add apps/authentication/models.py
git commit -m "test: User 모델 구현 - 8개 테스트 통과"
```

축하합니다! 첫 TDD 사이클을 완료했습니다.

---

## TDD 사이클 이해

### RED → GREEN → REFACTOR

```
┌─────────────────────────────────────────────┐
│  1. RED (테스트 먼저)                        │
│     - 테스트 작성                           │
│     - 실행 → 실패 확인                      │
│     - 실패 메시지 기록                      │
├─────────────────────────────────────────────┤
│  2. GREEN (최소 구현)                        │
│     - 최소한의 코드 작성                    │
│     - 테스트 통과만 목표                    │
│     - 다른 테스트 깨지지 않음 확인          │
├─────────────────────────────────────────────┤
│  3. REFACTOR (개선)                          │
│     - 코드 정리 (변수명, 주석)              │
│     - 중복 제거                             │
│     - 테스트 재실행 → 여전히 통과           │
├─────────────────────────────────────────────┤
│  4. COMMIT                                   │
│     - git add & commit                      │
│     - 작은 단위로 자주                      │
└─────────────────────────────────────────────┘
```

### TDD 핵심 원칙

1. **테스트가 먼저다** - 구현 전에 항상 테스트 작성
2. **작은 단위로** - 한 번에 한 테스트, 한 기능만
3. **RED는 정상이다** - 실패하지 않으면 TDD가 아님
4. **테스트가 스펙이다** - 테스트가 요구사항 정의

---

## Phase별 구현 로드맵

총 **46개 테스트**, **7개 Phase**로 구성:

### Phase 1: User 모델 ✅ (8개 테스트)
- **파일**: `apps/authentication/tests/test_models.py`
- **구현**: `apps/authentication/models.py`
- **시간**: 약 3시간
- **명령**: `python manage.py test apps.authentication.tests.test_models`

### Phase 2: SignupForm (8개 테스트)
- **파일**: `apps/authentication/tests/test_forms.py`
- **구현**: `apps/authentication/forms.py`
- **시간**: 약 2시간
- **명령**: `python manage.py test apps.authentication.tests.test_forms.SignupFormTest`

### Phase 3: SignupView (5개 테스트)
- **파일**: `apps/authentication/tests/test_views.py`
- **구현**: `apps/authentication/views.py`, `templates/auth/signup.html`
- **시간**: 약 2시간
- **명령**: `python manage.py test apps.authentication.tests.test_views.SignupViewTest`

### Phase 4: LoginForm & LoginView (13개 테스트)
- **파일**: `test_forms.py` (7개), `test_views.py` (6개)
- **구현**: `forms.py`, `views.py`, `templates/auth/login.html`
- **시간**: 약 3시간
- **명령**:
  ```bash
  python manage.py test apps.authentication.tests.test_forms.LoginFormTest
  python manage.py test apps.authentication.tests.test_views.LoginViewTest
  ```

### Phase 5: LogoutView (2개 테스트)
- **파일**: `apps/authentication/tests/test_views.py`
- **구현**: `views.py`, `urls.py`
- **시간**: 약 1시간
- **명령**: `python manage.py test apps.authentication.tests.test_views.LogoutViewTest`

### Phase 6: 권한 데코레이터 (6개 테스트)
- **파일**: `apps/core/tests/test_decorators.py`
- **구현**: `apps/core/decorators.py`
- **시간**: 약 2시간
- **명령**: `python manage.py test apps.core.tests.test_decorators`

### Phase 7: 세션 미들웨어 (4개 테스트)
- **파일**: `apps/core/tests/test_middleware.py`
- **구현**: `apps/core/middleware.py`, `config/settings.py`
- **시간**: 약 1시간
- **명령**: `python manage.py test apps.core.tests.test_middleware`

---

## Django TestCase 활용법

### 기본 TestCase 사용

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User

class UserModelTest(TestCase):
    def setUp(self):
        """각 테스트 전 실행"""
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트 사용자'
        )
        self.user.set_password('test1234')
        self.user.save()

    def test_password_is_hashed(self):
        """비밀번호 해싱 테스트"""
        self.assertNotEqual(self.user.password, 'test1234')
        self.assertTrue(self.user.check_password('test1234'))
```

### HTTP 요청 테스트

```python
class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

    def test_login_success(self):
        """로그인 성공 테스트"""
        response = self.client.post(self.login_url, {
            'email': 'test@university.ac.kr',
            'password': 'test1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
```

### 주요 Assertion 메서드

```python
# 상태 코드
self.assertEqual(response.status_code, 200)

# 리디렉션
self.assertRedirects(response, reverse('login'))

# 템플릿
self.assertTemplateUsed(response, 'auth/login.html')

# 콘텐츠
self.assertContains(response, '로그인')
self.assertNotContains(response, 'Error')

# 데이터베이스
self.assertTrue(User.objects.filter(email='test@university.ac.kr').exists())
self.assertEqual(User.objects.count(), 1)

# 세션
self.assertIn('_auth_user_id', self.client.session)
```

---

## 실전 명령어 모음

### 테스트 실행

```bash
# 전체 테스트
python manage.py test apps.authentication apps.core

# 특정 앱
python manage.py test apps.authentication

# 특정 파일
python manage.py test apps.authentication.tests.test_models

# 특정 클래스
python manage.py test apps.authentication.tests.test_models.UserModelTest

# 특정 메서드
python manage.py test apps.authentication.tests.test_models.UserModelTest.test_user_creation_with_required_fields

# Verbose 모드
python manage.py test apps.authentication -v 2

# DB 유지 (빠른 재실행)
python manage.py test apps.authentication --keepdb
```

### 커버리지 측정

```bash
# 설치
pip install coverage

# 실행
coverage run --source='apps' manage.py test apps
coverage report
coverage html  # htmlcov/index.html에서 확인
```

---

## FAQ 및 문제 해결

### Q: 테스트가 실패하는데 이게 맞나요?

**A**: 네, RED 단계에서는 실패가 정상입니다! 이제 구현 코드를 작성하세요.

### Q: "managed = False"가 뭔가요?

**A**: Supabase가 데이터베이스 스키마를 관리하므로 Django는 테이블을 생성/수정하지 않습니다.

### Q: 테스트가 너무 느려요

**A**:
1. `--keepdb` 옵션 사용
2. 불필요한 필드 저장 최소화
3. 외부 API는 Mock 사용

### Q: IntegrityError가 발생해요

**A**: 테스트 간 데이터 충돌입니다. 각 테스트에서 고유한 이메일 사용:
```python
def test_user_1(self):
    user = User.objects.create(email='test1@university.ac.kr', ...)

def test_user_2(self):
    user = User.objects.create(email='test2@university.ac.kr', ...)
```

### Q: 어떤 순서로 구현해야 하나요?

**A**: Phase 1 → 2 → 3 순서대로. 각 Phase는 이전 Phase에 의존합니다.

---

## 체크리스트

### 각 Cycle 체크리스트

```
□ RED: 테스트 실행 → 실패 확인
□ GREEN: 최소 코드 작성 → 테스트 통과
□ REFACTOR: 코드 개선 → 테스트 여전히 통과
□ COMMIT: git add & commit
```

### Phase 완료 체크리스트

```
□ 해당 Phase 모든 테스트 통과
□ 다른 Phase 테스트 영향 없음
□ 코드 리뷰 완료
□ 커밋 완료
```

### 전체 완료 체크리스트

```
□ 46개 테스트 모두 통과
□ 커버리지 80% 이상
□ 보안 검토 (비밀번호 해싱, CSRF 등)
□ 문서 업데이트
```

---

## 테스트 파일 위치

```
/Users/seunghyun/Test/vmc6/
├── apps/
│   ├── authentication/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py      # 8개 테스트
│   │   │   ├── test_forms.py       # 15개 테스트
│   │   │   └── test_views.py       # 13개 테스트
│   │   ├── models.py               # 구현할 파일
│   │   ├── forms.py                # 구현할 파일
│   │   └── views.py                # 구현할 파일
│   └── core/
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── test_decorators.py  # 6개 테스트
│       │   └── test_middleware.py  # 4개 테스트
│       ├── decorators.py           # 구현할 파일
│       └── middleware.py           # 구현할 파일
└── templates/
    └── auth/                       # 템플릿 구현
        ├── login.html
        └── signup.html
```

---

## 참고 문서

- [원본 계획 문서](/docs/pages/01-auth/plan.md)
- [Django 공식 테스트 문서](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Python unittest 문서](https://docs.python.org/3/library/unittest.html)

---

**준비 상태**: ✅ 46개 테스트 작성 완료, 구현 대기 중
**예상 소요 시간**: 총 14시간 (2-3일)
**마지막 업데이트**: 2025-11-02