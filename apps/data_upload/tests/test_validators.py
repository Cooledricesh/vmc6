"""
Tests for data validation functions.

Tests validator functions that check:
- Required columns presence
- Data types correctness
- Value ranges
- Data-type specific validation (KPI, Publication, Research Budget, Student)
"""
import pandas as pd
from django.test import TestCase
from decimal import Decimal

from apps.data_upload.validators import (
    validate_required_columns,
    validate_data_types,
    validate_value_ranges,
    validate_department_kpi_data,
    validate_publication_data,
    validate_research_budget_data,
    validate_student_data,
)
from apps.data_upload.exceptions import (
    MissingColumnError,
    DataTypeError,
    ValueRangeError,
)


class ValidateRequiredColumnsTest(TestCase):
    """Test validate_required_columns function."""

    def test_all_required_columns_present(self):
        """Should pass when all required columns are present."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과']
        })
        required = ['평가년도', '단과대학', '학과']

        # Should not raise exception
        try:
            validate_required_columns(df, required)
        except MissingColumnError:
            self.fail("validate_required_columns raised MissingColumnError unexpectedly")

    def test_missing_single_column(self):
        """Should raise MissingColumnError when one column is missing."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학']
        })
        required = ['평가년도', '단과대학', '학과']

        with self.assertRaises(MissingColumnError) as context:
            validate_required_columns(df, required)

        self.assertIn('학과', str(context.exception))

    def test_missing_multiple_columns(self):
        """Should raise MissingColumnError listing all missing columns."""
        df = pd.DataFrame({
            '평가년도': [2023]
        })
        required = ['평가년도', '단과대학', '학과']

        with self.assertRaises(MissingColumnError) as context:
            validate_required_columns(df, required)

        error_message = str(context.exception)
        self.assertIn('단과대학', error_message)
        self.assertIn('학과', error_message)

    def test_empty_dataframe(self):
        """Should raise MissingColumnError for empty DataFrame."""
        df = pd.DataFrame()
        required = ['평가년도', '단과대학']

        with self.assertRaises(MissingColumnError):
            validate_required_columns(df, required)

    def test_extra_columns_allowed(self):
        """Should pass when DataFrame has extra columns beyond required."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '추가컬럼': ['추가데이터']
        })
        required = ['평가년도', '단과대학', '학과']

        try:
            validate_required_columns(df, required)
        except MissingColumnError:
            self.fail("validate_required_columns raised MissingColumnError with extra columns")


class ValidateDataTypesTest(TestCase):
    """Test validate_data_types function."""

    def test_valid_integer_column(self):
        """Should pass when integer column has valid integers."""
        df = pd.DataFrame({
            '평가년도': [2023, 2024, 2025]
        })
        type_map = {'평가년도': 'int'}

        try:
            validate_data_types(df, type_map)
        except DataTypeError:
            self.fail("validate_data_types raised DataTypeError unexpectedly")

    def test_valid_string_column(self):
        """Should pass when string column has valid strings."""
        df = pd.DataFrame({
            '학과': ['컴퓨터공학과', '기계공학과', '전기공학과']
        })
        type_map = {'학과': 'str'}

        try:
            validate_data_types(df, type_map)
        except DataTypeError:
            self.fail("validate_data_types raised DataTypeError unexpectedly")

    def test_valid_decimal_column(self):
        """Should pass when decimal column has valid numeric values."""
        df = pd.DataFrame({
            '취업률': [85.5, 90.0, 78.3]
        })
        type_map = {'취업률': 'decimal'}

        try:
            validate_data_types(df, type_map)
        except DataTypeError:
            self.fail("validate_data_types raised DataTypeError unexpectedly")

    def test_invalid_integer_column(self):
        """Should raise DataTypeError when integer column has non-numeric values."""
        df = pd.DataFrame({
            '평가년도': ['2023', 'invalid', 2025]
        })
        type_map = {'평가년도': 'int'}

        with self.assertRaises(DataTypeError) as context:
            validate_data_types(df, type_map)

        self.assertIn('평가년도', str(context.exception))

    def test_invalid_decimal_column(self):
        """Should raise DataTypeError when decimal column has non-numeric values."""
        df = pd.DataFrame({
            '취업률': [85.5, 'not a number', 78.3]
        })
        type_map = {'취업률': 'decimal'}

        with self.assertRaises(DataTypeError) as context:
            validate_data_types(df, type_map)

        self.assertIn('취업률', str(context.exception))

    def test_multiple_column_types(self):
        """Should validate multiple columns with different types."""
        df = pd.DataFrame({
            '평가년도': [2023, 2024],
            '학과': ['컴퓨터공학과', '기계공학과'],
            '취업률': [85.5, 90.0]
        })
        type_map = {
            '평가년도': 'int',
            '학과': 'str',
            '취업률': 'decimal'
        }

        try:
            validate_data_types(df, type_map)
        except DataTypeError:
            self.fail("validate_data_types raised DataTypeError unexpectedly")


class ValidateValueRangesTest(TestCase):
    """Test validate_value_ranges function."""

    def test_valid_range_integer(self):
        """Should pass when integer values are within range."""
        df = pd.DataFrame({
            '평가년도': [2020, 2023, 2025]
        })
        range_map = {'평가년도': (2000, 2100)}

        try:
            validate_value_ranges(df, range_map)
        except ValueRangeError:
            self.fail("validate_value_ranges raised ValueRangeError unexpectedly")

    def test_valid_range_decimal(self):
        """Should pass when decimal values are within range."""
        df = pd.DataFrame({
            '취업률': [0.0, 50.5, 100.0]
        })
        range_map = {'취업률': (0, 100)}

        try:
            validate_value_ranges(df, range_map)
        except ValueRangeError:
            self.fail("validate_value_ranges raised ValueRangeError unexpectedly")

    def test_value_below_minimum(self):
        """Should raise ValueRangeError when value is below minimum."""
        df = pd.DataFrame({
            '평가년도': [1999, 2023, 2025]
        })
        range_map = {'평가년도': (2000, 2100)}

        with self.assertRaises(ValueRangeError) as context:
            validate_value_ranges(df, range_map)

        error_message = str(context.exception)
        self.assertIn('평가년도', error_message)
        self.assertIn('1999', error_message)

    def test_value_above_maximum(self):
        """Should raise ValueRangeError when value is above maximum."""
        df = pd.DataFrame({
            '취업률': [50.0, 75.5, 101.0]
        })
        range_map = {'취업률': (0, 100)}

        with self.assertRaises(ValueRangeError) as context:
            validate_value_ranges(df, range_map)

        error_message = str(context.exception)
        self.assertIn('취업률', error_message)
        self.assertIn('101', error_message)

    def test_null_values_ignored(self):
        """Should skip validation for null/NaN values."""
        df = pd.DataFrame({
            '취업률': [50.0, None, 75.5, pd.NA]
        })
        range_map = {'취업률': (0, 100)}

        try:
            validate_value_ranges(df, range_map)
        except ValueRangeError:
            self.fail("validate_value_ranges should ignore null values")

    def test_multiple_columns_with_ranges(self):
        """Should validate multiple columns with different ranges."""
        df = pd.DataFrame({
            '평가년도': [2020, 2023],
            '취업률': [75.5, 90.0]
        })
        range_map = {
            '평가년도': (2000, 2100),
            '취업률': (0, 100)
        }

        try:
            validate_value_ranges(df, range_map)
        except ValueRangeError:
            self.fail("validate_value_ranges raised ValueRangeError unexpectedly")


class ValidateDepartmentKPIDataTest(TestCase):
    """Test validate_department_kpi_data function."""

    def test_valid_kpi_data(self):
        """Should pass with valid Department KPI data."""
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

        try:
            validate_department_kpi_data(df)
        except Exception as e:
            self.fail(f"validate_department_kpi_data raised {type(e).__name__} unexpectedly: {e}")

    def test_missing_required_columns(self):
        """Should raise MissingColumnError when required columns are missing."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학']
            # Missing '학과'
        })

        with self.assertRaises(MissingColumnError):
            validate_department_kpi_data(df)

    def test_invalid_evaluation_year(self):
        """Should raise ValueRangeError for invalid evaluation year."""
        df = pd.DataFrame({
            '평가년도': [1999],  # Below 2000
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [85.5],
            '전임교원 수 (명)': [15],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [10.5],
            '국제학술대회 개최 횟수': [2]
        })

        with self.assertRaises(ValueRangeError):
            validate_department_kpi_data(df)

    def test_invalid_employment_rate(self):
        """Should raise ValueRangeError for employment rate > 100%."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [105.0],  # Over 100%
            '전임교원 수 (명)': [15],
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [10.5],
            '국제학술대회 개최 횟수': [2]
        })

        with self.assertRaises(ValueRangeError):
            validate_department_kpi_data(df)

    def test_negative_faculty_count(self):
        """Should raise ValueRangeError for negative faculty count."""
        df = pd.DataFrame({
            '평가년도': [2023],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '졸업생 취업률 (%)': [85.5],
            '전임교원 수 (명)': [-1],  # Negative
            '초빙교원 수 (명)': [5],
            '연간 기술이전 수입액 (억원)': [10.5],
            '국제학술대회 개최 횟수': [2]
        })

        with self.assertRaises(ValueRangeError):
            validate_department_kpi_data(df)


class ValidatePublicationDataTest(TestCase):
    """Test validate_publication_data function."""

    def test_valid_publication_data(self):
        """Should pass with valid publication data."""
        df = pd.DataFrame({
            '논문ID': ['PUB-23-001'],
            '게재일': ['2023-06-15'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '논문제목': ['AI Research'],
            '주저자': ['홍길동'],
            '참여저자': ['김철수;이영희'],
            '학술지명': ['Journal of AI'],
            '저널등급': ['SCIE'],
            'Impact Factor': [3.5],
            '과제연계여부': ['Y']
        })

        try:
            validate_publication_data(df)
        except Exception as e:
            self.fail(f"validate_publication_data raised {type(e).__name__} unexpectedly: {e}")

    def test_missing_required_columns(self):
        """Should raise MissingColumnError when required columns are missing."""
        df = pd.DataFrame({
            '논문ID': ['PUB-23-001'],
            '게재일': ['2023-06-15']
            # Missing other required columns
        })

        with self.assertRaises(MissingColumnError):
            validate_publication_data(df)

    def test_invalid_journal_grade(self):
        """Should raise ValueRangeError for invalid journal grade."""
        df = pd.DataFrame({
            '논문ID': ['PUB-23-001'],
            '게재일': ['2023-06-15'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '논문제목': ['AI Research'],
            '주저자': ['홍길동'],
            '참여저자': ['김철수;이영희'],
            '학술지명': ['Journal of AI'],
            '저널등급': ['INVALID'],  # Not in allowed list
            'Impact Factor': [3.5],
            '과제연계여부': ['Y']
        })

        with self.assertRaises(ValueRangeError):
            validate_publication_data(df)

    def test_invalid_project_linked(self):
        """Should raise ValueRangeError for invalid project_linked value."""
        df = pd.DataFrame({
            '논문ID': ['PUB-23-001'],
            '게재일': ['2023-06-15'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '논문제목': ['AI Research'],
            '주저자': ['홍길동'],
            '참여저자': ['김철수;이영희'],
            '학술지명': ['Journal of AI'],
            '저널등급': ['SCIE'],
            'Impact Factor': [3.5],
            '과제연계여부': ['MAYBE']  # Should be Y or N
        })

        with self.assertRaises(ValueRangeError):
            validate_publication_data(df)


class ValidateResearchBudgetDataTest(TestCase):
    """Test validate_research_budget_data function."""

    def test_valid_research_budget_data(self):
        """Should pass with valid research budget data."""
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

        try:
            validate_research_budget_data(df)
        except Exception as e:
            self.fail(f"validate_research_budget_data raised {type(e).__name__} unexpectedly: {e}")

    def test_missing_required_columns(self):
        """Should raise MissingColumnError when required columns are missing."""
        df = pd.DataFrame({
            '집행ID': ['T2301001'],
            '과제번호': ['NRF-2023-015']
            # Missing other required columns
        })

        with self.assertRaises(MissingColumnError):
            validate_research_budget_data(df)

    def test_invalid_status(self):
        """Should raise ValueRangeError for invalid status value."""
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
            '상태': ['INVALID'],  # Should be 집행완료 or 처리중
            '비고': ['정상집행']
        })

        with self.assertRaises(ValueRangeError):
            validate_research_budget_data(df)

    def test_negative_budget(self):
        """Should raise ValueRangeError for negative budget amounts."""
        df = pd.DataFrame({
            '집행ID': ['T2301001'],
            '과제번호': ['NRF-2023-015'],
            '과제명': ['AI 연구'],
            '연구책임자': ['홍길동'],
            '소속학과': ['컴퓨터공학과'],
            '지원기관': ['한국연구재단'],
            '총연구비': [-100000000],  # Negative
            '집행일자': ['2023-06-15'],
            '집행항목': ['인건비'],
            '집행금액': [5000000],
            '상태': ['집행완료'],
            '비고': ['정상집행']
        })

        with self.assertRaises(ValueRangeError):
            validate_research_budget_data(df)


class ValidateStudentDataTest(TestCase):
    """Test validate_student_data function."""

    def test_valid_student_data(self):
        """Should pass with valid student data."""
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

        try:
            validate_student_data(df)
        except Exception as e:
            self.fail(f"validate_student_data raised {type(e).__name__} unexpectedly: {e}")

    def test_missing_required_columns(self):
        """Should raise MissingColumnError when required columns are missing."""
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동']
            # Missing other required columns
        })

        with self.assertRaises(MissingColumnError):
            validate_student_data(df)

    def test_invalid_grade(self):
        """Should raise ValueRangeError for invalid grade (must be 0-4)."""
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '학년': [5],  # Invalid: should be 0-4
            '과정구분': ['학사'],
            '학적상태': ['재학'],
            '성별': ['남'],
            '입학년도': [2023]
        })

        with self.assertRaises(ValueRangeError):
            validate_student_data(df)

    def test_invalid_program_type(self):
        """Should raise ValueRangeError for invalid program type."""
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '학년': [3],
            '과정구분': ['INVALID'],  # Should be 학사, 석사, 박사
            '학적상태': ['재학'],
            '성별': ['남'],
            '입학년도': [2023]
        })

        with self.assertRaises(ValueRangeError):
            validate_student_data(df)

    def test_invalid_enrollment_status(self):
        """Should raise ValueRangeError for invalid enrollment status."""
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '학년': [3],
            '과정구분': ['학사'],
            '학적상태': ['INVALID'],  # Should be 재학, 휴학, 졸업
            '성별': ['남'],
            '입학년도': [2023]
        })

        with self.assertRaises(ValueRangeError):
            validate_student_data(df)

    def test_invalid_gender(self):
        """Should raise ValueRangeError for invalid gender."""
        df = pd.DataFrame({
            '학번': ['20231234'],
            '이름': ['홍길동'],
            '단과대학': ['공과대학'],
            '학과': ['컴퓨터공학과'],
            '학년': [3],
            '과정구분': ['학사'],
            '학적상태': ['재학'],
            '성별': ['INVALID'],  # Should be 남 or 여
            '입학년도': [2023]
        })

        with self.assertRaises(ValueRangeError):
            validate_student_data(df)
