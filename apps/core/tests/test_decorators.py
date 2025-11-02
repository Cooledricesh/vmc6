"""
권한 체크 데코레이터 테스트
TDD Red → Green → Refactor 사이클

실행: python manage.py test apps.core.tests.test_decorators
"""

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

    # ===== CYCLE 2: @role_required 기본 동작 =====
    def test_role_required_admin_only(self):
        """
        Given: admin 전용 뷰
        When: viewer가 접근 시도
        Then: 403 Forbidden
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

    def test_role_required_multiple_roles(self):
        """
        Given: admin 또는 manager 접근 가능한 뷰
        When: 다양한 role 사용자 접근
        Then: 권한에 따라 동작
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

    # ===== CYCLE 3: @active_user_required 데코레이터 =====
    def test_active_user_required_blocks_pending(self):
        """
        Given: active_user_required 뷰
        When: pending 사용자 접근
        Then: 403 또는 리디렉션
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

    def test_active_user_required_blocks_inactive(self):
        """
        Given: active_user_required 뷰
        When: inactive 사용자 접근
        Then: 403
        """
        # Arrange
        inactive_user = User.objects.create(
            email='inactive@university.ac.kr',
            name='비활성 사용자',
            status='inactive',
        )
        request = self.factory.get('/protected')
        request.user = inactive_user

        # Act
        response = self.view(request)

        # Assert
        self.assertEqual(response.status_code, 403)
