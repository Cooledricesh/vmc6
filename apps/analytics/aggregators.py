"""
Data aggregators for analytics app.

Aggregators compute statistics and metrics from database models.
They provide reusable business logic for data analysis and visualization.

Classes:
- DepartmentKPIAggregator: Department KPI metrics
- PublicationAggregator: Publication statistics
- ResearchBudgetAggregator: Research budget and execution analysis
- StudentAggregator: Student enrollment and demographics
"""
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import Coalesce
from decimal import Decimal

from apps.analytics.models import (
    DepartmentKPI,
    Publication,
    ResearchProject,
    ExecutionRecord,
    Student
)


class DepartmentKPIAggregator:
    """
    Aggregate and analyze department KPI data.

    Methods:
    - get_average_employment_rate: Calculate average employment rate
    - get_kpi_by_department: Get KPI for specific departments
    - get_kpi_trend_by_year: Analyze KPI trends over years
    - get_kpi_by_college: Get all KPIs for a college
    """

    def get_average_employment_rate(self, year=None):
        """
        Calculate average employment rate.

        Args:
            year (int, optional): Filter by specific year

        Returns:
            Decimal: Average employment rate, or None if no data
        """
        queryset = DepartmentKPI.objects.all()

        if year:
            queryset = queryset.filter(evaluation_year=year)

        result = queryset.aggregate(
            avg_rate=Avg('employment_rate')
        )

        avg_rate = result['avg_rate']
        if avg_rate is not None:
            return Decimal(str(avg_rate)).quantize(Decimal('0.01'))
        return None

    def get_kpi_by_department(self, departments, year=None):
        """
        Get KPI data for specific departments.

        Args:
            departments (list): List of department names
            year (int, optional): Filter by specific year

        Returns:
            QuerySet: Department KPI records
        """
        queryset = DepartmentKPI.objects.filter(department__in=departments)

        if year:
            queryset = queryset.filter(evaluation_year=year)

        return queryset.order_by('-evaluation_year', 'college', 'department')

    def get_kpi_trend_by_year(self, department, years):
        """
        Get KPI trend for a department over multiple years.

        Args:
            department (str): Department name
            years (list): List of years to analyze

        Returns:
            QuerySet: KPI records ordered by year (DESC)
        """
        return DepartmentKPI.objects.filter(
            department=department,
            evaluation_year__in=years
        ).order_by('-evaluation_year')

    def get_kpi_by_college(self, college, year=None):
        """
        Get all KPIs for a specific college.

        Args:
            college (str): College name
            year (int, optional): Filter by specific year

        Returns:
            QuerySet: Department KPI records for the college
        """
        queryset = DepartmentKPI.objects.filter(college=college)

        if year:
            queryset = queryset.filter(evaluation_year=year)

        return queryset.order_by('department')


class PublicationAggregator:
    """
    Aggregate and analyze publication data.

    Methods:
    - get_total_publication_count: Count total publications
    - get_publications_by_journal_grade: Distribution by journal grade
    - get_average_impact_factor: Average impact factor
    - get_publications_by_first_author: Publication count by author
    """

    def get_total_publication_count(self, department=None, year=None):
        """
        Get total publication count.

        Args:
            department (str, optional): Filter by department
            year (int, optional): Filter by publication year

        Returns:
            int: Total publication count
        """
        queryset = Publication.objects.all()

        if department:
            queryset = queryset.filter(department=department)

        if year:
            queryset = queryset.filter(publication_date__year=year)

        return queryset.count()

    def get_publications_by_journal_grade(self):
        """
        Get publication distribution by journal grade.

        Returns:
            dict: Journal grade -> count mapping
        """
        result = Publication.objects.values('journal_grade').annotate(
            count=Count('id')
        )

        return {item['journal_grade']: item['count'] for item in result}

    def get_average_impact_factor(self, journal_grade=None):
        """
        Calculate average impact factor.

        Args:
            journal_grade (str, optional): Filter by journal grade

        Returns:
            Decimal: Average impact factor, or None if no data
        """
        queryset = Publication.objects.exclude(impact_factor__isnull=True)

        if journal_grade:
            queryset = queryset.filter(journal_grade=journal_grade)

        result = queryset.aggregate(avg_if=Avg('impact_factor'))

        avg_if = result['avg_if']
        if avg_if is not None:
            return Decimal(str(avg_if)).quantize(Decimal('0.01'))
        return None

    def get_publications_by_first_author(self, limit=10):
        """
        Get publication count by first author.

        Args:
            limit (int): Maximum number of authors to return

        Returns:
            list: List of dicts with 'first_author' and 'count'
        """
        result = Publication.objects.values('first_author').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        return list(result)


class ResearchBudgetAggregator:
    """
    Aggregate and analyze research budget data.

    Methods:
    - get_total_budget_and_execution: Total budget and execution summary
    - get_budget_by_department: Budget aggregation by department
    - get_execution_by_category: Execution amount by category
    - get_execution_rate_by_project: Execution rate per project
    """

    def get_total_budget_and_execution(self):
        """
        Calculate total budget and execution.

        Returns:
            dict: {
                'total_budget': int,
                'total_executed': int,
                'execution_rate': Decimal
            }
        """
        budget_result = ResearchProject.objects.aggregate(
            total_budget=Coalesce(Sum('total_budget'), 0)
        )

        execution_result = ExecutionRecord.objects.aggregate(
            total_executed=Coalesce(Sum('amount'), 0)
        )

        total_budget = budget_result['total_budget']
        total_executed = execution_result['total_executed']

        if total_budget > 0:
            execution_rate = Decimal(total_executed) / Decimal(total_budget) * 100
            execution_rate = execution_rate.quantize(Decimal('0.01'))
        else:
            execution_rate = Decimal('0.00')

        return {
            'total_budget': total_budget,
            'total_executed': total_executed,
            'execution_rate': execution_rate
        }

    def get_budget_by_department(self):
        """
        Get budget and execution by department.

        Returns:
            list: List of dicts with department, budget, and execution data
        """
        # Aggregate budget by department
        projects = ResearchProject.objects.values('department').annotate(
            total_budget=Sum('total_budget')
        )

        # Create department -> budget mapping
        dept_budgets = {p['department']: p['total_budget'] for p in projects}

        # Aggregate execution by department via project FK
        executions = ExecutionRecord.objects.values(
            'project__department'
        ).annotate(
            total_executed=Sum('amount')
        )

        # Create department -> execution mapping
        dept_executions = {
            e['project__department']: e['total_executed']
            for e in executions
        }

        # Combine results
        result = []
        for dept, budget in dept_budgets.items():
            executed = dept_executions.get(dept, 0)
            execution_rate = Decimal('0.00')
            if budget > 0:
                execution_rate = Decimal(executed) / Decimal(budget) * 100
                execution_rate = execution_rate.quantize(Decimal('0.01'))

            result.append({
                'department': dept,
                'total_budget': budget,
                'total_executed': executed,
                'execution_rate': execution_rate
            })

        return result

    def get_execution_by_category(self):
        """
        Get execution amount by expense category.

        Returns:
            dict: Category -> total amount mapping
        """
        result = ExecutionRecord.objects.values('expense_category').annotate(
            total_amount=Sum('amount')
        )

        return {item['expense_category']: item['total_amount'] for item in result}

    def get_execution_rate_by_project(self):
        """
        Calculate execution rate for each project.

        Returns:
            list: List of dicts with project info and execution rate
        """
        # Get all projects with their execution sums
        projects = ResearchProject.objects.annotate(
            total_executed=Coalesce(Sum('execution_records__amount'), 0)
        ).values(
            'project_number',
            'project_name',
            'total_budget',
            'total_executed'
        )

        result = []
        for project in projects:
            budget = project['total_budget']
            executed = project['total_executed']

            if budget > 0:
                execution_rate = Decimal(executed) / Decimal(budget) * 100
                execution_rate = execution_rate.quantize(Decimal('0.01'))
            else:
                execution_rate = Decimal('0.00')

            result.append({
                'project_number': project['project_number'],
                'project_name': project['project_name'],
                'total_budget': budget,
                'total_executed': executed,
                'execution_rate': execution_rate
            })

        return result


class StudentAggregator:
    """
    Aggregate and analyze student data.

    Methods:
    - get_total_students_and_enrollment_rate: Total students and enrollment rate
    - get_students_by_grade: Student distribution by grade
    - get_students_by_department: Student count by department
    - get_students_by_admission_year: Student count by admission year
    - get_students_by_program_type: Student distribution by program type
    """

    def get_total_students_and_enrollment_rate(self, department=None):
        """
        Calculate total students and enrollment rate.

        Args:
            department (str, optional): Filter by department

        Returns:
            dict: {
                'total_students': int,
                'enrolled_students': int,
                'enrollment_rate': Decimal
            }
        """
        queryset = Student.objects.all()

        if department:
            queryset = queryset.filter(department=department)

        total = queryset.count()
        enrolled = queryset.filter(enrollment_status='재학').count()

        if total > 0:
            enrollment_rate = Decimal(enrolled) / Decimal(total) * 100
            enrollment_rate = enrollment_rate.quantize(Decimal('0.01'))
        else:
            enrollment_rate = Decimal('0.00')

        return {
            'total_students': total,
            'enrolled_students': enrolled,
            'enrollment_rate': enrollment_rate
        }

    def get_students_by_grade(self):
        """
        Get student distribution by grade.

        Returns:
            dict: Grade -> count mapping
        """
        result = Student.objects.values('grade').annotate(
            count=Count('id')
        )

        return {item['grade']: item['count'] for item in result}

    def get_students_by_department(self):
        """
        Get student count by department.

        Returns:
            list: List of dicts with department and student counts
        """
        result = Student.objects.values('department').annotate(
            total_students=Count('id'),
            enrolled_students=Count('id', filter=Q(enrollment_status='재학')),
            on_leave_students=Count('id', filter=Q(enrollment_status='휴학')),
            graduated_students=Count('id', filter=Q(enrollment_status='졸업'))
        ).order_by('department')

        return list(result)

    def get_students_by_admission_year(self, years=None):
        """
        Get student count by admission year.

        Args:
            years (list, optional): Filter by specific years

        Returns:
            dict: Year -> count mapping
        """
        queryset = Student.objects.all()

        if years:
            queryset = queryset.filter(admission_year__in=years)

        result = queryset.values('admission_year').annotate(
            count=Count('id')
        )

        return {item['admission_year']: item['count'] for item in result}

    def get_students_by_program_type(self):
        """
        Get student distribution by program type.

        Returns:
            dict: Program type -> count mapping
        """
        result = Student.objects.values('program_type').annotate(
            count=Count('id')
        )

        return {item['program_type']: item['count'] for item in result}
