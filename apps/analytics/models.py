"""
Analytics app models.

All models map to Supabase PostgreSQL tables with managed=False.
Supabase migrations control the database schema.

Models:
- DepartmentKPI: Department-level KPI metrics
- Publication: Research paper publications
- ResearchProject: Research project master data
- ExecutionRecord: Research budget execution details
- Student: Student enrollment data
- UploadHistory: File upload tracking
"""
from django.db import models
from django.utils import timezone

from apps.authentication.models import User


class DepartmentKPI(models.Model):
    """
    Department-level Key Performance Indicators.

    Maps to: department_kpi table
    Primary purpose: Track and visualize department performance metrics
    """
    id = models.BigAutoField(primary_key=True)
    evaluation_year = models.IntegerField(
        verbose_name='평가년도',
        help_text='KPI evaluation year (2000-2100)'
    )
    college = models.CharField(
        max_length=100,
        verbose_name='단과대학',
        help_text='College name'
    )
    department = models.CharField(
        max_length=100,
        verbose_name='학과',
        help_text='Department name'
    )
    employment_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='졸업생 취업률',
        help_text='Graduate employment rate (0.00-100.00%)'
    )
    full_time_faculty = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='전임교원 수',
        help_text='Number of full-time faculty'
    )
    visiting_faculty = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='초빙교원 수',
        help_text='Number of visiting faculty'
    )
    tech_transfer_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='기술이전 수입액',
        help_text='Technology transfer income (억원)'
    )
    intl_conference_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='국제학술대회 개최 횟수',
        help_text='Number of international conferences hosted'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )

    class Meta:
        db_table = 'department_kpi'
        managed = False  # Supabase manages schema
        verbose_name = '학과별 KPI'
        verbose_name_plural = '학과별 KPI 목록'
        ordering = ['-evaluation_year', 'college', 'department']

    def __str__(self):
        return f'{self.evaluation_year} - {self.college} {self.department}'


class Publication(models.Model):
    """
    Research paper publication records.

    Maps to: publications table
    Primary purpose: Track research output and journal metrics
    """
    JOURNAL_GRADE_CHOICES = [
        ('SCIE', 'SCIE'),
        ('KCI', 'KCI'),
        ('SCOPUS', 'SCOPUS'),
        ('KCI후보', 'KCI후보'),
        ('기타', '기타'),
    ]

    PROJECT_LINKED_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    id = models.BigAutoField(primary_key=True)
    publication_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='논문ID',
        help_text='Unique publication identifier (e.g., PUB-23-001)'
    )
    publication_date = models.DateField(
        verbose_name='게재일',
        help_text='Publication date'
    )
    college = models.CharField(
        max_length=100,
        verbose_name='단과대학',
        help_text='College name'
    )
    department = models.CharField(
        max_length=100,
        verbose_name='학과',
        help_text='Department name'
    )
    title = models.TextField(
        verbose_name='논문제목',
        help_text='Paper title'
    )
    first_author = models.CharField(
        max_length=100,
        verbose_name='주저자',
        help_text='First author name'
    )
    co_authors = models.TextField(
        null=True,
        blank=True,
        verbose_name='참여저자',
        help_text='Co-authors (semicolon separated)'
    )
    journal_name = models.CharField(
        max_length=255,
        verbose_name='학술지명',
        help_text='Journal name'
    )
    journal_grade = models.CharField(
        max_length=20,
        choices=JOURNAL_GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='저널등급',
        help_text='Journal grade (SCIE, KCI, etc.)'
    )
    impact_factor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Impact Factor',
        help_text='Journal impact factor'
    )
    project_linked = models.CharField(
        max_length=1,
        choices=PROJECT_LINKED_CHOICES,
        null=True,
        blank=True,
        verbose_name='과제연계여부',
        help_text='Research project linkage (Y/N)'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )

    class Meta:
        db_table = 'publications'
        managed = False  # Supabase manages schema
        verbose_name = '논문'
        verbose_name_plural = '논문 목록'
        ordering = ['-publication_date']

    def __str__(self):
        return f'{self.publication_id} - {self.title}'


class ResearchProject(models.Model):
    """
    Research project master data.

    Maps to: research_projects table
    Primary purpose: Track research projects and funding
    """
    id = models.BigAutoField(primary_key=True)
    project_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='과제번호',
        help_text='Unique project number (e.g., NRF-2023-015)'
    )
    project_name = models.CharField(
        max_length=255,
        verbose_name='과제명',
        help_text='Project name'
    )
    principal_investigator = models.CharField(
        max_length=100,
        verbose_name='연구책임자',
        help_text='Principal investigator name'
    )
    department = models.CharField(
        max_length=100,
        verbose_name='소속학과',
        help_text='Department name'
    )
    funding_agency = models.CharField(
        max_length=100,
        verbose_name='지원기관',
        help_text='Funding agency'
    )
    total_budget = models.BigIntegerField(
        verbose_name='총연구비',
        help_text='Total research budget (KRW)'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'research_projects'
        managed = False  # Supabase manages schema
        verbose_name = '연구 과제'
        verbose_name_plural = '연구 과제 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.project_number} - {self.project_name}'


class ExecutionRecord(models.Model):
    """
    Research budget execution records.

    Maps to: execution_records table
    Primary purpose: Track detailed budget spending
    """
    STATUS_CHOICES = [
        ('집행완료', '집행완료'),
        ('처리중', '처리중'),
    ]

    id = models.BigAutoField(primary_key=True)
    execution_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='집행ID',
        help_text='Unique execution ID (e.g., T2301001)'
    )
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        db_column='project_id',
        related_name='execution_records',
        verbose_name='연구 과제',
        help_text='Related research project'
    )
    execution_date = models.DateField(
        verbose_name='집행일자',
        help_text='Execution date'
    )
    expense_category = models.CharField(
        max_length=100,
        verbose_name='집행항목',
        help_text='Expense category'
    )
    amount = models.BigIntegerField(
        verbose_name='집행금액',
        help_text='Execution amount (KRW)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='상태',
        help_text='Execution status'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='비고',
        help_text='Description or notes'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )

    class Meta:
        db_table = 'execution_records'
        managed = False  # Supabase manages schema
        verbose_name = '연구비 집행 내역'
        verbose_name_plural = '연구비 집행 내역 목록'
        ordering = ['-execution_date']

    def __str__(self):
        return f'{self.execution_id} - {self.expense_category}: {self.amount}원'


class Student(models.Model):
    """
    Student enrollment and academic data.

    Maps to: students table
    Primary purpose: Track student demographics and enrollment status
    """
    PROGRAM_TYPE_CHOICES = [
        ('학사', '학사'),
        ('석사', '석사'),
        ('박사', '박사'),
    ]

    ENROLLMENT_STATUS_CHOICES = [
        ('재학', '재학'),
        ('휴학', '휴학'),
        ('졸업', '졸업'),
    ]

    GENDER_CHOICES = [
        ('남', '남'),
        ('여', '여'),
    ]

    id = models.BigAutoField(primary_key=True)
    student_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='학번',
        help_text='Student number'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='이름',
        help_text='Student name'
    )
    college = models.CharField(
        max_length=100,
        verbose_name='단과대학',
        help_text='College name'
    )
    department = models.CharField(
        max_length=100,
        verbose_name='학과',
        help_text='Department name'
    )
    grade = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='학년',
        help_text='Grade (0: graduate, 1-4: undergraduate)'
    )
    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='과정구분',
        help_text='Program type (학사/석사/박사)'
    )
    enrollment_status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        verbose_name='학적상태',
        help_text='Enrollment status'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name='성별',
        help_text='Gender'
    )
    admission_year = models.IntegerField(
        verbose_name='입학년도',
        help_text='Admission year'
    )
    advisor = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='지도교수',
        help_text='Academic advisor'
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='이메일',
        help_text='Email address'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'students'
        managed = False  # Supabase manages schema
        verbose_name = '학생'
        verbose_name_plural = '학생 목록'
        ordering = ['-admission_year', 'student_number']

    def __str__(self):
        return f'{self.student_number} - {self.name} ({self.department})'


class UploadHistory(models.Model):
    """
    File upload history and audit log.

    Maps to: upload_history table
    Primary purpose: Track data uploads and validation results
    """
    DATA_TYPE_CHOICES = [
        ('department_kpi', 'Department KPI'),
        ('publication', 'Publication'),
        ('research_budget', 'Research Budget'),
        ('student', 'Student'),
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='upload_history',
        verbose_name='업로드 사용자',
        help_text='User who uploaded the file'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='파일명',
        help_text='Original file name'
    )
    file_size = models.BigIntegerField(
        verbose_name='파일 크기',
        help_text='File size in bytes'
    )
    data_type = models.CharField(
        max_length=50,
        choices=DATA_TYPE_CHOICES,
        verbose_name='데이터 타입',
        help_text='Type of data uploaded'
    )
    upload_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='업로드 일시',
        help_text='Upload timestamp'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='처리 상태',
        help_text='Processing status'
    )
    rows_processed = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='처리된 행 수',
        help_text='Number of rows processed (success case)'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='오류 메시지',
        help_text='Error message (failure case)'
    )

    class Meta:
        db_table = 'upload_history'
        managed = False  # Supabase manages schema
        verbose_name = '업로드 이력'
        verbose_name_plural = '업로드 이력 목록'
        ordering = ['-upload_date']

    def __str__(self):
        return f'{self.file_name} - {self.data_type} ({self.status})'
