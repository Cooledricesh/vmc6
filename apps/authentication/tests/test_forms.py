"""
회원가입/로그인 폼 단위 테스트
TDD Red → Green → Refactor 사이클

실행: python manage.py test apps.authentication.tests.test_forms
"""

from django.test import TestCase
from apps.authentication.forms import SignupForm, LoginForm
from apps.authentication.models import User


class SignupFormTest(TestCase):
    """회원가입 폼 단위 테스트"""

    # ===== CYCLE 1: 필수 필드 검증 =====
    def test_signup_form_required_fields(self):
        """
        Given: 필수 필드 누락
        When: 폼 검증
        Then: 검증 실패, 에러 메시지 반환
        """
        # Arrange
        form_data = {
            'email': '',
            'password1': '',
            'password2': '',
            'username': '',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('username', form.errors)

    def test_signup_form_valid_data(self):
        """
        Given: 모든 필수 필드 제공
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'username': 'honggildong',
            'department': '컴퓨터공학과',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())

    # ===== CYCLE 2: 이메일 중복 검증 =====
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
            username='기존 사용자',
        )
        form_data = {
            'email': 'existing@university.ac.kr',
            'password1': 'newpass',
            'password2': 'newpass',
            'username': '신규 사용자',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # ===== CYCLE 3: 비밀번호 정책 검증 =====
    def test_password_min_length(self):
        """
        Given: 4자 미만 비밀번호
        When: 폼 검증
        Then: 검증 실패, 최소 길이 에러
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password1': 'abc',  # 3자
            'password2': 'abc',
            'username': '테스트',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    # ===== CYCLE 4: 비밀번호 일치 검증 =====
    def test_password_confirmation_match(self):
        """
        Given: 비밀번호와 확인이 불일치
        When: 폼 검증
        Then: 검증 실패, 불일치 에러
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password1': 'test1234',
            'password2': 'different',
            'username': '테스트',
        }

        # Act
        form = SignupForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())

    # ===== 추가 테스트 =====
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
        ]

        for invalid_email in invalid_emails:
            # Act
            form_data = {
                'email': invalid_email,
                'password1': 'test1234',
                'password2': 'test1234',
                'username': '테스트',
            }
            form = SignupForm(data=form_data)

            # Assert
            self.assertFalse(form.is_valid(), f"Email {invalid_email} should be invalid")

    def test_form_save_creates_user_with_defaults(self):
        """
        Given: 유효한 폼 데이터
        When: form.save() 호출
        Then: User 생성, 기본값 설정
        """
        # Arrange
        form_data = {
            'email': 'test@university.ac.kr',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'username': 'honggildong',
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


class LoginFormTest(TestCase):
    """로그인 폼 단위 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        # Arrange: 활성 사용자 생성
        self.active_user = User.objects.create(
            email='active@university.ac.kr',
            username='활성 사용자',
            status='active',
        )
        self.active_user.set_password('test1234')
        self.active_user.save()

        # 승인 대기 사용자
        self.pending_user = User.objects.create(
            email='pending@university.ac.kr',
            username='대기 사용자',
            status='pending',
        )
        self.pending_user.set_password('test1234')
        self.pending_user.save()

    # ===== CYCLE 1: 필수 필드 검증 =====
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

    # ===== CYCLE 2: 올바른 자격증명 =====
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

    # ===== CYCLE 3: 사용자 상태 확인 - pending =====
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

    # ===== CYCLE 4: 사용자 상태 확인 - inactive =====
    def test_login_form_inactive_user(self):
        """
        Given: status='inactive' 사용자
        When: 폼 검증
        Then: 검증 실패, 비활성화 메시지
        """
        # Arrange
        inactive_user = User.objects.create(
            email='inactive@university.ac.kr',
            username='비활성',
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

    # ===== 추가 테스트 =====
    def test_login_form_invalid_email(self):
        """
        Given: 존재하지 않는 이메일
        When: 폼 검증
        Then: 검증 실패
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

    def test_login_form_invalid_password(self):
        """
        Given: 잘못된 비밀번호
        When: 폼 검증
        Then: 검증 실패
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
