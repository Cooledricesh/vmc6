"""
User 모델 단위 테스트
TDD Red → Green → Refactor 사이클

실행: python manage.py test apps.authentication.tests.test_models
"""

from django.test import TestCase
from django.db import IntegrityError
from apps.authentication.models import User


class UserModelTest(TestCase):
    """User 모델 단위 테스트"""

    # ===== CYCLE 1: User 기본 필드 생성 =====
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
            'username': 'honggildong',
        }

        # Act
        user = User.objects.create(**user_data)

        # Assert
        self.assertEqual(user.email, 'test@university.ac.kr')
        self.assertEqual(user.username, 'honggildong')
        self.assertIsNotNone(user.id)

    # ===== CYCLE 2: 비밀번호 해싱 =====
    def test_password_is_hashed(self):
        """
        Given: 평문 비밀번호
        When: User 생성 시 set_password() 호출
        Then: 비밀번호가 해싱되어 저장됨
        """
        # Arrange
        user = User(
            email='test@university.ac.kr',
            username='testuser'
        )

        # Act
        user.set_password('test1234')
        user.save()

        # Assert
        self.assertNotEqual(user.password, 'test1234')
        self.assertTrue(user.check_password('test1234'))
        self.assertFalse(user.check_password('wrongpassword'))

    # ===== CYCLE 3: 기본값 설정 =====
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
            username='testuser',
        )

        # Assert
        self.assertEqual(user.role, 'viewer')
        self.assertEqual(user.status, 'pending')

    # ===== CYCLE 4: 모델 메서드 =====
    def test_is_approved_method(self):
        """
        Given: 다양한 status 상태를 가진 User
        When: is_approved() 호출
        Then: status='active'일 때만 True
        """
        # Arrange
        active_user = User.objects.create(
            email='active@university.ac.kr',
            password='test1234',
            username='활성',
            status='active',
        )
        pending_user = User.objects.create(
            email='pending@university.ac.kr',
            password='test1234',
            username='대기',
            status='pending',
        )

        # Act & Assert
        self.assertTrue(active_user.is_approved())
        self.assertFalse(pending_user.is_approved())

    # ===== 추가 테스트 =====
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
            username='기존 사용자',
        )

        # Act & Assert
        with self.assertRaises(IntegrityError):
            User.objects.create(
                email='test@university.ac.kr',
                password='5678',
                username='신규 사용자',
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
            username='testuser',
        )

        # Act & Assert
        self.assertEqual(str(user), 'test@university.ac.kr')

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
            username='관리자',
            role='admin',
            department='컴퓨터공학과',
        )
        viewer = User.objects.create(
            email='viewer@university.ac.kr',
            password='test1234',
            username='일반',
            role='viewer',
            department='컴퓨터공학과',
        )

        # Act & Assert
        self.assertTrue(admin.can_access_department('컴퓨터공학과'))
        self.assertTrue(admin.can_access_department('기계공학과'))
        self.assertTrue(viewer.can_access_department('컴퓨터공학과'))
        self.assertFalse(viewer.can_access_department('기계공학과'))
