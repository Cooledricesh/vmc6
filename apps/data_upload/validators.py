"""
Data validation functions for file uploads.

These validators check data integrity before database insertion:
- Required columns presence
- Data type correctness
- Value ranges
- Data-specific business rules

All validators raise specific exceptions from apps.data_upload.exceptions.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any

from apps.data_upload.exceptions import (
    MissingColumnError,
    DataTypeError,
    ValueRangeError,
)


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    """
    Validate that all required columns are present in DataFrame.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Raises:
        MissingColumnError: If any required columns are missing
    """
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise MissingColumnError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )


def validate_data_types(df: pd.DataFrame, type_map: Dict[str, str]) -> None:
    """
    Validate that columns have correct data types.

    Args:
        df: DataFrame to validate
        type_map: Dict mapping column names to expected types ('int', 'str', 'decimal')

    Raises:
        DataTypeError: If data type validation fails
    """
    for column, expected_type in type_map.items():
        if column not in df.columns:
            continue

        # Skip rows with null values for type checking
        non_null_values = df[column].dropna()

        if len(non_null_values) == 0:
            continue

        try:
            if expected_type == 'int':
                # Check if values can be converted to integers
                pd.to_numeric(non_null_values, errors='raise')
            elif expected_type == 'decimal':
                # Check if values can be converted to floats/decimals
                pd.to_numeric(non_null_values, errors='raise')
            elif expected_type == 'str':
                # Check if values are strings
                non_null_values.astype(str)
        except (ValueError, TypeError) as e:
            raise DataTypeError(
                f"Column '{column}' has invalid data type. Expected {expected_type}."
            )


def validate_value_ranges(df: pd.DataFrame, range_map: Dict[str, Tuple[float, float]]) -> None:
    """
    Validate that numeric values are within acceptable ranges.

    Args:
        df: DataFrame to validate
        range_map: Dict mapping column names to (min, max) tuples

    Raises:
        ValueRangeError: If any values are out of range
    """
    for column, (min_val, max_val) in range_map.items():
        if column not in df.columns:
            continue

        # Skip null values for range checking
        non_null_values = df[column].dropna()

        if len(non_null_values) == 0:
            continue

        # Check for values below minimum
        below_min = non_null_values[non_null_values < min_val]
        if not below_min.empty:
            raise ValueRangeError(
                f"Column '{column}' has values below minimum {min_val}: {below_min.tolist()}"
            )

        # Check for values above maximum
        above_max = non_null_values[non_null_values > max_val]
        if not above_max.empty:
            raise ValueRangeError(
                f"Column '{column}' has values above maximum {max_val}: {above_max.tolist()}"
            )


def validate_department_kpi_data(df: pd.DataFrame) -> None:
    """
    Validate Department KPI data.

    Checks:
    - Required columns present
    - Evaluation year in valid range (2000-2100)
    - Employment rate 0-100%
    - Faculty counts non-negative
    - Tech transfer income non-negative
    - Conference count non-negative

    Args:
        df: DataFrame with Korean column names

    Raises:
        MissingColumnError: If required columns are missing
        ValueRangeError: If values are out of acceptable ranges
    """
    # Required columns
    required_columns = [
        '평가년도',
        '단과대학',
        '학과',
        '졸업생 취업률 (%)',
        '전임교원 수 (명)',
        '초빙교원 수 (명)',
        '연간 기술이전 수입액 (억원)',
        '국제학술대회 개최 횟수'
    ]
    validate_required_columns(df, required_columns)

    # Value range validations
    range_map = {
        '평가년도': (2000, 2100),
        '졸업생 취업률 (%)': (0, 100),
        '전임교원 수 (명)': (0, 1000),
        '초빙교원 수 (명)': (0, 1000),
        '연간 기술이전 수입액 (억원)': (0, float('inf')),
        '국제학술대회 개최 횟수': (0, 1000)
    }
    validate_value_ranges(df, range_map)


def validate_publication_data(df: pd.DataFrame) -> None:
    """
    Validate Publication data.

    Checks:
    - Required columns present
    - Journal grade in allowed values (SCIE, KCI, SCOPUS, KCI후보, 기타)
    - Project linked is Y or N
    - Impact factor non-negative

    Args:
        df: DataFrame with Korean column names

    Raises:
        MissingColumnError: If required columns are missing
        ValueRangeError: If values are invalid
    """
    # Required columns
    required_columns = [
        '논문ID',
        '게재일',
        '단과대학',
        '학과',
        '논문제목',
        '주저자',
        '참여저자',
        '학술지명',
        '저널등급',
        'Impact Factor',
        '과제연계여부'
    ]
    validate_required_columns(df, required_columns)

    # Validate journal grade
    allowed_journal_grades = ['SCIE', 'KCI', 'SCOPUS', 'KCI후보', '기타', 'SSCI']
    if '저널등급' in df.columns:
        non_null_grades = df['저널등급'].dropna()
        invalid_grades = non_null_grades[~non_null_grades.isin(allowed_journal_grades)]
        if not invalid_grades.empty:
            raise ValueRangeError(
                f"Column '저널등급' has invalid values. Allowed: {allowed_journal_grades}. "
                f"Found: {invalid_grades.unique().tolist()}"
            )

    # Validate project linked
    allowed_project_linked = ['Y', 'N']
    if '과제연계여부' in df.columns:
        non_null_linked = df['과제연계여부'].dropna()
        invalid_linked = non_null_linked[~non_null_linked.isin(allowed_project_linked)]
        if not invalid_linked.empty:
            raise ValueRangeError(
                f"Column '과제연계여부' has invalid values. Allowed: {allowed_project_linked}. "
                f"Found: {invalid_linked.unique().tolist()}"
            )

    # Impact factor should be non-negative
    if 'Impact Factor' in df.columns:
        non_null_if = df['Impact Factor'].dropna()
        negative_if = non_null_if[non_null_if < 0]
        if not negative_if.empty:
            raise ValueRangeError(
                f"Column 'Impact Factor' has negative values: {negative_if.tolist()}"
            )


def validate_research_budget_data(df: pd.DataFrame) -> None:
    """
    Validate Research Budget data.

    Checks:
    - Required columns present
    - Total budget and execution amount are non-negative
    - Status is valid (집행완료, 처리중)

    Args:
        df: DataFrame with Korean column names

    Raises:
        MissingColumnError: If required columns are missing
        ValueRangeError: If values are invalid
    """
    # Required columns
    required_columns = [
        '집행ID',
        '과제번호',
        '과제명',
        '연구책임자',
        '소속학과',
        '지원기관',
        '총연구비',
        '집행일자',
        '집행항목',
        '집행금액',
        '상태',
        '비고'
    ]
    validate_required_columns(df, required_columns)

    # Validate status
    allowed_statuses = ['집행완료', '처리중']
    if '상태' in df.columns:
        non_null_status = df['상태'].dropna()
        invalid_status = non_null_status[~non_null_status.isin(allowed_statuses)]
        if not invalid_status.empty:
            raise ValueRangeError(
                f"Column '상태' has invalid values. Allowed: {allowed_statuses}. "
                f"Found: {invalid_status.unique().tolist()}"
            )

    # Budget amounts should be non-negative
    range_map = {
        '총연구비': (0, float('inf')),
        '집행금액': (0, float('inf'))
    }
    validate_value_ranges(df, range_map)


def validate_student_data(df: pd.DataFrame) -> None:
    """
    Validate Student data.

    Checks:
    - Required columns present
    - Grade is 0-4 (0 for graduate students)
    - Program type is valid (학사, 석사, 박사)
    - Enrollment status is valid (재학, 휴학, 졸업)
    - Gender is valid (남, 여)
    - Admission year is reasonable (1900-2100)

    Args:
        df: DataFrame with Korean column names

    Raises:
        MissingColumnError: If required columns are missing
        ValueRangeError: If values are invalid
    """
    # Required columns
    required_columns = [
        '학번',
        '이름',
        '단과대학',
        '학과',
        '학년',
        '과정구분',
        '학적상태',
        '성별',
        '입학년도'
    ]
    validate_required_columns(df, required_columns)

    # Validate grade (0-4)
    if '학년' in df.columns:
        validate_value_ranges(df, {'학년': (0, 4)})

    # Validate program type
    allowed_program_types = ['학사', '석사', '박사']
    if '과정구분' in df.columns:
        non_null_program = df['과정구분'].dropna()
        invalid_program = non_null_program[~non_null_program.isin(allowed_program_types)]
        if not invalid_program.empty:
            raise ValueRangeError(
                f"Column '과정구분' has invalid values. Allowed: {allowed_program_types}. "
                f"Found: {invalid_program.unique().tolist()}"
            )

    # Validate enrollment status
    allowed_enrollment_statuses = ['재학', '휴학', '졸업']
    if '학적상태' in df.columns:
        non_null_status = df['학적상태'].dropna()
        invalid_status = non_null_status[~non_null_status.isin(allowed_enrollment_statuses)]
        if not invalid_status.empty:
            raise ValueRangeError(
                f"Column '학적상태' has invalid values. Allowed: {allowed_enrollment_statuses}. "
                f"Found: {invalid_status.unique().tolist()}"
            )

    # Validate gender
    allowed_genders = ['남', '여']
    if '성별' in df.columns:
        non_null_gender = df['성별'].dropna()
        invalid_gender = non_null_gender[~non_null_gender.isin(allowed_genders)]
        if not invalid_gender.empty:
            raise ValueRangeError(
                f"Column '성별' has invalid values. Allowed: {allowed_genders}. "
                f"Found: {invalid_gender.unique().tolist()}"
            )

    # Validate admission year
    if '입학년도' in df.columns:
        validate_value_ranges(df, {'입학년도': (1900, 2100)})
