"""
세션 검증 미들웨어 테스트
TDD Red → Green → Refactor 사이클

실행: python manage.py test apps.core.tests.test_middleware
"""

from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class SessionValidationMiddlewareTest(TestCase):
    """세션 검증 미들웨어 테스트"""

    def setUp(self):
        self.client = Client()

    # ===== CYCLE 1: 미인증 사용자 리디렉션 =====
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

    # ===== CYCLE 2: 비활성 사용자 자동 로그아웃 =====
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

    # ===== CYCLE 3: 공개 경로 예외 처리 =====
    def test_middleware_allows_public_paths(self):
        """
        Given: 로그인하지 않은 사용자
        When: 공개 경로 (/login, /signup) 접근
        Then: 정상 응답
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
