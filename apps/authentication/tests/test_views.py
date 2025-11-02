"""
회원가입/로그인 뷰 통합 테스트
TDD Red → Green → Refactor 사이클

실행: python manage.py test apps.authentication.tests.test_views
"""

from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class SignupViewTest(TestCase):
    """회원가입 뷰 통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.client = Client()
        self.signup_url = reverse('signup')

    # ===== CYCLE 5: 회원가입 뷰 - GET 요청 =====
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

    # ===== CYCLE 5: 회원가입 뷰 - 성공 케이스 =====
    def test_signup_view_creates_user(self):
        """
        Given: 유효한 회원가입 데이터
        When: POST /signup
        Then: User 생성, 로그인 페이지로 리디렉션
        """
        # Arrange
        form_data = {
            'email': 'newuser@university.ac.kr',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'username': 'newuser',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # User 생성 확인
        self.assertTrue(User.objects.filter(email='newuser@university.ac.kr').exists())
        user = User.objects.get(email='newuser@university.ac.kr')
        self.assertEqual(user.is_active, 'pending')
        self.assertEqual(user.role, 'viewer')

    # ===== CYCLE 6: 회원가입 뷰 - 실패 케이스 =====
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
            username='기존 사용자',
        )
        form_data = {
            'email': 'existing@university.ac.kr',
            'password1': 'newpass',
            'password2': 'newpass',
            'username': '신규 사용자',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)
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
            'password1': 'test1234',
            'password2': 'different',
            'username': '테스트',
        }

        # Act
        response = self.client.post(self.signup_url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)

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
            username='테스트',
            is_active='active',
        )
        self.client.force_login(user)

        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))


class LoginViewTest(TestCase):
    """로그인 뷰 통합 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.client = Client()
        self.login_url = reverse('login')

        # 활성 사용자 생성
        self.active_user = User.objects.create(
            email='active@university.ac.kr',
            username='활성 사용자',
            is_active='active',
        )
        self.active_user.set_password('test1234')
        self.active_user.save()

    # ===== CYCLE 5: 로그인 뷰 - 성공 케이스 =====
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

    # ===== CYCLE 6: 로그인 뷰 - 실패 케이스들 =====
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
            username='대기',
            is_active='pending',
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
        self.assertNotIn('_auth_user_id', self.client.session)

    # ===== CYCLE 7: 로그인 뷰 - 이미 로그인된 경우 =====
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
            self.login_url + '?next=/dashboard/',
            data=form_data
        )

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')


class LogoutViewTest(TestCase):
    """로그아웃 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')

        self.user = User.objects.create(
            email='test@university.ac.kr',
            username='테스트',
            is_active='active',
        )
        self.user.set_password('test1234')
        self.user.save()

    # ===== CYCLE 1: 로그아웃 뷰 =====
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

    # ===== CYCLE 2: 로그아웃 후 리디렉션 =====
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


class IndexViewTest(TestCase):
    """인덱스 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.user = User.objects.create(
            email='test@university.ac.kr',
            username='테스트',
            is_active='active',
        )

    def test_index_view_shows_login_for_anonymous(self):
        """
        Given: 로그인하지 않은 사용자
        When: GET /
        Then: 로그인 페이지 표시
        """
        # Act
        response = self.client.get(self.index_url)

        # Assert
        self.assertEqual(response.status_code, 200)

    def test_index_view_redirects_authenticated_user(self):
        """
        Given: 로그인된 사용자
        When: GET /
        Then: 대시보드로 리디렉션
        """
        # Arrange
        self.client.force_login(self.user)

        # Act
        response = self.client.get(self.index_url)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
