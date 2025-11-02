"""
RED Phase: Tests for data aggregators.

This module tests all data aggregation logic for analytics.
Aggregators are responsible for computing statistics and metrics from database models.

Test strategy:
- Test each aggregator method independently
- Use AAA pattern (Arrange, Act, Assert)
- Test with sample data fixtures
- Test edge cases (empty data, null values)
"""
from django.test import TestCase
from decimal import Decimal
from datetime import date, datetime

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student
)
from apps.analytics.aggregators import (
    DepartmentKPIAggregator,
    PublicationAggregator,
    ResearchBudgetAggregator,
    StudentAggregator
)


class DepartmentKPIAggregatorTest(TestCase):
    """Test DepartmentKPIAggregator class"""

    def setUp(self):
        """Set up test data"""
        # Create sample KPI data
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=Decimal('88.50'),
            full_time_faculty=17,
            visiting_faculty=5,
            tech_transfer_income=Decimal('13.50'),
            intl_conference_count=4
        )
        DepartmentKPI.objects.create(
            evaluation_year=2025,
            college='공과대학',
            department='전자공학과',
            employment_rate=Decimal('85.00'),
            full_time_faculty=15,
            visiting_faculty=3,
            tech_transfer_income=Decimal('10.00'),
            intl_conference_count=2
        )
        DepartmentKPI.objects.create(
            evaluation_year=2024,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=Decimal('87.00'),
            full_time_faculty=16,
            visiting_faculty=4,
            tech_transfer_income=Decimal('12.00'),
            intl_conference_count=3
        )

        self.aggregator = DepartmentKPIAggregator()

    def test_aggregator_exists(self):
        """Test that DepartmentKPIAggregator can be instantiated"""
        self.assertIsNotNone(self.aggregator)

    def test_get_average_employment_rate(self):
        """Test average employment rate calculation"""
        # Arrange: data already set up

        # Act
        result = self.aggregator.get_average_employment_rate(year=2025)

        # Assert
        expected = Decimal('86.75')  # (88.50 + 85.00) / 2
        self.assertEqual(result, expected)

    def test_get_average_employment_rate_no_data(self):
        """Test average employment rate with no data"""
        # Act
        result = self.aggregator.get_average_employment_rate(year=2099)

        # Assert
        self.assertIsNone(result)

    def test_get_kpi_by_department(self):
        """Test KPI retrieval by department"""
        # Arrange
        departments = ['컴퓨터공학과']

        # Act
        result = self.aggregator.get_kpi_by_department(
            departments=departments,
            year=2025
        )

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].department, '컴퓨터공학과')
        self.assertEqual(result[0].employment_rate, Decimal('88.50'))

    def test_get_kpi_trend_by_year(self):
        """Test KPI trend analysis over years"""
        # Arrange
        department = '컴퓨터공학과'
        years = [2024, 2025]

        # Act
        result = self.aggregator.get_kpi_trend_by_year(
            department=department,
            years=years
        )

        # Assert
        self.assertEqual(len(result), 2)
        # Check ordering (should be DESC by year)
        self.assertEqual(result[0].evaluation_year, 2025)
        self.assertEqual(result[1].evaluation_year, 2024)

    def test_get_kpi_by_college(self):
        """Test KPI aggregation by college"""
        # Act
        result = self.aggregator.get_kpi_by_college(college='공과대학', year=2025)

        # Assert
        self.assertEqual(len(result), 2)
        # Should include both departments
        dept_names = [kpi.department for kpi in result]
        self.assertIn('컴퓨터공학과', dept_names)
        self.assertIn('전자공학과', dept_names)


class PublicationAggregatorTest(TestCase):
    """Test PublicationAggregator class"""

    def setUp(self):
        """Set up test data"""
        Publication.objects.create(
            publication_id='PUB-25-001',
            publication_date=date(2025, 6, 15),
            college='공과대학',
            department='컴퓨터공학과',
            title='AI Research Paper 1',
            first_author='김교수',
            journal_name='IEEE Journal',
            journal_grade='SCIE',
            impact_factor=Decimal('10.60'),
            project_linked='Y'
        )
        Publication.objects.create(
            publication_id='PUB-25-002',
            publication_date=date(2025, 5, 10),
            college='공과대학',
            department='컴퓨터공학과',
            title='AI Research Paper 2',
            first_author='이교수',
            journal_name='ACM Journal',
            journal_grade='SCIE',
            impact_factor=Decimal('8.50'),
            project_linked='N'
        )
        Publication.objects.create(
            publication_id='PUB-25-003',
            publication_date=date(2025, 4, 20),
            college='공과대학',
            department='전자공학과',
            title='Electronics Paper',
            first_author='박교수',
            journal_name='Korean Journal',
            journal_grade='KCI',
            impact_factor=None,
            project_linked='N'
        )

        self.aggregator = PublicationAggregator()

    def test_aggregator_exists(self):
        """Test that PublicationAggregator can be instantiated"""
        self.assertIsNotNone(self.aggregator)

    def test_get_total_publication_count(self):
        """Test total publication count"""
        # Act
        result = self.aggregator.get_total_publication_count()

        # Assert
        self.assertEqual(result, 3)

    def test_get_total_publication_count_with_filter(self):
        """Test publication count with department filter"""
        # Act
        result = self.aggregator.get_total_publication_count(
            department='컴퓨터공학과'
        )

        # Assert
        self.assertEqual(result, 2)

    def test_get_publications_by_journal_grade(self):
        """Test publication distribution by journal grade"""
        # Act
        result = self.aggregator.get_publications_by_journal_grade()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['SCIE'], 2)
        self.assertEqual(result['KCI'], 1)

    def test_get_average_impact_factor(self):
        """Test average impact factor calculation"""
        # Act
        result = self.aggregator.get_average_impact_factor(journal_grade='SCIE')

        # Assert
        expected = Decimal('9.55')  # (10.60 + 8.50) / 2
        self.assertEqual(result, expected)

    def test_get_average_impact_factor_with_nulls(self):
        """Test average impact factor ignoring null values"""
        # Act
        result = self.aggregator.get_average_impact_factor()  # All grades

        # Assert
        # Should only average non-null values: (10.60 + 8.50) / 2
        expected = Decimal('9.55')
        self.assertEqual(result, expected)

    def test_get_publications_by_first_author(self):
        """Test publication count by first author"""
        # Act
        result = self.aggregator.get_publications_by_first_author(limit=2)

        # Assert
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)
        # Each item should have author and count
        if result:
            self.assertIn('first_author', result[0])
            self.assertIn('count', result[0])


class ResearchBudgetAggregatorTest(TestCase):
    """Test ResearchBudgetAggregator class"""

    def setUp(self):
        """Set up test data"""
        # Create research projects
        self.project1 = ResearchProject.objects.create(
            project_number='NRF-2023-001',
            project_name='AI 연구',
            principal_investigator='김교수',
            department='컴퓨터공학과',
            funding_agency='한국연구재단',
            total_budget=100000000  # 1억
        )
        self.project2 = ResearchProject.objects.create(
            project_number='NRF-2023-002',
            project_name='IoT 연구',
            principal_investigator='이교수',
            department='전자공학과',
            funding_agency='한국연구재단',
            total_budget=50000000  # 5천만
        )

        # Create execution records
        ExecutionRecord.objects.create(
            execution_id='E-001',
            project=self.project1,
            execution_date=date(2023, 6, 15),
            expense_category='인건비',
            amount=30000000,
            status='집행완료'
        )
        ExecutionRecord.objects.create(
            execution_id='E-002',
            project=self.project1,
            execution_date=date(2023, 7, 20),
            expense_category='재료비',
            amount=20000000,
            status='집행완료'
        )
        ExecutionRecord.objects.create(
            execution_id='E-003',
            project=self.project2,
            execution_date=date(2023, 8, 10),
            expense_category='인건비',
            amount=25000000,
            status='집행완료'
        )

        self.aggregator = ResearchBudgetAggregator()

    def test_aggregator_exists(self):
        """Test that ResearchBudgetAggregator can be instantiated"""
        self.assertIsNotNone(self.aggregator)

    def test_get_total_budget_and_execution(self):
        """Test total budget and execution calculation"""
        # Act
        result = self.aggregator.get_total_budget_and_execution()

        # Assert
        self.assertIn('total_budget', result)
        self.assertIn('total_executed', result)
        self.assertIn('execution_rate', result)

        self.assertEqual(result['total_budget'], 150000000)  # 1억 + 5천만
        self.assertEqual(result['total_executed'], 75000000)  # 3천 + 2천 + 2.5천
        self.assertEqual(result['execution_rate'], Decimal('50.00'))  # 75/150 * 100

    def test_get_budget_by_department(self):
        """Test budget aggregation by department"""
        # Act
        result = self.aggregator.get_budget_by_department()

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Find computer science dept
        cs_dept = next(d for d in result if d['department'] == '컴퓨터공학과')
        self.assertEqual(cs_dept['total_budget'], 100000000)
        self.assertEqual(cs_dept['total_executed'], 50000000)

    def test_get_execution_by_category(self):
        """Test execution amount by category"""
        # Act
        result = self.aggregator.get_execution_by_category()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['인건비'], 55000000)  # 3천 + 2.5천
        self.assertEqual(result['재료비'], 20000000)

    def test_get_execution_rate_by_project(self):
        """Test execution rate calculation by project"""
        # Act
        result = self.aggregator.get_execution_rate_by_project()

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Find project 1
        proj1 = next(p for p in result if p['project_number'] == 'NRF-2023-001')
        self.assertEqual(proj1['total_budget'], 100000000)
        self.assertEqual(proj1['total_executed'], 50000000)
        self.assertEqual(proj1['execution_rate'], Decimal('50.00'))


class StudentAggregatorTest(TestCase):
    """Test StudentAggregator class"""

    def setUp(self):
        """Set up test data"""
        Student.objects.create(
            student_number='2023001',
            name='김학생',
            college='공과대학',
            department='컴퓨터공학과',
            grade=3,
            program_type='학사',
            enrollment_status='재학',
            gender='남',
            admission_year=2023
        )
        Student.objects.create(
            student_number='2023002',
            name='이학생',
            college='공과대학',
            department='컴퓨터공학과',
            grade=2,
            program_type='학사',
            enrollment_status='재학',
            gender='여',
            admission_year=2024
        )
        Student.objects.create(
            student_number='2023003',
            name='박학생',
            college='공과대학',
            department='컴퓨터공학과',
            grade=4,
            program_type='학사',
            enrollment_status='휴학',
            gender='남',
            admission_year=2022
        )
        Student.objects.create(
            student_number='2023004',
            name='최학생',
            college='공과대학',
            department='전자공학과',
            grade=0,
            program_type='석사',
            enrollment_status='재학',
            gender='여',
            admission_year=2024
        )

        self.aggregator = StudentAggregator()

    def test_aggregator_exists(self):
        """Test that StudentAggregator can be instantiated"""
        self.assertIsNotNone(self.aggregator)

    def test_get_total_students_and_enrollment_rate(self):
        """Test total student count and enrollment rate"""
        # Act
        result = self.aggregator.get_total_students_and_enrollment_rate()

        # Assert
        self.assertIn('total_students', result)
        self.assertIn('enrolled_students', result)
        self.assertIn('enrollment_rate', result)

        self.assertEqual(result['total_students'], 4)
        self.assertEqual(result['enrolled_students'], 3)
        self.assertEqual(result['enrollment_rate'], Decimal('75.00'))  # 3/4 * 100

    def test_get_total_students_by_department(self):
        """Test student count filtered by department"""
        # Act
        result = self.aggregator.get_total_students_and_enrollment_rate(
            department='컴퓨터공학과'
        )

        # Assert
        self.assertEqual(result['total_students'], 3)
        self.assertEqual(result['enrolled_students'], 2)

    def test_get_students_by_grade(self):
        """Test student distribution by grade"""
        # Act
        result = self.aggregator.get_students_by_grade()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result[2], 1)
        self.assertEqual(result[3], 1)
        self.assertEqual(result[4], 1)
        self.assertEqual(result[0], 1)  # Graduate student

    def test_get_students_by_department(self):
        """Test student count by department"""
        # Act
        result = self.aggregator.get_students_by_department()

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        # Find CS dept
        cs_dept = next(d for d in result if d['department'] == '컴퓨터공학과')
        self.assertEqual(cs_dept['total_students'], 3)

    def test_get_students_by_admission_year(self):
        """Test student count by admission year"""
        # Arrange
        years = [2023, 2024]

        # Act
        result = self.aggregator.get_students_by_admission_year(years=years)

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result[2023], 1)
        self.assertEqual(result[2024], 2)

    def test_get_students_by_program_type(self):
        """Test student distribution by program type"""
        # Act
        result = self.aggregator.get_students_by_program_type()

        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['학사'], 3)
        self.assertEqual(result['석사'], 1)
