"""
Tests for data filtering functions.

This module contains tests for functions that filter querysets based on:
- Date ranges
- Department access
- College access
- User permissions (role-based)
- Multiple combined filters

Test Coverage:
- Date range filtering
- Department filtering
- College filtering
- Permission-based filtering (admin/manager/viewer)
- Multiple filters combined
- Edge cases: None values, empty results, invalid inputs

Following TDD RED-GREEN-REFACTOR cycle:
- RED: These tests will fail until filters.py is implemented
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize and clean up
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    Student,
)
from apps.analytics.filters import (
    filter_by_date_range,
    filter_by_department,
    filter_by_college,
    apply_user_permission_filter,
    apply_multiple_filters,
)

User = get_user_model()


class FilterByDateRangeTest(TestCase):
    """
    Test suite for filter_by_date_range function.

    Validates filtering querysets by date ranges with various field names.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data for date range filtering."""
        from django.utils import timezone

        cls.kpi1 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2021,
            created_at=timezone.make_aware(timezone.datetime(2021, 12, 31)),
            employment_rate=85.5,
            full_time_faculty=10,
        )
        cls.kpi2 = DepartmentKPI.objects.create(
            department='전자공학과',
            college='공과대학',
            evaluation_year=2022,
            created_at=timezone.make_aware(timezone.datetime(2022, 12, 31)),
            employment_rate=88.0,
            full_time_faculty=12,
        )
        cls.kpi3 = DepartmentKPI.objects.create(
            department='기계공학과',
            college='공과대학',
            evaluation_year=2023,
            created_at=timezone.make_aware(timezone.datetime(2023, 12, 31)),
            employment_rate=82.3,
            full_time_faculty=11,
        )

    def test_filter_with_both_dates(self):
        """Should filter records between start and end dates."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        start_date = timezone.make_aware(timezone.datetime(2022, 1, 1))
        end_date = timezone.make_aware(timezone.datetime(2022, 12, 31))

        # Act
        result = filter_by_date_range(queryset, 'created_at', start_date, end_date)

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().evaluation_year, 2022)

    def test_filter_with_only_start_date(self):
        """Should filter records from start date onwards."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        start_date = timezone.make_aware(timezone.datetime(2022, 6, 1))

        # Act
        result = filter_by_date_range(queryset, 'created_at', start_date=start_date)

        # Assert
        self.assertEqual(result.count(), 2)  # 2022 and 2023

    def test_filter_with_only_end_date(self):
        """Should filter records up to end date."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        end_date = timezone.make_aware(timezone.datetime(2022, 6, 1))

        # Act
        result = filter_by_date_range(queryset, 'created_at', end_date=end_date)

        # Assert
        self.assertEqual(result.count(), 1)  # Only 2021

    def test_filter_with_no_dates(self):
        """Should return all records when no dates provided."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = filter_by_date_range(queryset, 'created_at')

        # Assert
        self.assertEqual(result.count(), 3)

    def test_filter_with_no_matches(self):
        """Should return empty queryset when no records match."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        start_date = timezone.make_aware(timezone.datetime(2025, 1, 1))
        end_date = timezone.make_aware(timezone.datetime(2025, 12, 31))

        # Act
        result = filter_by_date_range(queryset, 'created_at', start_date, end_date)

        # Assert
        self.assertEqual(result.count(), 0)


class FilterByDepartmentTest(TestCase):
    """
    Test suite for filter_by_department function.

    Validates filtering querysets by department names.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data for department filtering."""
        cls.kpi1 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=85.5,
            full_time_faculty=10,
        )
        cls.kpi2 = DepartmentKPI.objects.create(
            department='전자공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=88.0,
            full_time_faculty=12,
        )
        cls.kpi3 = DepartmentKPI.objects.create(
            department='수학과',
            college='자연과학대학',
            evaluation_year=2023,
            employment_rate=80.0,
            full_time_faculty=8,
        )

    def test_filter_single_department(self):
        """Should filter by single department."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        departments = ['컴퓨터공학과']

        # Act
        result = filter_by_department(queryset, departments)

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().department, '컴퓨터공학과')

    def test_filter_multiple_departments(self):
        """Should filter by multiple departments."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        departments = ['컴퓨터공학과', '전자공학과']

        # Act
        result = filter_by_department(queryset, departments)

        # Assert
        self.assertEqual(result.count(), 2)
        dept_names = [kpi.department for kpi in result]
        self.assertIn('컴퓨터공학과', dept_names)
        self.assertIn('전자공학과', dept_names)

    def test_filter_with_none_departments(self):
        """Should return all records when departments is None."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = filter_by_department(queryset, None)

        # Assert
        self.assertEqual(result.count(), 3)

    def test_filter_with_empty_list(self):
        """Should return all records when departments is empty list."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = filter_by_department(queryset, [])

        # Assert
        self.assertEqual(result.count(), 3)

    def test_filter_with_nonexistent_department(self):
        """Should return empty queryset for nonexistent department."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        departments = ['존재하지않는학과']

        # Act
        result = filter_by_department(queryset, departments)

        # Assert
        self.assertEqual(result.count(), 0)


class FilterByCollegeTest(TestCase):
    """
    Test suite for filter_by_college function.

    Validates filtering querysets by college names.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data for college filtering."""
        cls.kpi1 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=85.5,
            full_time_faculty=10,
        )
        cls.kpi2 = DepartmentKPI.objects.create(
            department='전자공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=88.0,
            full_time_faculty=12,
        )
        cls.kpi3 = DepartmentKPI.objects.create(
            department='수학과',
            college='자연과학대학',
            evaluation_year=2023,
            employment_rate=80.0,
            full_time_faculty=8,
        )

    def test_filter_single_college(self):
        """Should filter by single college."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        colleges = ['공과대학']

        # Act
        result = filter_by_college(queryset, colleges)

        # Assert
        self.assertEqual(result.count(), 2)

    def test_filter_multiple_colleges(self):
        """Should filter by multiple colleges."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        colleges = ['공과대학', '자연과학대학']

        # Act
        result = filter_by_college(queryset, colleges)

        # Assert
        self.assertEqual(result.count(), 3)

    def test_filter_with_none_colleges(self):
        """Should return all records when colleges is None."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = filter_by_college(queryset, None)

        # Assert
        self.assertEqual(result.count(), 3)


class ApplyUserPermissionFilterTest(TestCase):
    """
    Test suite for apply_user_permission_filter function.

    Validates role-based filtering:
    - Admin: See all data
    - Manager: See all data
    - Viewer: See only own department
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data for permission filtering."""
        # Create users with different roles
        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin_user',
            password='password123',
            department='컴퓨터공학과',
            role='admin',
            is_active='active',
        )
        cls.manager_user = User.objects.create_user(
            email='manager@test.com',
            username='manager_user',
            password='password123',
            department='전자공학과',
            role='manager',
            is_active='active',
        )
        cls.viewer_user = User.objects.create_user(
            email='viewer@test.com',
            username='viewer_user',
            password='password123',
            department='기계공학과',
            role='viewer',
            is_active='active',
        )

        # Create KPI data for different departments
        cls.kpi1 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=85.5,
            full_time_faculty=10,
        )
        cls.kpi2 = DepartmentKPI.objects.create(
            department='전자공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=88.0,
            full_time_faculty=12,
        )
        cls.kpi3 = DepartmentKPI.objects.create(
            department='기계공학과',
            college='공과대학',
            evaluation_year=2023,
            employment_rate=82.3,
            full_time_faculty=11,
        )

    def test_admin_sees_all_data(self):
        """Admin should see all departments."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = apply_user_permission_filter(queryset, self.admin_user)

        # Assert
        self.assertEqual(result.count(), 3)

    def test_manager_sees_all_data(self):
        """Manager should see all departments."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = apply_user_permission_filter(queryset, self.manager_user)

        # Assert
        self.assertEqual(result.count(), 3)

    def test_viewer_sees_only_own_department(self):
        """Viewer should see only their own department."""
        # Arrange
        queryset = DepartmentKPI.objects.all()

        # Act
        result = apply_user_permission_filter(queryset, self.viewer_user)

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().department, '기계공학과')

    def test_viewer_with_no_department_data(self):
        """Viewer should see empty result if their department has no data."""
        # Arrange
        viewer_no_data = User.objects.create_user(
            email='viewer2@test.com',
            username='viewer2_user',
            password='password123',
            department='물리학과',  # No KPI data for this department
            role='viewer',
            is_active='active',
        )
        queryset = DepartmentKPI.objects.all()

        # Act
        result = apply_user_permission_filter(queryset, viewer_no_data)

        # Assert
        self.assertEqual(result.count(), 0)


class ApplyMultipleFiltersTest(TestCase):
    """
    Test suite for apply_multiple_filters function.

    Validates combining multiple filters:
    - Date range
    - Departments
    - Colleges
    - User permissions
    """

    @classmethod
    def setUpTestData(cls):
        """Create test data for multiple filter combinations."""
        from django.utils import timezone

        cls.viewer_user = User.objects.create_user(
            email='viewer@test.com',
            username='viewer_user',
            password='password123',
            department='컴퓨터공학과',
            role='viewer',
            is_active='active',
        )

        cls.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin_user',
            password='password123',
            department='전자공학과',
            role='admin',
            is_active='active',
        )

        # Create KPI data
        cls.kpi1 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2021,
            created_at=timezone.make_aware(timezone.datetime(2021, 12, 31)),
            employment_rate=85.5,
            full_time_faculty=10,
        )
        cls.kpi2 = DepartmentKPI.objects.create(
            department='컴퓨터공학과',
            college='공과대학',
            evaluation_year=2022,
            created_at=timezone.make_aware(timezone.datetime(2022, 12, 31)),
            employment_rate=86.0,
            full_time_faculty=11,
        )
        cls.kpi3 = DepartmentKPI.objects.create(
            department='전자공학과',
            college='공과대학',
            evaluation_year=2022,
            created_at=timezone.make_aware(timezone.datetime(2022, 12, 31)),
            employment_rate=88.0,
            full_time_faculty=12,
        )
        cls.kpi4 = DepartmentKPI.objects.create(
            department='수학과',
            college='자연과학대학',
            evaluation_year=2022,
            created_at=timezone.make_aware(timezone.datetime(2022, 12, 31)),
            employment_rate=80.0,
            full_time_faculty=8,
        )

    def test_apply_date_and_department_filters(self):
        """Should apply both date range and department filters."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        filters = {
            'start_date': timezone.make_aware(timezone.datetime(2022, 1, 1)),
            'end_date': timezone.make_aware(timezone.datetime(2022, 12, 31)),
            'departments': ['컴퓨터공학과'],
        }

        # Act
        result = apply_multiple_filters(queryset, filters, date_field='created_at')

        # Assert
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().evaluation_year, 2022)
        self.assertEqual(result.first().department, '컴퓨터공학과')

    def test_apply_college_filter_only(self):
        """Should apply college filter only."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        filters = {
            'colleges': ['공과대학'],
        }

        # Act
        result = apply_multiple_filters(queryset, filters)

        # Assert
        self.assertEqual(result.count(), 3)

    def test_apply_user_permission_filter(self):
        """Should apply user permission filter."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        filters = {
            'user': self.viewer_user,
        }

        # Act
        result = apply_multiple_filters(queryset, filters)

        # Assert
        self.assertEqual(result.count(), 2)  # Only 컴퓨터공학과 records
        for kpi in result:
            self.assertEqual(kpi.department, '컴퓨터공학과')

    def test_apply_combined_filters(self):
        """Should apply all filters combined."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        filters = {
            'start_date': timezone.make_aware(timezone.datetime(2022, 1, 1)),
            'end_date': timezone.make_aware(timezone.datetime(2022, 12, 31)),
            'departments': ['컴퓨터공학과', '전자공학과'],
            'colleges': ['공과대학'],
            'user': self.admin_user,
        }

        # Act
        result = apply_multiple_filters(queryset, filters, date_field='created_at')

        # Assert
        self.assertEqual(result.count(), 2)  # 2022 records for CS and EE

    def test_apply_no_filters(self):
        """Should return all records when no filters provided."""
        # Arrange
        queryset = DepartmentKPI.objects.all()
        filters = {}

        # Act
        result = apply_multiple_filters(queryset, filters)

        # Assert
        self.assertEqual(result.count(), 4)

    def test_filters_with_no_matches(self):
        """Should return empty queryset when filters match nothing."""
        # Arrange
        from django.utils import timezone
        queryset = DepartmentKPI.objects.all()
        filters = {
            'start_date': timezone.make_aware(timezone.datetime(2025, 1, 1)),
            'end_date': timezone.make_aware(timezone.datetime(2025, 12, 31)),
        }

        # Act
        result = apply_multiple_filters(queryset, filters, date_field='created_at')

        # Assert
        self.assertEqual(result.count(), 0)
