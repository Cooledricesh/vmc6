# TDD 기반 구현 계획: 인증 기능
## University Data Visualization Dashboard

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 1.0
- **대상 기능**: 회원가입, 로그인, 로그아웃
- **관련 Use Cases**: UC-01 (회원가입), UC-02 (로그인), UC-11 (로그아웃)
- **관련 문서**: `/docs/pages/01-auth/state.md`, `/docs/usecases/01-signup/spec.md`, `/docs/usecases/02-login/spec.md`

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
       /__________\ - 뷰 + 폼 + DB
      /            \ - Django TestClient
     /    Unit      \ Unit Tests (70%)
    /________________\ - 모델, 폼, 헬퍼 함수
```

**예상 테스트 케이스 수:**
- Unit Tests: ~35개
- Integration Tests: ~10개
- Acceptance Tests: ~5개
- **총 예상**: ~50개 테스트

---

## 2. 구현 우선순위 및 순서

### 2.1 우선순위 (높음 → 낮음)

| 우선순위 | 기능 | 이유 | 예상 소요 시간 |
|---------|------|------|--------------|
| 1 | User 모델 | 모든 인증 기능의 기반 | 3시간 |
| 2 | 회원가입 | 사용자 생성 필수 | 4시간 |
| 3 | 로그인 | 인증 플로우 핵심 | 4시간 |
| 4 | 권한 체크 데코레이터 | 접근 제어 필수 | 2시간 |
| 5 | 로그아웃 | 세션 관리 | 1시간 |
| 6 | 세션 검증 미들웨어 | 보안 강화 | 2시간 |

**총 예상 시간**: 16시간 (2일)

---

### 2.2 개발 순서 (TDD 사이클별)

#### Phase 1: User 모델 (3시간)
```
Cycle 1: User 모델 기본 필드
  Red   → test_user_creation_with_required_fields() 작성
  Green → User 모델 기본 필드 정의
  Refactor → 필드 검증 추가

Cycle 2: 비밀번호 해싱
  Red   → test_password_is_hashed() 작성
  Green → set_password() 메서드 구현
  Refactor → check_password() 메서드 추가

Cycle 3: 기본값 설정
  Red   → test_default_role_and_status() 작성
  Green → role='viewer', status='pending' 기본값 설정
  Refactor → 없음

Cycle 4: 모델 메서드
  Red   → test_is_active_user() 작성
  Green → is_active_user() 메서드 구현
  Refactor → can_access_department() 메서드 추가
```

#### Phase 2: 회원가입 (4시간)
```
Cycle 1: SignupForm 필수 필드 검증
  Red   → test_signup_form_required_fields() 작성
  Green → SignupForm 클래스 생성, required 필드 정의
  Refactor → 에러 메시지 커스터마이징

Cycle 2: 이메일 중복 검증
  Red   → test_email_uniqueness_validation() 작성
  Green → clean_email() 메서드 구현
  Refactor → 에러 메시지 명확화

Cycle 3: 비밀번호 정책 검증
  Red   → test_password_min_length() 작성
  Green → clean_password() 메서드 구현 (최소 4자)
  Refactor → 없음

Cycle 4: 비밀번호 일치 검증
  Red   → test_password_confirmation_match() 작성
  Green → clean() 메서드에서 비밀번호 일치 확인
  Refactor → 에러 메시지 개선

Cycle 5: 회원가입 뷰 - 성공 케이스
  Red   → test_signup_view_creates_user() 작성
  Green → signup_view() 함수 구현 (POST)
  Refactor → 중복 코드 제거

Cycle 6: 회원가입 뷰 - 실패 케이스
  Red   → test_signup_view_duplicate_email() 작성
  Green → 에러 핸들링 추가
  Refactor → 없음

Cycle 7: 회원가입 템플릿 렌더링
  Red   → test_signup_view_get_renders_form() 작성
  Green → GET 요청 처리 추가
  Refactor → 템플릿 컨텍스트 정리
```

#### Phase 3: 로그인 (4시간)
```
Cycle 0: 루트 페이지 핸들러
  Red   → test_index_view_redirects_authenticated_user() 작성
  Red   → test_index_view_shows_login_for_anonymous() 작성
  Green → index_view() 함수 구현
  Refactor → login_view 재사용으로 중복 로직 제거

Cycle 1: LoginForm 기본 검증
  Red   → test_login_form_required_fields() 작성
  Green → LoginForm 클래스 생성
  Refactor → 없음

Cycle 2: 인증 로직 - 유효한 자격증명
  Red   → test_login_form_valid_credentials() 작성
  Green → clean() 메서드에서 인증 로직 구현
  Refactor → 인증 실패 메시지 통일

Cycle 3: 사용자 상태 확인 - pending
  Red   → test_login_form_pending_user() 작성
  Green → status 확인 로직 추가
  Refactor → ValidationError 통일

Cycle 4: 사용자 상태 확인 - inactive
  Red   → test_login_form_inactive_user() 작성
  Green → inactive 처리 추가
  Refactor → 없음

Cycle 5: 로그인 뷰 - 성공 케이스
  Red   → test_login_view_creates_session() 작성
  Green → login_view() 함수 구현, login(request, user) 호출
  Refactor → 리디렉션 로직 개선

Cycle 6: 로그인 뷰 - 실패 케이스들
  Red   → test_login_view_invalid_credentials() 작성
  Red   → test_login_view_pending_user() 작성
  Red   → test_login_view_inactive_user() 작성
  Green → 각 케이스 에러 처리 추가
  Refactor → 중복 코드 제거

Cycle 7: 이미 로그인된 경우 처리
  Red   → test_login_view_already_authenticated() 작성
  Green → 리디렉션 로직 추가
  Refactor → 없음
```

#### Phase 4: 로그아웃 (1시간)
```
Cycle 1: 로그아웃 뷰
  Red   → test_logout_view_destroys_session() 작성
  Green → logout_view() 함수 구현, logout(request) 호출
  Refactor → 없음

Cycle 2: 로그아웃 후 리디렉션
  Red   → test_logout_redirects_to_login() 작성
  Green → 리디렉션 로직 추가
  Refactor → 없음
```

#### Phase 5: 권한 체크 데코레이터 (2시간)
```
Cycle 1: @login_required 데코레이터
  Red   → test_login_required_redirects_anonymous() 작성
  Green → login_required 데코레이터 구현 (Django 내장 사용)
  Refactor → 없음

Cycle 2: @role_required 데코레이터
  Red   → test_role_required_admin_only() 작성
  Green → role_required() 데코레이터 구현
  Refactor → 권한 체크 로직 함수로 분리

Cycle 3: @active_user_required 데코레이터
  Red   → test_active_user_required_blocks_pending() 작성
  Green → active_user_required() 데코레이터 구현
  Refactor → 없음
```

#### Phase 6: 세션 검증 미들웨어 (2시간)
```
Cycle 1: 세션 유효성 검증
  Red   → test_middleware_redirects_unauthenticated() 작성
  Green → SessionValidationMiddleware 클래스 구현
  Refactor → 없음

Cycle 2: 비활성 사용자 자동 로그아웃
  Red   → test_middleware_logs_out_inactive_user() 작성
  Green → 비활성 사용자 처리 로직 추가
  Refactor → 로깅 추가

Cycle 3: 공개 경로 예외 처리
  Red   → test_middleware_allows_public_paths() 작성
  Green → public_paths 리스트 추가
  Refactor → 설정 파일로 분리
```

---

## 3. 기능별 테스트 시나리오

### 3.1 User 모델 테스트 (Unit Tests)

#### 테스트 파일: `apps/authentication/tests/test_models.py`

```python
from django.test import TestCase
from apps.authentication.models import User


class UserModelTest(TestCase):
    """User 모델 단위 테스트"""

    # Red → Green → Refactor Cycle 1
    def test_user_creation_with_required_fields(self):
        """
        Given: 필수 필드만 제공
        When: User 생성
        Then: 정상 생성됨
        """
        # Arrange
        user_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'name': '홍길동',
        }

        # Act
        user = User.objects.create(**user_data)

        # Assert
        self.assertEqual(user.email, 'test@university.ac.kr')
        self.assertEqual(user.name, '홍길동')
        self.assertIsNotNone(user.id)

    # Cycle 2
    def test_password_is_hashed(self):
        """
        Given: 평문 비밀번호
        When: User 생성 시 set_password() 호출
        Then: 비밀번호가 해싱되어 저장됨
        """
        # Arrange
        user = User(email='test@university.ac.kr', name='테스트')

        # Act
        user.set_password('test1234')
        user.save()

        # Assert
        self.assertNotEqual(user.password, 'test1234')
        self.assertTrue(user.check_password('test1234'))
        self.assertFalse(user.check_password('wrong'))

    # Cycle 3
    def test_default_role_and_status(self):
        """
        Given: role과 status를 명시하지 않음
        When: User 생성
        Then: 기본값 'viewer', 'pending' 설정됨
        """
        # Arrange & Act
        user = User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='테스트',
        )

        # Assert
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.status, 'pending')

    # Cycle 4
    def test_is_active_user_method(self):
        """
        Given: 다양한 status를 가진 User
        When: is_active_user() 호출
        Then: status='active'일 때만 True
        """
        # Arrange
        active_user = User.objects.create(
            email='active@university.ac.kr',
            password='test1234',
            name='활성',
            status='active',
        )
        pending_user = User.objects.create(
            email='pending@university.ac.kr',
            password='test1234',
            name='대기',
            status='pending',
        )

        # Act & Assert
        self.assertTrue(active_user.is_active_user())
        self.assertFalse(pending_user.is_active_user())

    def test_can_access_department_method(self):
        """
        Given: 특정 학과 소속 User
        When: can_access_department() 호출
        Then: 자신의 학과와 role에 따라 접근 권한 반환
        """
        # Arrange
        admin = User.objects.create(
            email='admin@university.ac.kr',
            password='test1234',
            name='관리자',
            role='admin',
            department='컴퓨터공학과',
        )
        viewer = User.objects.create(
            email='viewer@university.ac.kr',
            password='test1234',
            name='일반',
            role='viewer',
            department='컴퓨터공학과',
        )

        # Act & Assert
        self.assertTrue(admin.can_access_department('컴퓨터공학과'))
        self.assertTrue(admin.can_access_department('기계공학과'))  # admin은 모든 학과 접근 가능
        self.assertTrue(viewer.can_access_department('컴퓨터공학과'))
        self.assertFalse(viewer.can_access_department('기계공학과'))  # viewer는 자신의 학과만

    def test_email_uniqueness(self):
        """
        Given: 이미 존재하는 이메일
        When: 동일 이메일로 User 생성 시도
        Then: IntegrityError 발생
        """
        # Arrange
        User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='기존 사용자',
        )

        # Act & Assert
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create(
                email='test@university.ac.kr',
                password='5678',
                name='신규 사용자',
            )

    def test_string_representation(self):
        """
        Given: User 객체
        When: str(user) 호출
        Then: 이메일 반환
        """
        # Arrange
        user = User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='테스트',
        )

        # Act & Assert
        self.assertEqual(str(user), 'test@university.ac.kr')
```

---

### 3.2 회원가입 폼 테스트 (Unit Tests)

#### 테스트 파일: `apps/authentication/tests/test_forms.py`

```python
from django.test import TestCase
from apps.authentication.forms import SignupForm
from apps.authentication.models import User


class SignupFormTest(TestCase):
    """회원가입 폼 단위 테스트"""

    # Cycle 1
    def test_signup_form_required_fields(self):
        """
        Given: 필수 필드 누락
        When: 폼 검증
        Then: 검증 실패, 에러 메시지 반환
        """
        # Arrange
        form_data = {
            'email': '',
            'password': '',
            'password_confirm': '',
            'name': '',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('name', form.errors)

    def test_signup_form_valid_data(self):
        """
        Given: 모든 필수 필드 제공
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'test1234',
            'name': '홍길동',
            'department': '컴퓨터공학과',
            'position': '교수',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())

    # Cycle 2
    def test_email_uniqueness_validation(self):
        """
        Given: 이미 존재하는 이메일
        When: 폼 검증
        Then: 검증 실패, 중복 에러 메시지
        """
        # Arrange
        User.objects.create(
            email='existing@university.ac.kr',
            password='test1234',
            name='기존 사용자',
        )
        form_data = {
            'email': 'existing@university.ac.kr',
            'password': 'newpass',
            'password_confirm': 'newpass',
            'name': '신규 사용자',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('이미 사용 중인 이메일', str(form.errors['email']))

    # Cycle 3
    def test_password_min_length(self):
        """
        Given: 4자 미만 비밀번호
        When: 폼 검증
        Then: 검증 실패, 최소 길이 에러
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'abc',  # 3자
            'password_confirm': 'abc',
            'name': '테스트',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('최소 4자', str(form.errors['password']))

    # Cycle 4
    def test_password_confirmation_match(self):
        """
        Given: 비밀번호와 확인이 불일치
        When: 폼 검증
        Then: 검증 실패, 불일치 에러
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'different',
            'name': '테스트',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # non-field error
        self.assertIn('일치하지 않습니다', str(form.errors['__all__']))

    def test_email_format_validation(self):
        """
        Given: 잘못된 이메일 형식
        When: 폼 검증
        Then: 검증 실패, 형식 에러
        """
        # Arrange
        invalid_emails = [
            'invalid-email',
            'test@',
            '@university.ac.kr',
            'test..user@university.ac.kr',
        ]

        for invalid_email in invalid_emails:
            # Act
            form_data = {
                'email': invalid_email,
                'password': 'test1234',
                'password_confirm': 'test1234',
                'name': '테스트',
            }
            form = SignupForm(data=form_data)

            # Assert
            self.assertFalse(form.is_valid(), f"이메일 {invalid_email}이 유효하다고 판단됨")
            self.assertIn('email', form.errors)

    def test_form_save_creates_user_with_defaults(self):
        """
        Given: 유효한 폼 데이터
        When: form.save() 호출
        Then: User 생성, 기본값 설정 (role=viewer, status=pending)
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'test1234',
            'name': '홍길동',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Act
        user = form.save()

        # Assert
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'test@university.ac.kr')
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.status, 'pending')
        self.assertTrue(user.check_password('test1234'))  # 해싱 확인
```

---

### 3.3 회원가입 뷰 테스트 (Integration Tests)

#### 테스트 파일: `apps/authentication/tests/test_views.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class SignupViewTest(TestCase):
    """회원가입 뷰 통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        # Arrange: Django TestClient 생성
        self.client = Client()
        self.signup_url = reverse('signup')

    # Cycle 5
    def test_signup_view_get_renders_form(self):
        """
        Given: 로그인하지 않은 상태
        When: GET /signup
        Then: 회원가입 폼 렌더링
        """
        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')
        self.assertContains(response, '회원가입')
        self.assertContains(response, 'email')
        self.assertContains(response, 'password')

    def test_signup_view_creates_user(self):
        """
        Given: 유효한 회원가입 데이터
        When: POST /signup
        Then: User 생성, 로그인 페이지로 리디렉션
        """
        # Arrange
        form_data = {
            'email': 'newuser@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'test1234',
            'name': '신규 사용자',
            'department': '컴퓨터공학과',
            'position': '교수',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)  # 리디렉션
        self.assertRedirects(response, reverse('login'))

        # User 생성 확인
        self.assertTrue(User.objects.filter(email='newuser@university.ac.kr').exists())
        user = User.objects.get(email='newuser@university.ac.kr')
        self.assertEqual(user.status, 'pending')
        self.assertEqual(user.role, 'viewer')

    # Cycle 6
    def test_signup_view_duplicate_email(self):
        """
        Given: 이미 존재하는 이메일
        When: POST /signup
        Then: 에러 메시지, 폼 재렌더링
        """
        # Arrange
        User.objects.create(
            email='existing@university.ac.kr',
            password='oldpass',
            name='기존 사용자',
        )
        form_data = {
            'email': 'existing@university.ac.kr',
            'password': 'newpass',
            'password_confirm': 'newpass',
            'name': '신규 사용자',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)  # 폼 재렌더링
        self.assertContains(response, '이미 사용 중인 이메일')
        self.assertEqual(User.objects.filter(email='existing@university.ac.kr').count(), 1)

    def test_signup_view_password_mismatch(self):
        """
        Given: 비밀번호 불일치
        When: POST /signup
        Then: 에러 메시지, 폼 재렌더링
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'different',
            'name': '테스트',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '일치하지 않습니다')

    def test_signup_view_redirects_authenticated_user(self):
        """
        Given: 이미 로그인된 사용자
        When: GET /signup
        Then: 대시보드로 리디렉션
        """
        # Arrange
        user = User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='테스트',
            status='active',
        )
        self.client.force_login(user)

        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
```

---

### 3.4 로그인 폼 테스트 (Unit Tests)

```python
class LoginFormTest(TestCase):
    """로그인 폼 단위 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        # Arrange: 활성 사용자 생성
        self.active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성 사용자',
            status='active',
        )
        self.active_user.set_password('test1234')
        self.active_user.save()

        # 승인 대기 사용자
        self.pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기 사용자',
            status='pending',
        )
        self.pending_user.set_password('test1234')
        self.pending_user.save()

    # Cycle 1
    def test_login_form_required_fields(self):
        """
        Given: 필수 필드 누락
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {
            'email': '',
            'password': '',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)

    # Cycle 2
    def test_login_form_valid_credentials(self):
        """
        Given: 올바른 이메일과 비밀번호
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {
            'email': 'active@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_email(self):
        """
        Given: 존재하지 않는 이메일
        When: 폼 검증
        Then: 검증 실패, 일반적 에러 메시지 (보안)
        """
        # Arrange
        form_data = {
            'email': 'nonexistent@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('이메일 또는 비밀번호가', str(form.errors))

    def test_login_form_invalid_password(self):
        """
        Given: 잘못된 비밀번호
        When: 폼 검증
        Then: 검증 실패, 일반적 에러 메시지
        """
        # Arrange
        form_data = {
            'email': 'active@university.ac.kr',
            'password': 'wrongpassword',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('이메일 또는 비밀번호가', str(form.errors))

    # Cycle 3
    def test_login_form_pending_user(self):
        """
        Given: status='pending' 사용자
        When: 폼 검증
        Then: 검증 실패, 승인 대기 메시지
        """
        # Arrange
        form_data = {
            'email': 'pending@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('승인 대기', str(form.errors))

    # Cycle 4
    def test_login_form_inactive_user(self):
        """
        Given: status='inactive' 사용자
        When: 폼 검증
        Then: 검증 실패, 비활성화 메시지
        """
        # Arrange
        inactive_user = User.objects.create(
            email='inactive@university.ac.kr',
            name='비활성',
            status='inactive',
        )
        inactive_user.set_password('test1234')
        inactive_user.save()

        form_data = {
            'email': 'inactive@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        form = LoginForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('비활성화', str(form.errors))
```

---

### 3.5 로그인 뷰 테스트 (Integration Tests)

```python
class LoginViewTest(TestCase):
    """로그인 뷰 통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.client = Client()
        self.login_url = reverse('login')

        # 활성 사용자 생성
        self.active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성 사용자',
            status='active',
        )
        self.active_user.set_password('test1234')
        self.active_user.save()

    # Cycle 5
    def test_login_view_creates_session(self):
        """
        Given: 유효한 로그인 데이터
        When: POST /login
        Then: 세션 생성, 대시보드로 리디렉션
        """
        # Arrange
        form_data = {
            'email': 'active@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        response = self.client.post(self.login_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # 세션 확인
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.active_user.id)

    # Cycle 6
    def test_login_view_invalid_credentials(self):
        """
        Given: 잘못된 비밀번호
        When: POST /login
        Then: 에러 메시지, 폼 재렌더링
        """
        # Arrange
        form_data = {
            'email': 'active@university.ac.kr',
            'password': 'wrongpassword',
        }

        # Act
        response = self.client.post(self.login_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '이메일 또는 비밀번호가')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_view_pending_user(self):
        """
        Given: 승인 대기 사용자
        When: POST /login
        Then: 승인 대기 메시지, 세션 생성 안 됨
        """
        # Arrange
        pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기',
            status='pending',
        )
        pending_user.set_password('test1234')
        pending_user.save()

        form_data = {
            'email': 'pending@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        response = self.client.post(self.login_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '승인 대기')
        self.assertNotIn('_auth_user_id', self.client.session)

    # Cycle 7
    def test_login_view_already_authenticated(self):
        """
        Given: 이미 로그인된 사용자
        When: GET /login
        Then: 대시보드로 리디렉션
        """
        # Arrange
        self.client.force_login(self.active_user)

        # Act
        response = self.client.get(self.login_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_view_next_parameter(self):
        """
        Given: next 파라미터 포함
        When: 로그인 성공
        Then: next URL로 리디렉션
        """
        # Arrange
        form_data = {
            'email': 'active@university.ac.kr',
            'password': 'test1234',
        }

        # Act
        response = self.client.post(
            self.login_url + '?next=/analytics/publications',
            data=form_data
        )

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/analytics/publications')
```

---

### 3.6 로그아웃 테스트 (Integration Tests)

```python
class LogoutViewTest(TestCase):
    """로그아웃 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')

        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            status='active',
        )
        self.user.set_password('test1234')
        self.user.save()

    # Cycle 1
    def test_logout_view_destroys_session(self):
        """
        Given: 로그인된 사용자
        When: POST /logout
        Then: 세션 삭제
        """
        # Arrange
        self.client.force_login(self.user)
        self.assertIn('_auth_user_id', self.client.session)

        # Act
        response = self.client.post(self.logout_url)

        # Assert
        self.assertNotIn('_auth_user_id', self.client.session)

    # Cycle 2
    def test_logout_redirects_to_login(self):
        """
        Given: 로그인된 사용자
        When: POST /logout
        Then: 로그인 페이지로 리디렉션
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.post(self.logout_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
```

---

### 3.7 권한 체크 데코레이터 테스트 (Unit Tests)

#### 테스트 파일: `apps/core/tests/test_decorators.py`

```python
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from apps.core.decorators import role_required, active_user_required
from apps.authentication.models import User


class RoleRequiredDecoratorTest(TestCase):
    """@role_required 데코레이터 테스트"""

    def setUp(self):
        self.factory = RequestFactory()

        # 테스트용 뷰 함수
        @role_required(['admin'])
        def admin_only_view(request):
            return HttpResponse('Admin content')

        self.view = admin_only_view

        # 테스트 사용자들
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.viewer = User.objects.create(
            email='viewer@university.ac.kr',
            name='일반 사용자',
            role='viewer',
            status='active',
        )

    # Cycle 2
    def test_role_required_admin_only(self):
        """
        Given: admin 전용 뷰
        When: viewer가 접근 시도
        Then: 403 Forbidden 또는 리디렉션
        """
        # Arrange
        request = self.factory.get('/admin-only')
        request.user = self.viewer

        # Act
        response = self.view(request)

        # Assert
        self.assertEqual(response.status_code, 403)

    def test_role_required_allows_admin(self):
        """
        Given: admin 전용 뷰
        When: admin이 접근
        Then: 정상 응답
        """
        # Arrange
        request = self.factory.get('/admin-only')
        request.user = self.admin

        # Act
        response = self.view(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin content')

    def test_role_required_multiple_roles(self):
        """
        Given: admin 또는 manager 접근 가능한 뷰
        When: viewer가 접근
        Then: 403 Forbidden
        """
        # Arrange
        @role_required(['admin', 'manager'])
        def multi_role_view(request):
            return HttpResponse('Multi role content')

        manager = User.objects.create(
            email='manager@university.ac.kr',
            name='매니저',
            role='manager',
            status='active',
        )

        # Act - manager 접근
        request = self.factory.get('/multi-role')
        request.user = manager
        response = multi_role_view(request)

        # Assert
        self.assertEqual(response.status_code, 200)

        # Act - viewer 접근
        request.user = self.viewer
        response = multi_role_view(request)

        # Assert
        self.assertEqual(response.status_code, 403)


class ActiveUserRequiredDecoratorTest(TestCase):
    """@active_user_required 데코레이터 테스트"""

    def setUp(self):
        self.factory = RequestFactory()

        @active_user_required
        def protected_view(request):
            return HttpResponse('Protected content')

        self.view = protected_view

    # Cycle 3
    def test_active_user_required_blocks_pending(self):
        """
        Given: active_user_required 뷰
        When: pending 사용자 접근
        Then: 리디렉션 또는 403
        """
        # Arrange
        pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기 사용자',
            status='pending',
        )
        request = self.factory.get('/protected')
        request.user = pending_user

        # Act
        response = self.view(request)

        # Assert
        self.assertEqual(response.status_code, 403)

    def test_active_user_required_allows_active(self):
        """
        Given: active_user_required 뷰
        When: active 사용자 접근
        Then: 정상 응답
        """
        # Arrange
        active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성 사용자',
            status='active',
        )
        request = self.factory.get('/protected')
        request.user = active_user

        # Act
        response = self.view(request)

        # Assert
        self.assertEqual(response.status_code, 200)
```

---

### 3.8 세션 검증 미들웨어 테스트 (Integration Tests)

#### 테스트 파일: `apps/core/tests/test_middleware.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class SessionValidationMiddlewareTest(TestCase):
    """세션 검증 미들웨어 테스트"""

    def setUp(self):
        self.client = Client()

    # Cycle 1
    def test_middleware_redirects_unauthenticated(self):
        """
        Given: 로그인하지 않은 사용자
        When: 보호된 페이지 접근
        Then: 로그인 페이지로 리디렉션
        """
        # Act
        response = self.client.get(reverse('dashboard'))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=/dashboard')

    # Cycle 2
    def test_middleware_logs_out_inactive_user(self):
        """
        Given: inactive 사용자로 로그인
        When: 보호된 페이지 접근
        Then: 자동 로그아웃, 로그인 페이지로 리디렉션
        """
        # Arrange
        inactive_user = User.objects.create(
            email='inactive@university.ac.kr',
            name='비활성',
            status='inactive',
        )
        self.client.force_login(inactive_user)

        # Act
        response = self.client.get(reverse('dashboard'))

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    # Cycle 3
    def test_middleware_allows_public_paths(self):
        """
        Given: 로그인하지 않은 사용자
        When: 공개 경로 (/login, /signup) 접근
        Then: 정상 응답, 리디렉션 없음
        """
        # Act - login
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        # Act - signup
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_middleware_allows_active_user(self):
        """
        Given: active 사용자로 로그인
        When: 보호된 페이지 접근
        Then: 정상 응답
        """
        # Arrange
        active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성',
            status='active',
        )
        self.client.force_login(active_user)

        # Act
        response = self.client.get(reverse('dashboard'))

        # Assert
        self.assertEqual(response.status_code, 200)
```

---

### 3.9 Acceptance Tests (End-to-End)

#### 테스트 파일: `apps/authentication/tests/test_acceptance.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class UserRegistrationAcceptanceTest(TestCase):
    """회원가입 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()

    def test_full_registration_flow(self):
        """
        Scenario: 신규 사용자 회원가입 → 관리자 승인 → 로그인
        Given: 회원가입하지 않은 신규 사용자
        When: 회원가입 → 승인 대기 → 관리자 승인 → 로그인
        Then: 대시보드 접근 가능
        """
        # Step 1: 회원가입 페이지 접근
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

        # Step 2: 회원가입 정보 입력 및 제출
        signup_data = {
            'email': 'newuser@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'test1234',
            'name': '신규 사용자',
            'department': '컴퓨터공학과',
            'position': '교수',
        }
        response = self.client.post(reverse('signup'), data=signup_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Step 3: User 생성 확인
        self.assertTrue(User.objects.filter(email='newuser@university.ac.kr').exists())
        user = User.objects.get(email='newuser@university.ac.kr')
        self.assertEqual(user.status, 'pending')

        # Step 4: 승인 전 로그인 시도 (실패)
        login_data = {
            'email': 'newuser@university.ac.kr',
            'password': 'test1234',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '승인 대기')

        # Step 5: 관리자 승인 (시뮬레이션)
        user.status = 'active'
        user.save()

        # Step 6: 로그인 재시도 (성공)
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Step 7: 대시보드 접근 확인
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class LoginLogoutAcceptanceTest(TestCase):
    """로그인/로그아웃 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트 사용자',
            status='active',
        )
        self.user.set_password('test1234')
        self.user.save()

    def test_login_and_logout_flow(self):
        """
        Scenario: 로그인 → 대시보드 접근 → 로그아웃
        Given: 활성 사용자
        When: 로그인 → 로그아웃
        Then: 세션 관리 정상 작동
        """
        # Step 1: 로그인 페이지 접근
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        # Step 2: 로그인
        login_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Step 3: 세션 확인
        self.assertIn('_auth_user_id', self.client.session)

        # Step 4: 대시보드 접근
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Step 5: 로그아웃
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Step 6: 세션 삭제 확인
        self.assertNotIn('_auth_user_id', self.client.session)

        # Step 7: 대시보드 재접근 시도 (실패)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=/dashboard')
```

---

## 4. AAA 패턴 적용 예제

### 4.1 기본 AAA 패턴

```python
def test_example(self):
    """
    Given: 테스트 조건
    When: 실행할 동작
    Then: 예상 결과
    """
    # Arrange (준비)
    # - 테스트에 필요한 데이터 준비
    # - 객체 생성, 상태 설정
    user_data = {
        'email': 'test@university.ac.kr',
        'password': 'test1234',
        'name': '테스트',
    }

    # Act (실행)
    # - 테스트할 동작 수행
    # - 단 하나의 액션만 수행
    user = User.objects.create(**user_data)

    # Assert (검증)
    # - 결과 검증
    # - 여러 검증 가능
    self.assertEqual(user.email, 'test@university.ac.kr')
    self.assertIsNotNone(user.id)
    self.assertEqual(user.status, 'pending')
```

### 4.2 복잡한 AAA 패턴 (Integration Test)

```python
def test_signup_with_existing_email(self):
    """
    Given: 이미 등록된 이메일
    When: 동일 이메일로 회원가입 시도
    Then: 에러 메시지 표시, User 생성 안 됨
    """
    # Arrange
    # 1. 기존 사용자 생성
    User.objects.create(
        email='existing@university.ac.kr',
        password='oldpass',
        name='기존 사용자',
    )

    # 2. 회원가입 데이터 준비
    signup_data = {
        'email': 'existing@university.ac.kr',
        'password': 'newpass',
        'password_confirm': 'newpass',
        'name': '신규 사용자',
    }

    # Act
    # 회원가입 시도
    response = self.client.post(reverse('signup'), data=signup_data)

    # Assert
    # 1. 200 상태 코드 (폼 재렌더링)
    self.assertEqual(response.status_code, 200)

    # 2. 에러 메시지 확인
    self.assertContains(response, '이미 사용 중인 이메일')

    # 3. User 개수 확인 (여전히 1개)
    self.assertEqual(User.objects.count(), 1)
```

---

## 5. FIRST 원칙 적용

### 5.1 Fast (빠른 테스트)
- 각 테스트는 100ms 이하로 실행
- DB 트랜잭션 롤백으로 속도 향상 (Django TestCase 기본)
- Mock 사용 최소화 (통합 테스트는 실제 DB 사용)

```python
class FastTestExample(TestCase):
    """빠른 테스트 예제"""

    def test_user_creation_is_fast(self):
        """User 생성 테스트는 100ms 이하"""
        import time
        start = time.time()

        # Act
        user = User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='테스트',
        )

        # Assert
        elapsed = time.time() - start
        self.assertLess(elapsed, 0.1)  # 100ms 이하
        self.assertIsNotNone(user.id)
```

### 5.2 Independent (독립적인 테스트)
- 각 테스트는 독립적으로 실행 가능
- 테스트 간 공유 상태 없음
- setUp()에서 필요한 데이터 생성, tearDown()은 자동 (Django)

```python
class IndependentTestExample(TestCase):
    """독립적인 테스트 예제"""

    def setUp(self):
        """각 테스트 전에 독립적으로 실행"""
        self.user = User.objects.create(
            email='test@university.ac.kr',
            password='test1234',
            name='테스트',
        )

    def test_user_exists(self):
        """테스트 1: User 존재 확인"""
        self.assertTrue(User.objects.filter(email='test@university.ac.kr').exists())

    def test_user_status(self):
        """테스트 2: User 상태 확인 (test_user_exists와 독립적)"""
        user = User.objects.get(email='test@university.ac.kr')
        self.assertEqual(user.status, 'pending')

    # tearDown() 불필요 - Django TestCase가 자동으로 DB 롤백
```

### 5.3 Repeatable (반복 가능한 테스트)
- 언제 실행해도 같은 결과
- 외부 상태에 의존하지 않음
- 랜덤 데이터 사용 시 시드 고정

```python
class RepeatableTestExample(TestCase):
    """반복 가능한 테스트 예제"""

    def test_password_hashing_is_repeatable(self):
        """비밀번호 해싱은 항상 일관된 결과"""
        # Arrange
        user1 = User(email='test1@university.ac.kr', name='테스트1')
        user1.set_password('test1234')

        user2 = User(email='test2@university.ac.kr', name='테스트2')
        user2.set_password('test1234')

        # Assert
        # 동일한 비밀번호는 동일하게 해싱됨 (salt 고정 시)
        # 실제로는 랜덤 salt 사용하므로 check_password로 검증
        self.assertTrue(user1.check_password('test1234'))
        self.assertTrue(user2.check_password('test1234'))
```

### 5.4 Self-validating (자가 검증)
- 테스트 결과는 Pass/Fail만 존재
- 수동 확인 불필요
- 명확한 assertion

```python
class SelfValidatingTestExample(TestCase):
    """자가 검증 테스트 예제"""

    def test_signup_creates_user_with_correct_defaults(self):
        """회원가입 시 올바른 기본값 설정 (자가 검증)"""
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password': 'test1234',
            'password_confirm': 'test1234',
            'name': '테스트',
        }
        form = SignupForm(data=form_data)
        form.is_valid()

        # Act
        user = form.save()

        # Assert (명확한 검증, 수동 확인 불필요)
        self.assertEqual(user.role, 'viewer', "기본 역할은 viewer여야 함")
        self.assertEqual(user.status, 'pending', "기본 상태는 pending이어야 함")
        self.assertTrue(user.check_password('test1234'), "비밀번호가 올바르게 해싱되어야 함")
```

### 5.5 Timely (적시성)
- 코드 작성 전에 테스트 먼저 작성
- Red → Green → Refactor

```python
# 1. Red: 테스트 먼저 작성 (실패)
def test_user_is_admin_method(self):
    """User.is_admin() 메서드 테스트"""
    # Arrange
    admin = User.objects.create(
        email='admin@university.ac.kr',
        password='test1234',
        name='관리자',
        role='admin',
    )
    viewer = User.objects.create(
        email='viewer@university.ac.kr',
        password='test1234',
        name='일반 사용자',
        role='viewer',
    )

    # Act & Assert
    self.assertTrue(admin.is_admin())  # 실패: 메서드 없음
    self.assertFalse(viewer.is_admin())

# 2. Green: 최소한의 코드로 통과
# apps/authentication/models.py
def is_admin(self):
    return self.role == 'admin'

# 3. Refactor: 코드 개선
def is_admin(self):
    """관리자 여부 확인"""
    return self.role == 'admin'
```

---

## 6. 예상 테스트 실행 계획

### 6.1 테스트 실행 명령어

```bash
# 전체 인증 테스트 실행
python manage.py test apps.authentication

# 특정 테스트 파일만 실행
python manage.py test apps.authentication.tests.test_models

# 특정 테스트 케이스만 실행
python manage.py test apps.authentication.tests.test_models.UserModelTest

# 특정 테스트 메서드만 실행
python manage.py test apps.authentication.tests.test_models.UserModelTest.test_user_creation_with_required_fields

# 코드 커버리지 측정
coverage run --source='apps.authentication' manage.py test apps.authentication
coverage report
coverage html  # HTML 리포트 생성
```

### 6.2 테스트 실행 시간 예상

| 테스트 유형 | 개수 | 예상 시간 | 비고 |
|------------|------|----------|------|
| Unit Tests (모델) | 8 | 1초 | 빠른 실행 |
| Unit Tests (폼) | 15 | 2초 | 검증 로직 포함 |
| Integration Tests (뷰) | 15 | 5초 | DB 트랜잭션 |
| Integration Tests (미들웨어) | 5 | 2초 | - |
| Acceptance Tests | 5 | 8초 | 전체 플로우 |
| **총합** | **48** | **18초** | 충분히 빠름 |

---

## 7. 커밋 전략

### 7.1 작은 단위 커밋

```bash
# Cycle 1 완료 후
git add apps/authentication/models.py apps/authentication/tests/test_models.py
git commit -m "test: User 모델 기본 필드 테스트 작성 및 구현

- Red: test_user_creation_with_required_fields() 작성
- Green: User 모델 기본 필드 정의
- Refactor: 필드 검증 추가
"

# Cycle 2 완료 후
git add apps/authentication/models.py apps/authentication/tests/test_models.py
git commit -m "test: User 비밀번호 해싱 테스트 및 구현

- Red: test_password_is_hashed() 작성
- Green: set_password(), check_password() 메서드 구현
"
```

### 7.2 커밋 메시지 규칙
```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `test:` 테스트 추가/수정
- `feat:` 새 기능 추가
- `fix:` 버그 수정
- `refactor:` 리팩토링
- `docs:` 문서 수정

---

## 8. 체크리스트

### 8.1 각 Cycle 완료 시

- [ ] Red: 실패하는 테스트 작성
- [ ] 테스트 실행하여 실패 확인
- [ ] Green: 최소한의 코드로 통과
- [ ] 테스트 실행하여 성공 확인
- [ ] Refactor: 코드 개선 (필요 시)
- [ ] 모든 테스트 재실행 (회귀 방지)
- [ ] 커밋 (Red, Green, Refactor 각각 또는 합쳐서)

### 8.2 Phase 완료 시

- [ ] 해당 Phase의 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상
- [ ] 코드 리뷰 (선택)
- [ ] 문서 업데이트
- [ ] 다음 Phase로 진행

### 8.3 전체 완료 시

- [ ] 모든 테스트 통과 (Unit + Integration + Acceptance)
- [ ] 코드 커버리지 80% 이상
- [ ] 보안 검토 (비밀번호 해싱, CSRF, XSS)
- [ ] 성능 검토 (쿼리 최적화)
- [ ] 문서 완성도 확인
- [ ] Pull Request 생성

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성<br>- TDD 사이클별 구현 계획<br>- 50개 테스트 시나리오<br>- AAA 패턴 및 FIRST 원칙 적용 예제<br>- 예상 소요 시간 및 우선순위 정의 | Claude Code |

---

## 10. 참고 문서

- [TDD 가이드라인](/Users/seunghyun/Test/vmc6/docs/tdd.md)
- [인증 상태관리 문서](/Users/seunghyun/Test/vmc6/docs/pages/01-auth/state.md)
- [UC-01: 회원가입](/Users/seunghyun/Test/vmc6/docs/usecases/01-signup/spec.md)
- [UC-02: 로그인](/Users/seunghyun/Test/vmc6/docs/usecases/02-login/spec.md)
- [Database Schema](/Users/seunghyun/Test/vmc6/docs/database.md)

---

**문서 작성 완료**
**다음 작업**: Phase 1 (User 모델) 구현 시작
