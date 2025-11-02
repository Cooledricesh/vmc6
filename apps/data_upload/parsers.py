"""
Data parsers for file uploads.

Parsers handle:
- Reading Excel/CSV files with Pandas
- Column mapping from Korean to English
- Data validation
- Database insertion with transactions
- Upload history logging

Each parser extends BaseParser and implements parse() method.
"""
import os
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student,
    UploadHistory,
)
from apps.data_upload.validators import (
    validate_department_kpi_data,
    validate_publication_data,
    validate_research_budget_data,
    validate_student_data,
)
from apps.data_upload.exceptions import (
    FileFormatError,
    FileSizeError,
    ValidationError,
)


class BaseParser(ABC):
    """
    Abstract base parser for file uploads.

    Provides common functionality:
    - File extension validation
    - File size validation
    - File reading (Excel/CSV)
    - Data cleaning

    Subclasses must implement:
    - parse(filepath, user): Main parsing logic
    """

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB in bytes
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']

    def validate_extension(self, filepath: str) -> None:
        """
        Validate file extension.

        Args:
            filepath: Path to file

        Raises:
            FileFormatError: If extension is not allowed
        """
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise FileFormatError(
                f"Invalid file format '{ext}'. Allowed formats: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

    def validate_size(self, size_bytes: int) -> None:
        """
        Validate file size.

        Args:
            size_bytes: File size in bytes

        Raises:
            FileSizeError: If file exceeds maximum size
        """
        if size_bytes > self.MAX_FILE_SIZE:
            size_mb = size_bytes / (1024 * 1024)
            raise FileSizeError(
                f"File size ({size_mb:.1f}MB) exceeds maximum allowed size (50MB)"
            )

    def read_file(self, filepath: str) -> pd.DataFrame:
        """
        Read Excel or CSV file into DataFrame.

        Args:
            filepath: Path to file

        Returns:
            DataFrame with file contents

        Raises:
            FileFormatError: If file cannot be read
        """
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        try:
            if ext == '.csv':
                df = pd.read_csv(filepath, encoding='utf-8-sig')
            elif ext in ['.xlsx', '.xls']:
                engine = 'openpyxl' if ext == '.xlsx' else 'xlrd'
                df = pd.read_excel(filepath, engine=engine)
            else:
                raise FileFormatError(f"Unsupported file format: {ext}")

            return df

        except FileNotFoundError:
            raise FileFormatError(f"File not found: {filepath}")
        except Exception as e:
            raise FileFormatError(f"Error reading file: {str(e)}")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by stripping whitespace from strings.

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()

        # Strip whitespace from string columns
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )

        return cleaned_df

    @abstractmethod
    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """
        Parse file and insert data into database.

        Must be implemented by subclasses.

        Args:
            filepath: Path to file to parse
            user: User performing the upload

        Returns:
            Dict with:
                - success: bool
                - rows_processed: int or None
                - error_message: str or None
        """
        pass


class DepartmentKPIParser(BaseParser):
    """
    Parser for Department KPI data.

    Column mapping (Korean → English):
    - 평가년도 → evaluation_year
    - 단과대학 → college
    - 학과 → department
    - 졸업생 취업률 (%) → employment_rate
    - 전임교원 수 (명) → full_time_faculty
    - 초빙교원 수 (명) → visiting_faculty
    - 연간 기술이전 수입액 (억원) → tech_transfer_income
    - 국제학술대회 개최 횟수 → intl_conference_count
    """

    DATA_TYPE = 'department_kpi'

    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """
        Parse Department KPI Excel/CSV file.

        Args:
            filepath: Path to file
            user: User performing upload

        Returns:
            Result dict with success status and details
        """
        try:
            # Validate file
            self.validate_extension(filepath)
            file_size = os.path.getsize(filepath)
            self.validate_size(file_size)

            # Read and clean data
            df = self.read_file(filepath)
            df = self.clean_data(df)

            # Validate data
            validate_department_kpi_data(df)

            # Parse and save to database
            with transaction.atomic():
                kpi_objects = []

                for _, row in df.iterrows():
                    kpi = DepartmentKPI(
                        evaluation_year=int(row['평가년도']),
                        college=row['단과대학'],
                        department=row['학과'],
                        employment_rate=Decimal(str(row['졸업생 취업률 (%)'])) if pd.notna(row['졸업생 취업률 (%)']) else None,
                        full_time_faculty=int(row['전임교원 수 (명)']) if pd.notna(row['전임교원 수 (명)']) else None,
                        visiting_faculty=int(row['초빙교원 수 (명)']) if pd.notna(row['초빙교원 수 (명)']) else None,
                        tech_transfer_income=Decimal(str(row['연간 기술이전 수입액 (억원)'])) if pd.notna(row['연간 기술이전 수입액 (억원)']) else None,
                        intl_conference_count=int(row['국제학술대회 개최 횟수']) if pd.notna(row['국제학술대회 개최 횟수']) else None,
                    )
                    kpi_objects.append(kpi)

                # Bulk insert
                DepartmentKPI.objects.bulk_create(kpi_objects)

                # Create upload history
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=file_size,
                    data_type=self.DATA_TYPE,
                    status='success',
                    rows_processed=len(kpi_objects)
                )

            return {
                'success': True,
                'rows_processed': len(kpi_objects),
                'error_message': None
            }

        except Exception as e:
            # Log failed upload
            try:
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                    data_type=self.DATA_TYPE,
                    status='failed',
                    error_message=str(e)
                )
            except:
                pass  # Don't fail if history logging fails

            return {
                'success': False,
                'rows_processed': None,
                'error_message': str(e)
            }


class PublicationParser(BaseParser):
    """
    Parser for Publication data.

    Column mapping (Korean → English):
    - 논문ID → publication_id
    - 게재일 → publication_date
    - 단과대학 → college
    - 학과 → department
    - 논문제목 → title
    - 주저자 → first_author
    - 참여저자 → co_authors
    - 학술지명 → journal_name
    - 저널등급 → journal_grade
    - Impact Factor → impact_factor
    - 과제연계여부 → project_linked
    """

    DATA_TYPE = 'publication'

    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """
        Parse Publication Excel/CSV file.

        Args:
            filepath: Path to file
            user: User performing upload

        Returns:
            Result dict with success status and details
        """
        try:
            # Validate file
            self.validate_extension(filepath)
            file_size = os.path.getsize(filepath)
            self.validate_size(file_size)

            # Read and clean data
            df = self.read_file(filepath)
            df = self.clean_data(df)

            # Validate data
            validate_publication_data(df)

            # Parse and save to database
            with transaction.atomic():
                pub_objects = []

                for _, row in df.iterrows():
                    pub = Publication(
                        publication_id=row['논문ID'],
                        publication_date=pd.to_datetime(row['게재일']).date(),
                        college=row['단과대학'],
                        department=row['학과'],
                        title=row['논문제목'],
                        first_author=row['주저자'],
                        co_authors=row['참여저자'] if pd.notna(row['참여저자']) else None,
                        journal_name=row['학술지명'],
                        journal_grade=row['저널등급'] if pd.notna(row['저널등급']) else None,
                        impact_factor=Decimal(str(row['Impact Factor'])) if pd.notna(row['Impact Factor']) else None,
                        project_linked=row['과제연계여부'] if pd.notna(row['과제연계여부']) else None,
                    )
                    pub_objects.append(pub)

                # Bulk insert
                Publication.objects.bulk_create(pub_objects)

                # Create upload history
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=file_size,
                    data_type=self.DATA_TYPE,
                    status='success',
                    rows_processed=len(pub_objects)
                )

            return {
                'success': True,
                'rows_processed': len(pub_objects),
                'error_message': None
            }

        except Exception as e:
            # Log failed upload
            try:
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                    data_type=self.DATA_TYPE,
                    status='failed',
                    error_message=str(e)
                )
            except:
                pass

            return {
                'success': False,
                'rows_processed': None,
                'error_message': str(e)
            }


class ResearchBudgetParser(BaseParser):
    """
    Parser for Research Budget data.

    This is complex: splits data into ResearchProject and ExecutionRecord.

    Column mapping:
    - 집행ID → execution_id (ExecutionRecord)
    - 과제번호 → project_number (ResearchProject)
    - 과제명 → project_name (ResearchProject)
    - 연구책임자 → principal_investigator (ResearchProject)
    - 소속학과 → department (ResearchProject)
    - 지원기관 → funding_agency (ResearchProject)
    - 총연구비 → total_budget (ResearchProject)
    - 집행일자 → execution_date (ExecutionRecord)
    - 집행항목 → expense_category (ExecutionRecord)
    - 집행금액 → amount (ExecutionRecord)
    - 상태 → status (ExecutionRecord)
    - 비고 → description (ExecutionRecord)
    """

    DATA_TYPE = 'research_budget'

    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """
        Parse Research Budget Excel/CSV file.

        Creates/updates ResearchProject and creates ExecutionRecords.

        Args:
            filepath: Path to file
            user: User performing upload

        Returns:
            Result dict with success status and details
        """
        try:
            # Validate file
            self.validate_extension(filepath)
            file_size = os.path.getsize(filepath)
            self.validate_size(file_size)

            # Read and clean data
            df = self.read_file(filepath)
            df = self.clean_data(df)

            # Validate data
            validate_research_budget_data(df)

            # Parse and save to database
            with transaction.atomic():
                execution_count = 0

                for _, row in df.iterrows():
                    # Get or create ResearchProject
                    project, created = ResearchProject.objects.get_or_create(
                        project_number=row['과제번호'],
                        defaults={
                            'project_name': row['과제명'],
                            'principal_investigator': row['연구책임자'],
                            'department': row['소속학과'],
                            'funding_agency': row['지원기관'],
                            'total_budget': int(row['총연구비']),
                        }
                    )

                    # Create ExecutionRecord
                    ExecutionRecord.objects.create(
                        execution_id=row['집행ID'],
                        project=project,
                        execution_date=pd.to_datetime(row['집행일자']).date(),
                        expense_category=row['집행항목'],
                        amount=int(row['집행금액']),
                        status=row['상태'],
                        description=row['비고'] if pd.notna(row['비고']) else None,
                    )
                    execution_count += 1

                # Create upload history
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=file_size,
                    data_type=self.DATA_TYPE,
                    status='success',
                    rows_processed=execution_count
                )

            return {
                'success': True,
                'rows_processed': execution_count,
                'error_message': None
            }

        except Exception as e:
            # Log failed upload
            try:
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                    data_type=self.DATA_TYPE,
                    status='failed',
                    error_message=str(e)
                )
            except:
                pass

            return {
                'success': False,
                'rows_processed': None,
                'error_message': str(e)
            }


class StudentParser(BaseParser):
    """
    Parser for Student data.

    Column mapping (Korean → English):
    - 학번 → student_number
    - 이름 → name
    - 단과대학 → college
    - 학과 → department
    - 학년 → grade
    - 과정구분 → program_type
    - 학적상태 → enrollment_status
    - 성별 → gender
    - 입학년도 → admission_year
    """

    DATA_TYPE = 'student'

    def parse(self, filepath: str, user: Any) -> Dict[str, Any]:
        """
        Parse Student Excel/CSV file.

        Args:
            filepath: Path to file
            user: User performing upload

        Returns:
            Result dict with success status and details
        """
        try:
            # Validate file
            self.validate_extension(filepath)
            file_size = os.path.getsize(filepath)
            self.validate_size(file_size)

            # Read and clean data
            df = self.read_file(filepath)
            df = self.clean_data(df)

            # Validate data
            validate_student_data(df)

            # Parse and save to database
            with transaction.atomic():
                student_objects = []

                for _, row in df.iterrows():
                    student = Student(
                        student_number=row['학번'],
                        name=row['이름'],
                        college=row['단과대학'],
                        department=row['학과'],
                        grade=int(row['학년']) if pd.notna(row['학년']) else None,
                        program_type=row['과정구분'] if pd.notna(row['과정구분']) else None,
                        enrollment_status=row['학적상태'],
                        gender=row['성별'] if pd.notna(row['성별']) else None,
                        admission_year=int(row['입학년도']),
                    )
                    student_objects.append(student)

                # Bulk insert
                Student.objects.bulk_create(student_objects)

                # Create upload history
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=file_size,
                    data_type=self.DATA_TYPE,
                    status='success',
                    rows_processed=len(student_objects)
                )

            return {
                'success': True,
                'rows_processed': len(student_objects),
                'error_message': None
            }

        except Exception as e:
            # Log failed upload
            try:
                UploadHistory.objects.create(
                    user=user,
                    file_name=os.path.basename(filepath),
                    file_size=os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                    data_type=self.DATA_TYPE,
                    status='failed',
                    error_message=str(e)
                )
            except:
                pass

            return {
                'success': False,
                'rows_processed': None,
                'error_message': str(e)
            }
