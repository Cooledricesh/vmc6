"""
RED Phase: Tests for analytics models.

This module tests all analytics data models that map to Supabase tables.
All models use managed=False since Supabase manages the schema.

Test strategy:
- Test model field definitions
- Test model meta options
- Test model methods
- Test database table mapping
"""
from django.test import TestCase
from django.db import connection
from django.utils import timezone
from datetime import date, datetime
from decimal import Decimal

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student,
    UploadHistory
)
from apps.authentication.models import User


class DepartmentKPIModelTest(TestCase):
    """Test DepartmentKPI model"""

    def test_model_exists(self):
        """Test that DepartmentKPI model can be imported"""
        # This will fail until we create the model
        self.assertIsNotNone(DepartmentKPI)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(DepartmentKPI._meta.db_table, 'department_kpi')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(DepartmentKPI._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in DepartmentKPI._meta.get_fields()]

        required_fields = [
            'id', 'evaluation_year', 'college', 'department',
            'employment_rate', 'full_time_faculty', 'visiting_faculty',
            'tech_transfer_income', 'intl_conference_count', 'created_at'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_create_department_kpi(self):
        """Test creating a DepartmentKPI instance"""
        kpi = DepartmentKPI(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=Decimal('88.50'),
            full_time_faculty=17,
            visiting_faculty=5,
            tech_transfer_income=Decimal('13.50'),
            intl_conference_count=4
        )

        self.assertEqual(kpi.evaluation_year, 2025)
        self.assertEqual(kpi.college, '공과대학')
        self.assertEqual(kpi.department, '컴퓨터공학과')
        self.assertEqual(kpi.employment_rate, Decimal('88.50'))

    def test_string_representation(self):
        """Test __str__ method"""
        kpi = DepartmentKPI(
            evaluation_year=2025,
            college='공과대학',
            department='컴퓨터공학과',
            employment_rate=Decimal('88.50')
        )

        expected = '2025 - 공과대학 컴퓨터공학과'
        self.assertEqual(str(kpi), expected)


class PublicationModelTest(TestCase):
    """Test Publication model"""

    def test_model_exists(self):
        """Test that Publication model can be imported"""
        self.assertIsNotNone(Publication)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(Publication._meta.db_table, 'publications')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(Publication._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in Publication._meta.get_fields()]

        required_fields = [
            'id', 'publication_id', 'publication_date', 'college', 'department',
            'title', 'first_author', 'co_authors', 'journal_name',
            'journal_grade', 'impact_factor', 'project_linked', 'created_at'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_create_publication(self):
        """Test creating a Publication instance"""
        pub = Publication(
            publication_id='PUB-25-001',
            publication_date=date(2025, 6, 15),
            college='공과대학',
            department='컴퓨터공학과',
            title='Federated Learning for Privacy-Preserving AI',
            first_author='이서연',
            co_authors='정현우',
            journal_name='IEEE Internet of Things Journal',
            journal_grade='SCIE',
            impact_factor=Decimal('10.60'),
            project_linked='Y'
        )

        self.assertEqual(pub.publication_id, 'PUB-25-001')
        self.assertEqual(pub.journal_grade, 'SCIE')
        self.assertEqual(pub.project_linked, 'Y')

    def test_string_representation(self):
        """Test __str__ method"""
        pub = Publication(
            publication_id='PUB-25-001',
            title='Federated Learning for Privacy-Preserving AI'
        )

        expected = 'PUB-25-001 - Federated Learning for Privacy-Preserving AI'
        self.assertEqual(str(pub), expected)


class ResearchProjectModelTest(TestCase):
    """Test ResearchProject model"""

    def test_model_exists(self):
        """Test that ResearchProject model can be imported"""
        self.assertIsNotNone(ResearchProject)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(ResearchProject._meta.db_table, 'research_projects')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(ResearchProject._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in ResearchProject._meta.get_fields()]

        required_fields = [
            'id', 'project_number', 'project_name', 'principal_investigator',
            'department', 'funding_agency', 'total_budget',
            'created_at', 'updated_at'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_create_research_project(self):
        """Test creating a ResearchProject instance"""
        project = ResearchProject(
            project_number='NRF-2023-015',
            project_name='AI 연구 과제',
            principal_investigator='김교수',
            department='컴퓨터공학과',
            funding_agency='한국연구재단',
            total_budget=50000000
        )

        self.assertEqual(project.project_number, 'NRF-2023-015')
        self.assertEqual(project.total_budget, 50000000)

    def test_string_representation(self):
        """Test __str__ method"""
        project = ResearchProject(
            project_number='NRF-2023-015',
            project_name='AI 연구 과제'
        )

        expected = 'NRF-2023-015 - AI 연구 과제'
        self.assertEqual(str(project), expected)


class ExecutionRecordModelTest(TestCase):
    """Test ExecutionRecord model"""

    def test_model_exists(self):
        """Test that ExecutionRecord model can be imported"""
        self.assertIsNotNone(ExecutionRecord)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(ExecutionRecord._meta.db_table, 'execution_records')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(ExecutionRecord._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in ExecutionRecord._meta.get_fields()]

        required_fields = [
            'id', 'execution_id', 'project', 'execution_date',
            'expense_category', 'amount', 'status', 'description', 'created_at'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_has_foreign_key_to_research_project(self):
        """Test that ExecutionRecord has FK to ResearchProject"""
        field = ExecutionRecord._meta.get_field('project')
        self.assertEqual(field.related_model, ResearchProject)

    def test_create_execution_record(self):
        """Test creating an ExecutionRecord instance"""
        record = ExecutionRecord(
            execution_id='T2301001',
            execution_date=date(2023, 6, 15),
            expense_category='인건비',
            amount=5000000,
            status='집행완료',
            description='연구원 급여'
        )

        self.assertEqual(record.execution_id, 'T2301001')
        self.assertEqual(record.amount, 5000000)
        self.assertEqual(record.status, '집행완료')

    def test_string_representation(self):
        """Test __str__ method"""
        record = ExecutionRecord(
            execution_id='T2301001',
            expense_category='인건비',
            amount=5000000
        )

        expected = 'T2301001 - 인건비: 5000000원'
        self.assertEqual(str(record), expected)


class StudentModelTest(TestCase):
    """Test Student model"""

    def test_model_exists(self):
        """Test that Student model can be imported"""
        self.assertIsNotNone(Student)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(Student._meta.db_table, 'students')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(Student._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in Student._meta.get_fields()]

        required_fields = [
            'id', 'student_number', 'name', 'college', 'department',
            'grade', 'program_type', 'enrollment_status', 'gender',
            'admission_year', 'advisor', 'email', 'created_at', 'updated_at'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_create_student(self):
        """Test creating a Student instance"""
        student = Student(
            student_number='20192101',
            name='정현우',
            college='공과대학',
            department='컴퓨터공학과',
            grade=0,
            program_type='석사',
            enrollment_status='재학',
            gender='남',
            admission_year=2024,
            advisor='이서연',
            email='hwjung@university.ac.kr'
        )

        self.assertEqual(student.student_number, '20192101')
        self.assertEqual(student.name, '정현우')
        self.assertEqual(student.program_type, '석사')

    def test_string_representation(self):
        """Test __str__ method"""
        student = Student(
            student_number='20192101',
            name='정현우',
            department='컴퓨터공학과'
        )

        expected = '20192101 - 정현우 (컴퓨터공학과)'
        self.assertEqual(str(student), expected)


class UploadHistoryModelTest(TestCase):
    """Test UploadHistory model"""

    def test_model_exists(self):
        """Test that UploadHistory model can be imported"""
        self.assertIsNotNone(UploadHistory)

    def test_model_has_correct_table_name(self):
        """Test that model maps to correct database table"""
        self.assertEqual(UploadHistory._meta.db_table, 'upload_history')

    def test_model_is_unmanaged(self):
        """Test that model is not managed by Django"""
        self.assertFalse(UploadHistory._meta.managed)

    def test_model_fields_exist(self):
        """Test that all required fields exist"""
        field_names = [f.name for f in UploadHistory._meta.get_fields()]

        required_fields = [
            'id', 'user', 'file_name', 'file_size', 'data_type',
            'upload_date', 'status', 'rows_processed', 'error_message'
        ]

        for field in required_fields:
            self.assertIn(field, field_names)

    def test_has_foreign_key_to_user(self):
        """Test that UploadHistory has FK to User"""
        field = UploadHistory._meta.get_field('user')
        self.assertEqual(field.related_model, User)

    def test_create_upload_history(self):
        """Test creating an UploadHistory instance"""
        upload = UploadHistory(
            file_name='department_kpi.csv',
            file_size=102400,
            data_type='department_kpi',
            status='success',
            rows_processed=50
        )

        self.assertEqual(upload.file_name, 'department_kpi.csv')
        self.assertEqual(upload.data_type, 'department_kpi')
        self.assertEqual(upload.status, 'success')

    def test_string_representation(self):
        """Test __str__ method"""
        upload = UploadHistory(
            file_name='department_kpi.csv',
            data_type='department_kpi',
            status='success'
        )

        expected = 'department_kpi.csv - department_kpi (success)'
        self.assertEqual(str(upload), expected)
