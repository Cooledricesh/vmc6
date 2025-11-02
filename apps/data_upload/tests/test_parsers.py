"""
Tests for data parser classes.

Tests parser functionality:
- BaseParser: File reading, validation, cleaning
- DepartmentKPIParser: KPI data parsing and database insertion
- PublicationParser: Publication data parsing
- ResearchBudgetParser: Research budget parsing (complex, splits into 2 models)
- StudentParser: Student data parsing
"""
import os
import io
import tempfile
import pandas as pd
from typing import Dict, Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student,
    UploadHistory,
)
from apps.data_upload.parsers import (
    BaseParser,
    DepartmentKPIParser,
    PublicationParser,
    ResearchBudgetParser,
    StudentParser,
)
from apps.data_upload.exceptions import (
    FileFormatError,
    FileSizeError,
    ValidationError,
)

User = get_user_model()


class ConcreteParser(BaseParser):
    """Concrete implementation of BaseParser for testing."""
    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """Minimal parse implementation for testing."""
        return {'success': True, 'rows_processed': 0, 'error_message': None}


class BaseParserTest(TestCase):
    """Test BaseParser abstract class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.parser = ConcreteParser()

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_validate_extension_xlsx(self):
        """Should accept .xlsx files."""
        filepath = os.path.join(self.test_dir, 'test.xlsx')

        try:
            self.parser.validate_extension(filepath)
        except FileFormatError:
            self.fail("validate_extension raised FileFormatError for .xlsx file")

    def test_validate_extension_xls(self):
        """Should accept .xls files."""
        filepath = os.path.join(self.test_dir, 'test.xls')

        try:
            self.parser.validate_extension(filepath)
        except FileFormatError:
            self.fail("validate_extension raised FileFormatError for .xls file")

    def test_validate_extension_csv(self):
        """Should accept .csv files."""
        filepath = os.path.join(self.test_dir, 'test.csv')

        try:
            self.parser.validate_extension(filepath)
        except FileFormatError:
            self.fail("validate_extension raised FileFormatError for .csv file")

    def test_validate_extension_invalid(self):
        """Should reject invalid file extensions."""
        filepath = os.path.join(self.test_dir, 'test.txt')

        with self.assertRaises(FileFormatError) as context:
            self.parser.validate_extension(filepath)

        self.assertIn('.txt', str(context.exception))

    def test_validate_size_within_limit(self):
        """Should accept files under 50MB."""
        size_bytes = 10 * 1024 * 1024  # 10 MB

        try:
            self.parser.validate_size(size_bytes)
        except FileSizeError:
            self.fail("validate_size raised FileSizeError for file under limit")

    def test_validate_size_at_limit(self):
        """Should accept files exactly at 50MB limit."""
        size_bytes = 50 * 1024 * 1024  # 50 MB exactly

        try:
            self.parser.validate_size(size_bytes)
        except FileSizeError:
            self.fail("validate_size raised FileSizeError for file at limit")

    def test_validate_size_over_limit(self):
        """Should reject files over 50MB."""
        size_bytes = 51 * 1024 * 1024  # 51 MB

        with self.assertRaises(FileSizeError) as context:
            self.parser.validate_size(size_bytes)

        self.assertIn('50MB', str(context.exception))

    def test_clean_data_strips_whitespace(self):
        """Should strip leading/trailing whitespace from strings."""
        df = pd.DataFrame({
            '학과': ['  컴퓨터공학과  ', '기계공학과  ', '  전기공학과']
        })

        cleaned_df = self.parser.clean_data(df)

        self.assertEqual(cleaned_df['학과'].iloc[0], '컴퓨터공학과')
        self.assertEqual(cleaned_df['학과'].iloc[1], '기계공학과')
        self.assertEqual(cleaned_df['학과'].iloc[2], '전기공학과')

    def test_clean_data_handles_nan(self):
        """Should preserve NaN values properly."""
        df = pd.DataFrame({
            '학과': ['컴퓨터공학과', None, '전기공학과'],
            '취업률': [85.5, None, 90.0]
        })

        cleaned_df = self.parser.clean_data(df)

        self.assertEqual(cleaned_df['학과'].iloc[0], '컴퓨터공학과')
        self.assertTrue(pd.isna(cleaned_df['학과'].iloc[1]))
        self.assertTrue(pd.isna(cleaned_df['취업률'].iloc[1]))

    def test_clean_data_preserves_numeric_types(self):
        """Should not modify numeric columns."""
        df = pd.DataFrame({
            '평가년도': [2023, 2024, 2025],
            '취업률': [85.5, 90.0, 78.3]
        })

        cleaned_df = self.parser.clean_data(df)

        self.assertEqual(cleaned_df['평가년도'].iloc[0], 2023)
        self.assertEqual(cleaned_df['취업률'].iloc[0], 85.5)

    def test_read_file_csv(self):
        """Should read CSV files correctly."""
        csv_path = os.path.join(self.test_dir, 'test.csv')

        # Create test CSV
        df = pd.DataFrame({
            '학과': ['컴퓨터공학과', '기계공학과'],
            '평가년도': [2023, 2024]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # Read it back
        result_df = self.parser.read_file(csv_path)

        self.assertEqual(len(result_df), 2)
        self.assertIn('학과', result_df.columns)
        self.assertEqual(result_df['학과'].iloc[0], '컴퓨터공학과')

    def test_read_file_xlsx(self):
        """Should read Excel (.xlsx) files correctly."""
        xlsx_path = os.path.join(self.test_dir, 'test.xlsx')

        # Create test Excel file
        df = pd.DataFrame({
            '학과': ['컴퓨터공학과', '기계공학과'],
            '평가년도': [2023, 2024]
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Read it back
        result_df = self.parser.read_file(xlsx_path)

        self.assertEqual(len(result_df), 2)
        self.assertIn('학과', result_df.columns)

    def test_read_file_nonexistent(self):
        """Should raise FileFormatError for nonexistent files."""
        filepath = os.path.join(self.test_dir, 'nonexistent.xlsx')

        with self.assertRaises(FileFormatError):
            self.parser.read_file(filepath)


class DepartmentKPIParserTest(TestCase):
    """Test DepartmentKPIParser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            department='전체'
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_valid_kpi_file(self):
        """Should successfully parse valid KPI Excel file."""
        parser = DepartmentKPIParser()
        xlsx_path = os.path.join(self.test_dir, 'kpi.xlsx')

        # Create test data
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [85.5],
            '전임교원 수 (명)': [15],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [10.5],
            '국제학술대회 개최 횟수': [2]
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['rows_processed'], 1)
        self.assertIsNone(result['error_message'])

        # Check database
        kpi = DepartmentKPI.objects.first()
        self.assertIsNotNone(kpi)
        self.assertEqual(kpi.evaluation_year, 2023)
        self.assertEqual(kpi.department, '컴퓨터공학과')

    def test_parse_invalid_kpi_file_missing_columns(self):
        """Should fail when required columns are missing."""
        parser = DepartmentKPIParser()
        xlsx_path = os.path.join(self.test_dir, 'kpi_invalid.xlsx')

        # Create test data with missing columns
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학']
            # Missing other required columns
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Assertions
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error_message'])
        self.assertIn('Missing required columns', result['error_message'])

    def test_parse_creates_upload_history(self):
        """Should create UploadHistory record."""
        parser = DepartmentKPIParser()
        xlsx_path = os.path.join(self.test_dir, 'kpi.xlsx')

        # Create test data
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [85.5],
            '전임교원 수 (명)': [15],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [10.5],
            '국제학술대회 개최 횟수': [2]
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Check UploadHistory
        history = UploadHistory.objects.first()
        self.assertIsNotNone(history)
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.data_type, 'department_kpi')
        self.assertEqual(history.status, 'success')
        self.assertEqual(history.rows_processed, 1)


class PublicationParserTest(TestCase):
    """Test PublicationParser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            department='전체'
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_valid_publication_file(self):
        """Should successfully parse valid publication Excel file."""
        parser = PublicationParser()
        xlsx_path = os.path.join(self.test_dir, 'publication.xlsx')

        # Create test data
        df = pd.DataFrame({
            '논문ID': ['PUB-23-001'],
            '게재일': ['2023-06-15'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '논문제목': ['AI Research Paper'],
            '주저자': ['홍길동'],
            '참여저자': ['김철수;이영희'],
            '학술지명': ['Journal of AI'],
            '저널등급': ['SCIE'],
            'Impact Factor': [3.5],
            '과제연계여부': ['Y']
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['rows_processed'], 1)

        # Check database
        pub = Publication.objects.first()
        self.assertIsNotNone(pub)
        self.assertEqual(pub.publication_id, 'PUB-23-001')
        self.assertEqual(pub.first_author, '홍길동')


class ResearchBudgetParserTest(TestCase):
    """Test ResearchBudgetParser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            department='전체'
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_creates_project_and_execution(self):
        """Should create both ResearchProject and ExecutionRecord."""
        parser = ResearchBudgetParser()
        xlsx_path = os.path.join(self.test_dir, 'budget.xlsx')

        # Create test data
        df = pd.DataFrame({
            '집행ID': ['T2301001'],
            '과제번호': ['NRF-2023-015'],
            '과제명': ['AI 연구'],
            '연구책임자': ['홍길동'],
            '소속학과': ['컴퓨터공학과'],
            '지원기관': ['한국연구재단'],
            '총연구비': [100000000],
            '집행일자': ['2023-06-15'],
            '집행항목': ['인건비'],
            '집행금액': [5000000],
            '상태': ['집행완료'],
            '비고': ['정상집행']
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Assertions
        self.assertTrue(result['success'])

        # Check ResearchProject created
        project = ResearchProject.objects.first()
        self.assertIsNotNone(project)
        self.assertEqual(project.project_number, 'NRF-2023-015')
        self.assertEqual(project.total_budget, 100000000)

        # Check ExecutionRecord created
        execution = ExecutionRecord.objects.first()
        self.assertIsNotNone(execution)
        self.assertEqual(execution.execution_id, 'T2301001')
        self.assertEqual(execution.amount, 5000000)


class StudentParserTest(TestCase):
    """Test StudentParser functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            department='전체'
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_parse_valid_student_file(self):
        """Should successfully parse valid student Excel file."""
        parser = StudentParser()
        xlsx_path = os.path.join(self.test_dir, 'student.xlsx')

        # Create test data
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '학년': [3],
            '과정구분': ['학사'],
            '학적상태': ['재학'],
            '성별': ['남'],
            '입학년도': [2023]
        })
        df.to_excel(xlsx_path, index=False, engine='openpyxl')

        # Parse
        result = parser.parse(xlsx_path, self.user)

        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['rows_processed'], 1)

        # Check database
        student = Student.objects.first()
        self.assertIsNotNone(student)
        self.assertEqual(student.student_number, '20231234')
        self.assertEqual(student.name, '홍길동')
