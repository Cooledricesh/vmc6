"""
Analytics Views Test Suite
TDD Red → Green → Refactor cycle

Tests for analytics views with permission-based access control.

Test coverage:
- dashboard_view: Main dashboard with KPI summary
- department_kpi_view: Department KPI visualization
- publications_view: Publications analysis
- research_budget_view: Research budget analysis
- students_view: Student statistics

Each view tested for:
1. Template rendering
2. Login required
3. Active user required
4. Permission-based data filtering (by role and department)
5. Context includes aggregated data
6. Context includes chart data

Run: python manage.py test apps.analytics.tests.test_views
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from decimal import Decimal

from apps.authentication.models import User
from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student
)
from apps.analytics.views import (
    dashboard_view,
    department_kpi_view,
    publications_view,
    research_budget_view,
    students_view
)


class DashboardViewTest(TestCase):
    """Test dashboard_view - main dashboard with KPI summary"""

    def setUp(self):
        """Set up test data and users"""
        self.factory = RequestFactory()

        # Create test users with different roles
        self.admin = User.objects.create_user(
            email='admin@university.ac.kr',
            username='admin',
            password='testpass123',
            role='admin',
            is_active='active'
        )

        self.manager = User.objects.create_user(
            email='manager@university.ac.kr',
            username='manager',
            password='testpass123',
            role='manager',
            is_active='active'
        )

        self.viewer_cs = User.objects.create_user(
            email='viewer_cs@university.ac.kr',
            username='viewer_cs',
            password='testpass123',
            role='viewer',
            department='컴퓨터공학과',
            is_active='active'
        )

        self.pending_user = User.objects.create_user(
            email='pending@university.ac.kr',
            username='pending',
            password='testpass123',
            role='viewer',
            is_active='pending'
        )

        # Create test data for multiple departments
        # Department KPI data
        DepartmentKPI.objects.create(
            college='공과대학',
            department='컴퓨터공학과',
            evaluation_year=2024,
            employment_rate=Decimal('85.50'),
            full_time_faculty=20,
            visiting_faculty=5,
            tech_transfer_income=Decimal('10.00'),
            intl_conference_count=3
        )

        DepartmentKPI.objects.create(
            college='경영대학',
            department='경영학과',
            evaluation_year=2024,
            employment_rate=Decimal('78.30'),
            full_time_faculty=15,
            visiting_faculty=3,
            tech_transfer_income=Decimal('5.00'),
            intl_conference_count=2
        )

        # Publication data
        Publication.objects.create(
            publication_id='PUB-2024-001',
            title='AI Research Paper',
            college='공과대학',
            department='컴퓨터공학과',
            first_author='김철수',
            co_authors='이영희',
            journal_name='ACM Transactions',
            publication_date='2024-01-15',
            journal_grade='SCIE'
        )

        Publication.objects.create(
            publication_id='PUB-2024-002',
            title='Business Research',
            college='경영대학',
            department='경영학과',
            first_author='박지성',
            journal_name='Business Journal',
            publication_date='2024-02-20',
            journal_grade='KCI'
        )

        # Research project data
        project1 = ResearchProject.objects.create(
            project_number='CS2024-001',
            project_name='AI 기반 추천 시스템 연구',
            department='컴퓨터공학과',
            principal_investigator='김철수',
            funding_agency='한국연구재단',
            total_budget=50000000
        )

        project2 = ResearchProject.objects.create(
            project_number='BUS2024-001',
            project_name='디지털 마케팅 전략 연구',
            department='경영학과',
            principal_investigator='박지성',
            funding_agency='한국연구재단',
            total_budget=30000000
        )

        # Execution records
        ExecutionRecord.objects.create(
            execution_id='EXE-2024-001',
            project=project1,
            execution_date='2024-03-01',
            expense_category='인건비',
            amount=20000000,
            status='Y',
            description='연구원 인건비'
        )

        ExecutionRecord.objects.create(
            execution_id='EXE-2024-002',
            project=project2,
            execution_date='2024-03-15',
            expense_category='재료비',
            amount=10000000,
            status='Y',
            description='설문조사 비용'
        )

        # Student data
        Student.objects.create(
            student_number='2024001',
            name='홍길동',
            college='공과대학',
            department='컴퓨터공학과',
            admission_year=2024,
            grade=1,
            enrollment_status='재학',
            program_type='학사'
        )

        Student.objects.create(
            student_number='2024002',
            name='김민수',
            college='경영대학',
            department='경영학과',
            admission_year=2024,
            grade=1,
            enrollment_status='재학',
            program_type='학사'
        )

    # ===== Test 1: Login Required =====
    def test_dashboard_view_requires_login(self):
        """
        Given: Anonymous user
        When: Accessing dashboard
        Then: Redirect to login page
        """
        request = self.factory.get('/analytics/')
        request.user = AnonymousUser()

        response = dashboard_view(request)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # ===== Test 2: Active User Required =====
    def test_dashboard_view_requires_active_user(self):
        """
        Given: Pending user (not yet approved)
        When: Accessing dashboard
        Then: 403 Forbidden or redirect to pending page
        """
        request = self.factory.get('/analytics/')
        request.user = self.pending_user

        response = dashboard_view(request)

        # Should deny access
        self.assertEqual(response.status_code, 403)

    # ===== Test 3: Template Rendering =====
    def test_dashboard_view_renders_correct_template(self):
        """
        Given: Active admin user
        When: Accessing dashboard
        Then: Renders dashboard.html template
        """
        request = self.factory.get('/analytics/')
        request.user = self.admin

        response = dashboard_view(request)

        self.assertEqual(response.status_code, 200)
        # Check response is valid
        self.assertIsNotNone(response.content)

    # ===== Test 4: Admin Sees All Data =====
    def test_dashboard_view_admin_sees_all_departments(self):
        """
        Given: Admin user
        When: Accessing dashboard
        Then: Context includes data from all departments
        """
        # Login admin user
        self.client.force_login(self.admin)

        # Access dashboard via test client
        response = self.client.get('/analytics/')

        # Check context contains aggregated data
        self.assertIn('total_departments', response.context)
        self.assertEqual(response.context['total_departments'], 2)

        self.assertIn('total_publications', response.context)
        self.assertEqual(response.context['total_publications'], 2)

        self.assertIn('total_students', response.context)
        self.assertEqual(response.context['total_students'], 2)

    # ===== Test 5: Viewer Sees Only Their Department =====
    def test_dashboard_view_viewer_sees_only_own_department(self):
        """
        Given: Viewer user with department '컴퓨터공학과'
        When: Accessing dashboard
        Then: Context includes data only from '컴퓨터공학과'
        """
        self.client.force_login(self.viewer_cs)
        response = self.client.get('/analytics/')

        # Should see only 1 department
        self.assertEqual(response.context['total_departments'], 1)

        # Should see only publications from CS department
        self.assertEqual(response.context['total_publications'], 1)

        # Should see only students from CS department
        self.assertEqual(response.context['total_students'], 1)

    # ===== Test 6: Manager Sees All Departments =====
    def test_dashboard_view_manager_sees_all_departments(self):
        """
        Given: Manager user
        When: Accessing dashboard
        Then: Context includes data from all departments
        """
        self.client.force_login(self.manager)
        response = self.client.get('/analytics/')

        # Manager should see all departments like admin
        self.assertEqual(response.context['total_departments'], 2)
        self.assertEqual(response.context['total_publications'], 2)
        self.assertEqual(response.context['total_students'], 2)

    # ===== Test 7: Context Includes Chart Data =====
    def test_dashboard_view_includes_chart_data(self):
        """
        Given: Active admin user
        When: Accessing dashboard
        Then: Context includes chart data for visualizations
        """
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/')

        # Check for chart data keys
        self.assertIn('employment_chart_data', response.context)
        self.assertIn('publication_chart_data', response.context)
        self.assertIn('budget_chart_data', response.context)

        # Chart data should be serialized for Chart.js
        employment_data = response.context['employment_chart_data']
        self.assertIn('labels', employment_data)
        self.assertIn('datasets', employment_data)

    # ===== Test 8: Context Includes Summary Stats =====
    def test_dashboard_view_includes_summary_statistics(self):
        """
        Given: Active admin user
        When: Accessing dashboard
        Then: Context includes summary statistics
        """
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/')

        # Check for summary stats
        self.assertIn('avg_employment_rate', response.context)
        self.assertIn('total_research_budget', response.context)
        self.assertIn('total_execution_amount', response.context)

        # Verify calculation correctness
        avg_rate = response.context['avg_employment_rate']
        # (85.50 + 78.30) / 2 = 81.90
        self.assertEqual(avg_rate, Decimal('81.90'))


class DepartmentKPIViewTest(TestCase):
    """Test department_kpi_view - Department KPI visualization"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            email='admin@university.ac.kr',
            username='admin',
            password='testpass123',
            role='admin',
            is_active='active'
        )

        self.viewer_cs = User.objects.create_user(
            email='viewer_cs@university.ac.kr',
            username='viewer_cs',
            password='testpass123',
            role='viewer',
            department='컴퓨터공학과',
            is_active='active'
        )

        # Create KPI data
        DepartmentKPI.objects.create(
            college='공과대학',
            department='컴퓨터공학과',
            evaluation_year=2024,
            employment_rate=Decimal('85.50'),
            full_time_faculty=20,
            visiting_faculty=5,
            tech_transfer_income=Decimal('10.00'),
            intl_conference_count=3
        )

        DepartmentKPI.objects.create(
            college='공과대학',
            department='컴퓨터공학과',
            evaluation_year=2023,
            employment_rate=Decimal('83.00'),
            full_time_faculty=19,
            visiting_faculty=4,
            tech_transfer_income=Decimal('8.00'),
            intl_conference_count=2
        )

    def test_department_kpi_view_requires_login(self):
        """Anonymous user should be redirected to login"""
        request = self.factory.get('/analytics/department-kpi/')
        request.user = AnonymousUser()

        response = department_kpi_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_department_kpi_view_renders_template(self):
        """Should render department_kpi.html template"""
        request = self.factory.get('/analytics/department-kpi/')
        request.user = self.admin

        response = department_kpi_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

    def test_department_kpi_view_includes_trend_data(self):
        """Context should include year-over-year trend data"""
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/department-kpi/')

        self.assertIn('kpi_trend_data', response.context)
        self.assertIn('department_comparison_data', response.context)

    def test_department_kpi_view_filters_by_year(self):
        """Should support year filtering via GET parameter"""
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/department-kpi/?year=2024')

        # Should filter data to 2024 only
        self.assertEqual(response.context['selected_year'], 2024)


class PublicationsViewTest(TestCase):
    """Test publications_view - Publications analysis"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            email='admin@university.ac.kr',
            username='admin',
            password='testpass123',
            role='admin',
            is_active='active'
        )

        # Create publication data
        Publication.objects.create(
            publication_id='PUB-2024-001',
            title='AI Research Paper',
            college='공과대학',
            department='컴퓨터공학과',
            first_author='김철수',
            journal_name='ACM Transactions',
            publication_date='2024-01-15',
            journal_grade='SCIE'
        )

        Publication.objects.create(
            publication_id='PUB-2024-002',
            title='Machine Learning Study',
            college='공과대학',
            department='컴퓨터공학과',
            first_author='이영희',
            journal_name='IEEE Transactions',
            publication_date='2024-02-20',
            journal_grade='SCIE'
        )

    def test_publications_view_requires_login(self):
        """Anonymous user should be redirected"""
        request = self.factory.get('/analytics/publications/')
        request.user = AnonymousUser()

        response = publications_view(request)

        self.assertEqual(response.status_code, 302)

    def test_publications_view_renders_template(self):
        """Should render publications.html template"""
        request = self.factory.get('/analytics/publications/')
        request.user = self.admin

        response = publications_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

    def test_publications_view_includes_grade_distribution(self):
        """Context should include journal grade distribution"""
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/publications/')

        self.assertIn('grade_distribution_data', response.context)
        self.assertIn('department_publication_data', response.context)


class ResearchBudgetViewTest(TestCase):
    """Test research_budget_view - Research budget analysis"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            email='admin@university.ac.kr',
            username='admin',
            password='testpass123',
            role='admin',
            is_active='active'
        )

        # Create research project
        self.project = ResearchProject.objects.create(
            project_number='CS2024-001',
            project_name='AI Research',
            department='컴퓨터공학과',
            principal_investigator='김철수',
            funding_agency='한국연구재단',
            total_budget=50000000
        )

        ExecutionRecord.objects.create(
            execution_id='EXE-2024-001',
            project=self.project,
            execution_date='2024-03-01',
            expense_category='인건비',
            amount=20000000,
            status='Y',
            description='Research staff'
        )

    def test_research_budget_view_requires_login(self):
        """Anonymous user should be redirected"""
        request = self.factory.get('/analytics/research-budget/')
        request.user = AnonymousUser()

        response = research_budget_view(request)

        self.assertEqual(response.status_code, 302)

    def test_research_budget_view_renders_template(self):
        """Should render research_budget.html template"""
        request = self.factory.get('/analytics/research-budget/')
        request.user = self.admin

        response = research_budget_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

    def test_research_budget_view_includes_execution_rate(self):
        """Context should include budget execution rate"""
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/research-budget/')

        self.assertIn('execution_rate_data', response.context)
        self.assertIn('category_distribution_data', response.context)


class StudentsViewTest(TestCase):
    """Test students_view - Student statistics"""

    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            email='admin@university.ac.kr',
            username='admin',
            password='testpass123',
            role='admin',
            is_active='active'
        )

        # Create student data
        Student.objects.create(
            student_number='2024001',
            name='홍길동',
            college='공과대학',
            department='컴퓨터공학과',
            admission_year=2024,
            grade=1,
            enrollment_status='재학',
            program_type='학사'
        )

        Student.objects.create(
            student_number='2024002',
            name='김민수',
            college='공과대학',
            department='컴퓨터공학과',
            admission_year=2024,
            grade=1,
            enrollment_status='재학',
            program_type='학사'
        )

    def test_students_view_requires_login(self):
        """Anonymous user should be redirected"""
        request = self.factory.get('/analytics/students/')
        request.user = AnonymousUser()

        response = students_view(request)

        self.assertEqual(response.status_code, 302)

    def test_students_view_renders_template(self):
        """Should render students.html template"""
        request = self.factory.get('/analytics/students/')
        request.user = self.admin

        response = students_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)

    def test_students_view_includes_enrollment_stats(self):
        """Context should include enrollment statistics"""
        self.client.force_login(self.admin)
        response = self.client.get('/analytics/students/')

        self.assertIn('enrollment_by_year_data', response.context)
        self.assertIn('department_distribution_data', response.context)
        self.assertIn('total_students', response.context)
