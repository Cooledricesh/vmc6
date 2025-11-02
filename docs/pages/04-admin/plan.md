# TDD 기반 구현 계획: 관리자 기능
## University Data Visualization Dashboard

---

## 문서 정보
- **작성일**: 2025-11-02
- **버전**: 1.0
- **대상 기능**: 사용자 승인/거부, 권한 관리, 업로드 이력 조회
- **관련 Use Cases**: UC-09 (사용자 승인), UC-10 (프로필 관리), UC-12 (업로드 이력)
- **관련 문서**: `/docs/database.md`, `/docs/userflow.md`, `/docs/common-modules.md`

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
          /____\  - 사용자 승인 전체 플로우
         /      \  - End-to-End 시나리오
        / Integ. \ Integration Tests (20%)
       /__________\ - 뷰 + 폼 + DB
      /            \ - Django TestClient
     /    Unit      \ Unit Tests (70%)
    /________________\ - 모델 메서드, 폼, 헬퍼
```

**예상 테스트 케이스 수:**
- Unit Tests: ~35개 (모델 메서드 15, 폼 10, 헬퍼 10)
- Integration Tests: ~15개 (뷰 테스트)
- Acceptance Tests: ~5개 (전체 플로우)
- **총 예상**: ~55개 테스트

---

## 2. 구현 우선순위 및 순서

### 2.1 우선순위 (높음 → 낮음)

| 우선순위 | 기능 | 이유 | 예상 소요 시간 |
|---------|------|------|--------------|
| 1 | 사용자 승인/거부 뷰 | 핵심 관리 기능 | 4시간 |
| 2 | 사용자 목록 조회 및 필터링 | 승인 전제 조건 | 3시간 |
| 3 | 권한 변경 기능 | 역할 관리 | 2시간 |
| 4 | 업로드 이력 조회 | 데이터 관리 감사 | 3시간 |
| 5 | 사용자 프로필 관리 | 개인정보 수정 | 3시간 |
| 6 | 비밀번호 변경 | 보안 | 2시간 |
| 7 | 관리자 권한 체크 | 보안 강화 | 1시간 |

**총 예상 시간**: 18시간 (2~3일)

---

### 2.2 개발 순서 (TDD 사이클별)

#### Phase 1: 사용자 목록 조회 및 필터링 (3시간)

```
Cycle 1: 전체 사용자 목록 조회
  Red   → test_admin_user_list_view() 작성
  Green → admin_user_list_view() 함수 구현
  Refactor → 권한 체크 데코레이터 적용

Cycle 2: 상태별 필터링 (pending, active, inactive)
  Red   → test_filter_users_by_status() 작성
  Green → 쿼리 파라미터 처리 추가
  Refactor → 필터링 로직 함수로 분리

Cycle 3: 역할별 필터링
  Red   → test_filter_users_by_role() 작성
  Green → 역할 필터 추가
  Refactor → 다중 필터 지원

Cycle 4: 검색 기능 (이름, 이메일)
  Red   → test_search_users() 작성
  Green → Q 객체를 활용한 검색 로직 구현
  Refactor → 대소문자 구분 없이 검색

Cycle 5: 페이지네이션
  Red   → test_user_list_pagination() 작성
  Green → Paginator 적용
  Refactor → 페이지 크기 조정 옵션
```

---

#### Phase 2: 사용자 승인/거부 (4시간)

```
Cycle 1: 승인 뷰 기본 구조
  Red   → test_approve_user_view() 작성
  Green → approve_user_view() 함수 구현
  Refactor → 없음

Cycle 2: 사용자 상태 변경 (pending → active)
  Red   → test_approve_changes_status_to_active() 작성
  Green → user.status = 'active', user.save() 추가
  Refactor → 트랜잭션 처리

Cycle 3: 승인 성공 메시지
  Red   → test_approve_shows_success_message() 작성
  Green → messages.success() 호출
  Refactor → 없음

Cycle 4: 거부 뷰 기본 구조
  Red   → test_reject_user_view() 작성
  Green → reject_user_view() 함수 구현
  Refactor → 없음

Cycle 5: 사용자 상태 변경 (pending → inactive)
  Red   → test_reject_changes_status_to_inactive() 작성
  Green → user.status = 'inactive', user.save() 추가
  Refactor → 트랜잭션 처리

Cycle 6: 거부 사유 입력 폼
  Red   → test_reject_requires_reason() 작성
  Green → RejectUserForm 생성, reason 필드 추가
  Refactor → 폼 검증 강화

Cycle 7: 거부 사유 저장
  Red   → test_reject_saves_reason() 작성
  Green → User 모델에 rejection_reason 필드 추가
  Refactor → 없음 (마이그레이션 필요 없음, managed=False)

Cycle 8: 이미 처리된 사용자 체크
  Red   → test_approve_already_active_user() 작성
  Green → 상태 확인 로직 추가
  Refactor → 에러 메시지 개선

Cycle 9: 권한 체크 (admin만 가능)
  Red   → test_non_admin_cannot_approve() 작성
  Green → @role_required(['admin']) 데코레이터 적용
  Refactor → 없음
```

---

#### Phase 3: 권한 변경 기능 (2시간)

```
Cycle 1: 권한 변경 뷰
  Red   → test_change_user_role_view() 작성
  Green → change_user_role_view() 함수 구현
  Refactor → 없음

Cycle 2: 역할 변경 폼
  Red   → test_change_role_form_validation() 작성
  Green → ChangeRoleForm 생성, role 필드 추가
  Refactor → 선택지 제한 (admin, manager, viewer)

Cycle 3: 역할 변경 저장
  Red   → test_change_role_updates_user() 작성
  Green → user.role = new_role, user.save() 추가
  Refactor → 트랜잭션 처리

Cycle 4: 자기 자신의 역할 변경 방지
  Red   → test_cannot_change_own_role() 작성
  Green → if user.id == request.user.id 체크
  Refactor → 에러 메시지 추가

Cycle 5: 권한 체크 (admin만 가능)
  Red   → test_non_admin_cannot_change_role() 작성
  Green → @role_required(['admin']) 데코레이터 적용
  Refactor → 없음
```

---

#### Phase 4: 업로드 이력 조회 (3시간)

```
Cycle 1: 업로드 이력 목록 뷰
  Red   → test_upload_history_list_view() 작성
  Green → upload_history_list_view() 함수 구현
  Refactor → 없음

Cycle 2: 이력 필터링 (날짜 범위)
  Red   → test_filter_upload_history_by_date() 작성
  Green → 날짜 범위 쿼리 파라미터 처리
  Refactor → 없음

Cycle 3: 이력 필터링 (데이터 타입)
  Red   → test_filter_upload_history_by_data_type() 작성
  Green → 데이터 타입 필터 추가
  Refactor → 없음

Cycle 4: 이력 필터링 (상태)
  Red   → test_filter_upload_history_by_status() 작성
  Green → 상태 필터 추가
  Refactor → 다중 필터 통합

Cycle 5: 업로드자별 이력 조회 (admin 전용)
  Red   → test_admin_sees_all_upload_history() 작성
  Green → 권한별 쿼리 분기 추가
  Refactor → permissions.py 활용

Cycle 6: 일반 사용자는 자신의 이력만
  Red   → test_viewer_sees_own_upload_history() 작성
  Green → user_id 필터 추가
  Refactor → 없음

Cycle 7: 상세 정보 조회
  Red   → test_upload_history_detail_view() 작성
  Green → upload_history_detail_view() 함수 구현
  Refactor → 에러 로그 표시 추가
```

---

#### Phase 5: 사용자 프로필 관리 (3시간)

```
Cycle 1: 프로필 조회 뷰
  Red   → test_profile_view_shows_user_info() 작성
  Green → profile_view() 함수 구현
  Refactor → 없음

Cycle 2: 프로필 수정 폼
  Red   → test_profile_update_form_validation() 작성
  Green → ProfileUpdateForm 생성
  Refactor → 필드 제한 (name, department, position만 수정 가능)

Cycle 3: 프로필 수정 저장
  Red   → test_profile_update_saves_changes() 작성
  Green → form.save() 구현
  Refactor → 변경 사항 없을 시 메시지

Cycle 4: 이메일 수정 방지
  Red   → test_cannot_change_email() 작성
  Green → 폼에서 이메일 필드 제외
  Refactor → 없음

Cycle 5: 역할 수정 방지
  Red   → test_cannot_change_role_in_profile() 작성
  Green → 폼에서 role 필드 제외
  Refactor → 없음
```

---

#### Phase 6: 비밀번호 변경 (2시간)

```
Cycle 1: 비밀번호 변경 폼
  Red   → test_password_change_form_validation() 작성
  Green → PasswordChangeForm 생성
  Refactor → 없음

Cycle 2: 현재 비밀번호 검증
  Red   → test_password_change_verifies_current_password() 작성
  Green → clean_current_password() 메서드 구현
  Refactor → 없음

Cycle 3: 새 비밀번호 정책 검증
  Red   → test_new_password_meets_policy() 작성
  Green → 비밀번호 Validator 호출
  Refactor → 없음

Cycle 4: 새 비밀번호 일치 검증
  Red   → test_new_passwords_match() 작성
  Green → clean() 메서드에서 일치 확인
  Refactor → 없음

Cycle 5: 비밀번호 변경 저장
  Red   → test_password_change_saves_new_password() 작성
  Green → user.set_password(), user.save() 호출
  Refactor → 세션 유지 (update_session_auth_hash)

Cycle 6: 새 비밀번호가 현재와 동일 방지
  Red   → test_new_password_different_from_current() 작성
  Green → clean() 메서드에서 체크
  Refactor → 에러 메시지 추가
```

---

#### Phase 7: 관리자 권한 체크 (1시간)

```
Cycle 1: admin 전용 데코레이터 테스트
  Red   → test_admin_required_decorator() 작성
  Green → @role_required(['admin']) 확인
  Refactor → 없음

Cycle 2: 일반 사용자 접근 차단
  Red   → test_viewer_cannot_access_admin_pages() 작성
  Green → 403 Forbidden 응답 확인
  Refactor → 없음

Cycle 3: 권한 없는 사용자 리디렉션
  Red   → test_redirect_to_dashboard_on_permission_denied() 작성
  Green → 리디렉션 로직 추가
  Refactor → 메시지 표시
```

---

## 3. 기능별 테스트 시나리오

### 3.1 모델 메서드 테스트 (Unit Tests)

#### 테스트 파일: `apps/authentication/tests/test_models.py`

```python
from django.test import TestCase
from apps.authentication.models import User


class UserModelMethodsTest(TestCase):
    """User 모델 메서드 단위 테스트"""

    def setUp(self):
        """테스트 환경 설정"""
        self.pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기 사용자',
            status='pending',
        )
        self.active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성 사용자',
            status='active',
        )

    def test_approve_user_method(self):
        """
        Given: pending 사용자
        When: approve() 메서드 호출
        Then: status가 'active'로 변경됨
        """
        # Arrange
        user = self.pending_user

        # Act
        user.approve()

        # Assert
        user.refresh_from_db()
        self.assertEqual(user.status, 'active')

    def test_reject_user_method(self):
        """
        Given: pending 사용자
        When: reject(reason) 메서드 호출
        Then: status가 'inactive'로 변경, 거부 사유 저장
        """
        # Arrange
        user = self.pending_user
        reason = '자격 요건 미충족'

        # Act
        user.reject(reason)

        # Assert
        user.refresh_from_db()
        self.assertEqual(user.status, 'inactive')
        self.assertEqual(user.rejection_reason, reason)

    def test_change_role_method(self):
        """
        Given: viewer 사용자
        When: change_role('manager') 호출
        Then: role이 'manager'로 변경됨
        """
        # Arrange
        user = self.active_user

        # Act
        user.change_role('manager')

        # Assert
        user.refresh_from_db()
        self.assertEqual(user.role, 'manager')

    def test_cannot_approve_already_active_user(self):
        """
        Given: active 사용자
        When: approve() 메서드 호출
        Then: ValueError 발생
        """
        # Arrange
        user = self.active_user

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            user.approve()

        self.assertIn('이미 활성', str(context.exception))
```

---

### 3.2 폼 테스트 (Unit Tests)

#### 테스트 파일: `apps/authentication/tests/test_forms.py`

```python
from django.test import TestCase
from apps.authentication.forms import (
    ProfileUpdateForm,
    PasswordChangeForm,
    ChangeRoleForm,
    RejectUserForm,
)
from apps.authentication.models import User


class ProfileUpdateFormTest(TestCase):
    """프로필 수정 폼 단위 테스트"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            department='컴퓨터공학과',
            position='교수',
        )

    def test_profile_update_form_valid_data(self):
        """
        Given: 유효한 프로필 데이터
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {
            'name': '홍길동',
            'department': '기계공학과',
            'position': '부교수',
        }

        # Act
        form = ProfileUpdateForm(data=form_data, instance=self.user)

        # Assert
        self.assertTrue(form.is_valid())

    def test_profile_update_form_excludes_email(self):
        """
        Given: 이메일 필드 포함 시도
        When: 폼 생성
        Then: 이메일 필드가 폼에 없음
        """
        # Arrange & Act
        form = ProfileUpdateForm(instance=self.user)

        # Assert
        self.assertNotIn('email', form.fields)

    def test_profile_update_form_excludes_role(self):
        """
        Given: role 필드 포함 시도
        When: 폼 생성
        Then: role 필드가 폼에 없음
        """
        # Arrange & Act
        form = ProfileUpdateForm(instance=self.user)

        # Assert
        self.assertNotIn('role', form.fields)


class PasswordChangeFormTest(TestCase):
    """비밀번호 변경 폼 단위 테스트"""

    def setUp(self):
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
        )
        self.user.set_password('old_password')
        self.user.save()

    def test_password_change_form_valid_data(self):
        """
        Given: 올바른 현재 비밀번호와 새 비밀번호
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {
            'current_password': 'old_password',
            'new_password': 'new_password123',
            'new_password_confirm': 'new_password123',
        }

        # Act
        form = PasswordChangeForm(data=form_data, user=self.user)

        # Assert
        self.assertTrue(form.is_valid())

    def test_password_change_form_invalid_current_password(self):
        """
        Given: 잘못된 현재 비밀번호
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {
            'current_password': 'wrong_password',
            'new_password': 'new_password123',
            'new_password_confirm': 'new_password123',
        }

        # Act
        form = PasswordChangeForm(data=form_data, user=self.user)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('current_password', form.errors)

    def test_password_change_form_new_passwords_mismatch(self):
        """
        Given: 새 비밀번호 불일치
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {
            'current_password': 'old_password',
            'new_password': 'new_password123',
            'new_password_confirm': 'different_password',
        }

        # Act
        form = PasswordChangeForm(data=form_data, user=self.user)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_password_change_form_new_same_as_current(self):
        """
        Given: 새 비밀번호가 현재 비밀번호와 동일
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {
            'current_password': 'old_password',
            'new_password': 'old_password',
            'new_password_confirm': 'old_password',
        }

        # Act
        form = PasswordChangeForm(data=form_data, user=self.user)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)


class ChangeRoleFormTest(TestCase):
    """권한 변경 폼 단위 테스트"""

    def test_change_role_form_valid_choices(self):
        """
        Given: 유효한 역할 선택
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {'role': 'manager'}

        # Act
        form = ChangeRoleForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())

    def test_change_role_form_invalid_choice(self):
        """
        Given: 유효하지 않은 역할
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {'role': 'invalid_role'}

        # Act
        form = ChangeRoleForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())


class RejectUserFormTest(TestCase):
    """사용자 거부 폼 단위 테스트"""

    def test_reject_user_form_requires_reason(self):
        """
        Given: 거부 사유 누락
        When: 폼 검증
        Then: 검증 실패
        """
        # Arrange
        form_data = {'reason': ''}

        # Act
        form = RejectUserForm(data=form_data)

        # Assert
        self.assertFalse(form.is_valid())
        self.assertIn('reason', form.errors)

    def test_reject_user_form_valid_reason(self):
        """
        Given: 유효한 거부 사유
        When: 폼 검증
        Then: 검증 성공
        """
        # Arrange
        form_data = {'reason': '자격 요건 미충족'}

        # Act
        form = RejectUserForm(data=form_data)

        # Assert
        self.assertTrue(form.is_valid())
```

---

### 3.3 뷰 테스트 (Integration Tests)

#### 테스트 파일: `apps/authentication/tests/test_admin_views.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class AdminUserListViewTest(TestCase):
    """관리자 사용자 목록 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
            is_staff=True,
        )
        self.admin.set_password('admin1234')
        self.admin.save()

        # 테스트용 사용자들
        User.objects.create(
            email='pending1@university.ac.kr',
            name='대기1',
            status='pending',
        )
        User.objects.create(
            email='active1@university.ac.kr',
            name='활성1',
            status='active',
        )

    def test_admin_user_list_view(self):
        """
        Given: admin 로그인
        When: GET /admin/users
        Then: 사용자 목록 렌더링
        """
        # Arrange
        self.client.force_login(self.admin)

        # Act
        response = self.client.get(reverse('admin_user_list'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/user_list.html')

    def test_filter_users_by_status(self):
        """
        Given: status=pending 쿼리 파라미터
        When: GET /admin/users?status=pending
        Then: pending 사용자만 표시
        """
        # Arrange
        self.client.force_login(self.admin)

        # Act
        response = self.client.get(reverse('admin_user_list'), {'status': 'pending'})

        # Assert
        self.assertEqual(response.status_code, 200)
        users = response.context['users']
        self.assertTrue(all(u.status == 'pending' for u in users))

    def test_non_admin_cannot_access(self):
        """
        Given: viewer 사용자
        When: GET /admin/users
        Then: 403 Forbidden
        """
        # Arrange
        viewer = User.objects.create(
            email='viewer@university.ac.kr',
            name='Viewer',
            role='viewer',
            status='active',
        )
        self.client.force_login(viewer)

        # Act
        response = self.client.get(reverse('admin_user_list'))

        # Assert
        self.assertEqual(response.status_code, 403)


class ApproveUserViewTest(TestCase):
    """사용자 승인 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.client.force_login(self.admin)

        self.pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기',
            status='pending',
        )

    def test_approve_user_view(self):
        """
        Given: pending 사용자
        When: POST /admin/users/{id}/approve
        Then: status가 'active'로 변경
        """
        # Arrange
        url = reverse('approve_user', kwargs={'user_id': self.pending_user.id})

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, 302)  # 리디렉션
        self.pending_user.refresh_from_db()
        self.assertEqual(self.pending_user.status, 'active')

    def test_approve_shows_success_message(self):
        """
        Given: pending 사용자
        When: 승인 요청
        Then: 성공 메시지 표시
        """
        # Arrange
        url = reverse('approve_user', kwargs={'user_id': self.pending_user.id})

        # Act
        response = self.client.post(url, follow=True)

        # Assert
        messages = list(response.context['messages'])
        self.assertTrue(any('승인되었습니다' in str(m) for m in messages))

    def test_approve_already_active_user(self):
        """
        Given: 이미 active 사용자
        When: 승인 요청
        Then: 에러 메시지
        """
        # Arrange
        active_user = User.objects.create(
            email='active@university.ac.kr',
            name='활성',
            status='active',
        )
        url = reverse('approve_user', kwargs={'user_id': active_user.id})

        # Act
        response = self.client.post(url, follow=True)

        # Assert
        messages = list(response.context['messages'])
        self.assertTrue(any('이미 활성' in str(m) for m in messages))


class RejectUserViewTest(TestCase):
    """사용자 거부 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.client.force_login(self.admin)

        self.pending_user = User.objects.create(
            email='pending@university.ac.kr',
            name='대기',
            status='pending',
        )

    def test_reject_user_view(self):
        """
        Given: pending 사용자 및 거부 사유
        When: POST /admin/users/{id}/reject
        Then: status가 'inactive'로 변경
        """
        # Arrange
        url = reverse('reject_user', kwargs={'user_id': self.pending_user.id})
        form_data = {'reason': '자격 요건 미충족'}

        # Act
        response = self.client.post(url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.pending_user.refresh_from_db()
        self.assertEqual(self.pending_user.status, 'inactive')
        self.assertEqual(self.pending_user.rejection_reason, '자격 요건 미충족')

    def test_reject_requires_reason(self):
        """
        Given: 거부 사유 없음
        When: POST /admin/users/{id}/reject
        Then: 폼 에러
        """
        # Arrange
        url = reverse('reject_user', kwargs={'user_id': self.pending_user.id})
        form_data = {'reason': ''}

        # Act
        response = self.client.post(url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)  # 폼 재렌더링
        self.assertContains(response, '필수 항목')


class ChangeUserRoleViewTest(TestCase):
    """권한 변경 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.client.force_login(self.admin)

        self.viewer = User.objects.create(
            email='viewer@university.ac.kr',
            name='Viewer',
            role='viewer',
            status='active',
        )

    def test_change_user_role_view(self):
        """
        Given: viewer 사용자
        When: POST /admin/users/{id}/change-role (manager)
        Then: role이 'manager'로 변경
        """
        # Arrange
        url = reverse('change_user_role', kwargs={'user_id': self.viewer.id})
        form_data = {'role': 'manager'}

        # Act
        response = self.client.post(url, data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, 'manager')

    def test_cannot_change_own_role(self):
        """
        Given: 자기 자신의 ID
        When: POST /admin/users/{self_id}/change-role
        Then: 에러 메시지
        """
        # Arrange
        url = reverse('change_user_role', kwargs={'user_id': self.admin.id})
        form_data = {'role': 'viewer'}

        # Act
        response = self.client.post(url, data=form_data, follow=True)

        # Assert
        messages = list(response.context['messages'])
        self.assertTrue(any('자신의 권한' in str(m) for m in messages))
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, 'admin')  # 변경되지 않음


class UploadHistoryListViewTest(TestCase):
    """업로드 이력 조회 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        self.client.force_login(self.admin)

        from apps.data_upload.models import UploadHistory
        UploadHistory.objects.create(
            user=self.admin,
            file_name='test1.xlsx',
            file_size=1024,
            data_type='department_kpi',
            status='success',
        )
        UploadHistory.objects.create(
            user=self.admin,
            file_name='test2.xlsx',
            file_size=2048,
            data_type='publication',
            status='failed',
            error_message='Invalid data',
        )

    def test_upload_history_list_view(self):
        """
        Given: admin 로그인
        When: GET /data/history
        Then: 업로드 이력 목록 렌더링
        """
        # Act
        response = self.client.get(reverse('upload_history'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'data_upload/history.html')

    def test_filter_upload_history_by_status(self):
        """
        Given: status=failed 쿼리 파라미터
        When: GET /data/history?status=failed
        Then: 실패한 이력만 표시
        """
        # Act
        response = self.client.get(reverse('upload_history'), {'status': 'failed'})

        # Assert
        self.assertEqual(response.status_code, 200)
        history_list = response.context['upload_history']
        self.assertTrue(all(h.status == 'failed' for h in history_list))


class ProfileViewTest(TestCase):
    """프로필 관리 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            department='컴퓨터공학과',
            position='교수',
            status='active',
        )
        self.client.force_login(self.user)

    def test_profile_view_shows_user_info(self):
        """
        Given: 로그인된 사용자
        When: GET /profile
        Then: 사용자 정보 표시
        """
        # Act
        response = self.client.get(reverse('profile'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '테스트')
        self.assertContains(response, 'test@university.ac.kr')

    def test_profile_update_saves_changes(self):
        """
        Given: 수정된 프로필 데이터
        When: POST /profile
        Then: 변경 사항 저장
        """
        # Arrange
        form_data = {
            'name': '홍길동',
            'department': '기계공학과',
            'position': '부교수',
        }

        # Act
        response = self.client.post(reverse('profile'), data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, '홍길동')
        self.assertEqual(self.user.department, '기계공학과')


class PasswordChangeViewTest(TestCase):
    """비밀번호 변경 뷰 통합 테스트"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            email='test@university.ac.kr',
            name='테스트',
            status='active',
        )
        self.user.set_password('old_password')
        self.user.save()
        self.client.force_login(self.user)

    def test_password_change_saves_new_password(self):
        """
        Given: 올바른 현재 비밀번호와 새 비밀번호
        When: POST /profile/password
        Then: 비밀번호 변경됨
        """
        # Arrange
        form_data = {
            'current_password': 'old_password',
            'new_password': 'new_password123',
            'new_password_confirm': 'new_password123',
        }

        # Act
        response = self.client.post(reverse('password_change'), data=form_data)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password123'))

    def test_password_change_invalid_current_password(self):
        """
        Given: 잘못된 현재 비밀번호
        When: POST /profile/password
        Then: 에러 메시지
        """
        # Arrange
        form_data = {
            'current_password': 'wrong_password',
            'new_password': 'new_password123',
            'new_password_confirm': 'new_password123',
        }

        # Act
        response = self.client.post(reverse('password_change'), data=form_data)

        # Assert
        self.assertEqual(response.status_code, 200)  # 폼 재렌더링
        self.assertContains(response, '현재 비밀번호가 올바르지 않습니다')
```

---

### 3.4 Acceptance Tests (End-to-End)

#### 테스트 파일: `apps/authentication/tests/test_admin_acceptance.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from apps.authentication.models import User


class UserApprovalAcceptanceTest(TestCase):
    """사용자 승인 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()

    def test_full_user_approval_flow(self):
        """
        Scenario: 신규 회원가입 → 관리자 로그인 → 사용자 목록 조회 → 승인 → 로그인 가능
        Given: 신규 가입한 pending 사용자
        When: 관리자가 승인
        Then: 사용자가 로그인 가능
        """
        # Step 1: 관리자 생성
        admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
            is_staff=True,
        )
        admin.set_password('admin1234')
        admin.save()

        # Step 2: pending 사용자 생성 (회원가입 시뮬레이션)
        pending_user = User.objects.create(
            email='newuser@university.ac.kr',
            name='신규 사용자',
            status='pending',
        )
        pending_user.set_password('user1234')
        pending_user.save()

        # Step 3: 관리자 로그인
        self.client.force_login(admin)

        # Step 4: 사용자 목록 조회
        response = self.client.get(reverse('admin_user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'newuser@university.ac.kr')

        # Step 5: 승인 대기 사용자 필터링
        response = self.client.get(reverse('admin_user_list'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)

        # Step 6: 사용자 승인
        url = reverse('approve_user', kwargs={'user_id': pending_user.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        # Step 7: 승인 확인
        pending_user.refresh_from_db()
        self.assertEqual(pending_user.status, 'active')

        # Step 8: 관리자 로그아웃
        self.client.logout()

        # Step 9: 승인된 사용자 로그인 시도
        login_successful = self.client.login(
            username='newuser@university.ac.kr',
            password='user1234'
        )
        self.assertTrue(login_successful)

        # Step 10: 대시보드 접근 확인
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class UserRejectionAcceptanceTest(TestCase):
    """사용자 거부 전체 플로우 Acceptance Test"""

    def setUp(self):
        self.client = Client()

    def test_full_user_rejection_flow(self):
        """
        Scenario: 신규 회원가입 → 관리자 로그인 → 거부 사유 입력 → 거부 → 로그인 불가
        Given: 신규 가입한 pending 사용자
        When: 관리자가 거부
        Then: 사용자가 로그인 불가
        """
        # Step 1: 관리자 및 pending 사용자 생성
        admin = User.objects.create(
            email='admin@university.ac.kr',
            name='관리자',
            role='admin',
            status='active',
        )
        admin.set_password('admin1234')
        admin.save()

        pending_user = User.objects.create(
            email='rejected@university.ac.kr',
            name='거부 대상',
            status='pending',
        )
        pending_user.set_password('user1234')
        pending_user.save()

        # Step 2: 관리자 로그인
        self.client.force_login(admin)

        # Step 3: 사용자 거부
        url = reverse('reject_user', kwargs={'user_id': pending_user.id})
        form_data = {'reason': '자격 요건 미충족'}
        response = self.client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Step 4: 거부 확인
        pending_user.refresh_from_db()
        self.assertEqual(pending_user.status, 'inactive')
        self.assertEqual(pending_user.rejection_reason, '자격 요건 미충족')

        # Step 5: 관리자 로그아웃
        self.client.logout()

        # Step 6: 거부된 사용자 로그인 시도 (실패)
        from apps.authentication.forms import LoginForm
        form_data = {
            'email': 'rejected@university.ac.kr',
            'password': 'user1234',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('비활성화', str(form.errors))
```

---

## 4. AAA 패턴 적용 예제

### 4.1 모델 메서드 테스트 (AAA)

```python
def test_approve_user_method(self):
    """
    Given: pending 상태 사용자
    When: approve() 메서드 호출
    Then: status가 'active'로 변경됨
    """
    # Arrange (준비)
    # 1. pending 사용자 생성
    user = User.objects.create(
        email='pending@university.ac.kr',
        name='대기 사용자',
        status='pending',
    )

    # Act (실행)
    # approve() 메서드 호출
    user.approve()

    # Assert (검증)
    # 1. DB에서 다시 읽기
    user.refresh_from_db()
    # 2. status 확인
    self.assertEqual(user.status, 'active', "승인 후 status는 'active'여야 함")
```

---

## 5. FIRST 원칙 적용

### 5.1 Fast (빠른 테스트)
- 모델 메서드 테스트: 각 10ms 이하
- 폼 테스트: 각 20ms 이하
- 뷰 테스트: 각 100ms 이하

### 5.2 Independent (독립적)
```python
class IndependentTest(TestCase):
    def setUp(self):
        """각 테스트마다 독립적으로 실행"""
        self.user = User.objects.create(...)

    def test_a(self):
        """독립적 테스트 A"""
        pass

    def test_b(self):
        """독립적 테스트 B (test_a와 무관)"""
        pass
```

### 5.3 Repeatable (반복 가능)
- 고정된 테스트 데이터 사용
- 외부 의존성 없음
- 트랜잭션 롤백 보장

### 5.4 Self-validating (자가 검증)
```python
def test_approve_changes_status(self):
    """승인 시 상태 변경 검증 (자가 검증)"""
    # Arrange
    user = User.objects.create(status='pending')

    # Act
    user.approve()

    # Assert
    user.refresh_from_db()
    self.assertEqual(user.status, 'active', "승인 후 상태는 active여야 함")
```

### 5.5 Timely (적시성)
- 코드 작성 전 테스트 먼저 작성
- Red → Green → Refactor 사이클 준수

---

## 6. 테스트 실행 계획

### 6.1 테스트 실행 명령어

```bash
# 전체 관리자 기능 테스트 실행
python manage.py test apps.authentication.tests.test_admin_views
python manage.py test apps.authentication.tests.test_admin_acceptance

# Unit 테스트만 실행
python manage.py test apps.authentication.tests.test_models
python manage.py test apps.authentication.tests.test_forms

# 코드 커버리지 측정
coverage run --source='apps.authentication' manage.py test apps.authentication
coverage report
coverage html
```

### 6.2 테스트 실행 시간 예상

| 테스트 유형 | 개수 | 예상 시간 | 비고 |
|------------|------|----------|------|
| Unit (모델) | 15 | 0.5초 | 빠른 메서드 호출 |
| Unit (폼) | 20 | 1초 | 폼 검증 로직 |
| Integration (뷰) | 15 | 4초 | DB + 뷰 렌더링 |
| Acceptance | 5 | 3초 | 전체 플로우 |
| **총합** | **55** | **8.5초** | 충분히 빠름 |

---

## 7. 커밋 전략

### 7.1 작은 단위 커밋

```bash
# Phase 2 Cycle 2 완료 후
git add apps/authentication/models.py apps/authentication/tests/test_models.py
git commit -m "test: 사용자 승인 메서드 테스트 및 구현

- Red: test_approve_user_method() 작성
- Green: User.approve() 메서드 구현
- Refactor: 트랜잭션 처리 추가
"

# Phase 5 Cycle 3 완료 후
git add apps/authentication/views.py apps/authentication/tests/test_admin_views.py
git commit -m "test: 프로필 수정 저장 테스트 및 구현

- Red: test_profile_update_saves_changes() 작성
- Green: ProfileUpdateView에서 form.save() 호출
- Refactor: 변경 사항 없을 시 메시지 추가
"
```

---

## 8. 체크리스트

### 8.1 각 Cycle 완료 시
- [ ] Red: 실패하는 테스트 작성
- [ ] 테스트 실행하여 실패 확인
- [ ] Green: 최소한의 코드로 통과
- [ ] 테스트 실행하여 성공 확인
- [ ] Refactor: 코드 개선
- [ ] 모든 테스트 재실행
- [ ] 커밋

### 8.2 Phase 완료 시
- [ ] 해당 Phase 모든 테스트 통과
- [ ] 코드 커버리지 80% 이상
- [ ] 권한 체크 확인
- [ ] 문서 업데이트
- [ ] 다음 Phase 진행

### 8.3 전체 완료 시
- [ ] 모든 테스트 통과 (Unit + Integration + Acceptance)
- [ ] 코드 커버리지 85% 이상
- [ ] 보안 검토 (권한 체크, CSRF)
- [ ] 성능 검토 (쿼리 최적화)
- [ ] Django Admin UI 수동 테스트
- [ ] Pull Request 생성

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2025-11-02 | 초안 작성<br>- 관리자 기능 TDD 구현 계획<br>- 55개 테스트 시나리오<br>- 사용자 승인/거부, 권한 관리, 프로필 관리 테스트 | Claude Code |

---

## 10. 참고 문서

- [TDD 가이드라인](/Users/seunghyun/Test/vmc6/docs/tdd.md)
- [Database Schema](/Users/seunghyun/Test/vmc6/docs/database.md)
- [UC-09: 사용자 승인](/Users/seunghyun/Test/vmc6/docs/usecases/09-user-approval/spec.md)
- [UC-10: 프로필 관리](/Users/seunghyun/Test/vmc6/docs/usecases/10-profile-management/spec.md)
- [UC-12: 업로드 이력](/Users/seunghyun/Test/vmc6/docs/usecases/12-upload-history/spec.md)
- [인증 구현 계획](/Users/seunghyun/Test/vmc6/docs/pages/01-auth/plan.md)

---

**문서 작성 완료**
**다음 작업**: Phase 1 (사용자 목록 조회 및 필터링) 구현 시작
