"""
Analytics Views

This module contains all view functions for the analytics dashboard.

Views:
- dashboard_view: Main dashboard with overall KPI summary
- department_kpi_view: Department KPI analysis and visualization
- publications_view: Publication statistics and analysis
- research_budget_view: Research budget and execution analysis
- students_view: Student enrollment and demographics

All views require login and apply role-based permission filtering.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from decimal import Decimal

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
from apps.analytics.serializers import (
    to_bar_chart_data,
    to_line_chart_data,
    to_pie_chart_data,
)
from apps.analytics.filters import apply_user_permission_filter


def _check_user_active(user):
    """
    Check if user is active (approved).

    Args:
        user: User object

    Returns:
        bool: True if user is active
    """
    return user.status == 'active'


@login_required(login_url='/login/')
def dashboard_view(request):
    """
    Main dashboard view with overall KPI summary.

    Shows:
    - Total departments, publications, students
    - Average employment rate
    - Total research budget and execution
    - Chart data for visualizations

    Permission filtering:
    - Admin/Manager: See all departments
    - Viewer: See only their own department

    Template: analytics/dashboard.html
    """
    # Check if user is active
    if not _check_user_active(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Your account is pending approval.')

    # Apply permission filtering to all querysets
    kpis = apply_user_permission_filter(DepartmentKPI.objects.all(), request.user)
    publications = apply_user_permission_filter(Publication.objects.all(), request.user)
    projects = apply_user_permission_filter(ResearchProject.objects.all(), request.user)
    students = apply_user_permission_filter(Student.objects.all(), request.user)

    # Get aggregated data using aggregators
    kpi_aggregator = DepartmentKPIAggregator()
    pub_aggregator = PublicationAggregator()
    budget_aggregator = ResearchBudgetAggregator()
    student_aggregator = StudentAggregator()

    # Calculate summary statistics
    total_departments = kpis.values('department').distinct().count()
    total_publications = publications.count()
    total_students = students.count()

    # Average employment rate
    avg_employment_rate = kpi_aggregator.get_average_employment_rate()

    # Research budget totals
    total_budget = projects.aggregate(total=Sum('total_budget'))['total'] or Decimal('0')

    # Get execution records for accessible projects
    project_ids = projects.values_list('id', flat=True)
    execution_total = ExecutionRecord.objects.filter(
        project_id__in=project_ids
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Prepare chart data
    # Employment rate by department
    kpi_data = list(kpis.values('department', 'employment_rate').order_by('department'))
    employment_chart_data = to_bar_chart_data(
        kpi_data,
        label_field='department',
        value_field='employment_rate',
        title='Employment Rate by Department'
    )

    # Publications by department
    pub_by_dept = list(publications.values('department').annotate(
        count=Count('id')
    ).order_by('department'))
    publication_chart_data = to_bar_chart_data(
        pub_by_dept,
        label_field='department',
        value_field='count',
        title='Publications by Department'
    )

    # Budget by department
    budget_by_dept = list(projects.values('department').annotate(
        total_budget=Sum('total_budget')
    ).order_by('department'))
    budget_chart_data = to_bar_chart_data(
        budget_by_dept,
        label_field='department',
        value_field='total_budget',
        title='Research Budget by Department'
    )

    context = {
        'total_departments': total_departments,
        'total_publications': total_publications,
        'total_students': total_students,
        'avg_employment_rate': avg_employment_rate,
        'total_research_budget': total_budget,
        'total_execution_amount': execution_total,
        'employment_chart_data': employment_chart_data,
        'publication_chart_data': publication_chart_data,
        'budget_chart_data': budget_chart_data,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required(login_url='/login/')
def department_kpi_view(request):
    """
    Department KPI analysis view.

    Shows:
    - KPI trends over years
    - Department comparisons
    - Detailed metrics (employment, student-faculty ratio, etc.)

    Supports year filtering via GET parameter.

    Template: analytics/department_kpi.html
    """
    # Check if user is active
    if not _check_user_active(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Your account is pending approval.')

    # Get year filter from request
    selected_year = request.GET.get('year')
    if selected_year:
        try:
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            selected_year = None

    # Apply permission filtering
    kpis = apply_user_permission_filter(DepartmentKPI.objects.all(), request.user)

    # Filter by year if provided
    if selected_year:
        kpis = kpis.filter(evaluation_year=selected_year)

    # Aggregator
    kpi_aggregator = DepartmentKPIAggregator()

    # Get trend data (year over year)
    trend_data = list(kpis.values('evaluation_year').annotate(
        avg_employment=Avg('employment_rate'),
        avg_student_faculty=Avg('student_faculty_ratio')
    ).order_by('evaluation_year'))

    kpi_trend_data = to_line_chart_data(
        trend_data,
        label_field='evaluation_year',
        value_fields={
            'avg_employment': 'Employment Rate',
            'avg_student_faculty': 'Student-Faculty Ratio'
        }
    )

    # Department comparison
    dept_comparison = list(kpis.values('department', 'employment_rate').order_by('department'))
    department_comparison_data = to_bar_chart_data(
        dept_comparison,
        label_field='department',
        value_field='employment_rate',
        title='Employment Rate by Department'
    )

    context = {
        'kpi_trend_data': kpi_trend_data,
        'department_comparison_data': department_comparison_data,
        'selected_year': selected_year,
    }

    return render(request, 'analytics/department_kpi.html', context)


@login_required(login_url='/login/')
def publications_view(request):
    """
    Publications analysis view.

    Shows:
    - Journal grade distribution
    - Publications by department
    - Publication trends over time

    Template: analytics/publications.html
    """
    # Check if user is active
    if not _check_user_active(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Your account is pending approval.')

    # Apply permission filtering
    publications = apply_user_permission_filter(Publication.objects.all(), request.user)

    # Aggregator
    pub_aggregator = PublicationAggregator()

    # Grade distribution
    grade_dist = list(publications.values('journal_grade').annotate(
        count=Count('id')
    ).order_by('journal_grade'))

    grade_distribution_data = to_pie_chart_data(
        grade_dist,
        label_field='journal_grade',
        value_field='count',
        title='Publications by Journal Grade'
    )

    # Publications by department
    dept_pubs = list(publications.values('department').annotate(
        count=Count('id')
    ).order_by('department'))

    department_publication_data = to_bar_chart_data(
        dept_pubs,
        label_field='department',
        value_field='count',
        title='Publications by Department'
    )

    context = {
        'grade_distribution_data': grade_distribution_data,
        'department_publication_data': department_publication_data,
    }

    return render(request, 'analytics/publications.html', context)


@login_required(login_url='/login/')
def research_budget_view(request):
    """
    Research budget and execution analysis view.

    Shows:
    - Budget execution rate
    - Category distribution
    - Department-wise budget allocation

    Template: analytics/research_budget.html
    """
    # Check if user is active
    if not _check_user_active(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Your account is pending approval.')

    # Apply permission filtering
    projects = apply_user_permission_filter(ResearchProject.objects.all(), request.user)

    # Aggregator
    budget_aggregator = ResearchBudgetAggregator()

    # Get execution records for accessible projects
    project_ids = projects.values_list('id', flat=True)
    executions = ExecutionRecord.objects.filter(project_id__in=project_ids)

    # Calculate execution rate by project
    execution_rates = []
    for project in projects:
        total_budget = project.total_budget
        executed = executions.filter(project=project).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        rate = (executed / total_budget * 100) if total_budget > 0 else Decimal('0')

        execution_rates.append({
            'project_name': project.project_name,
            'execution_rate': rate
        })

    execution_rate_data = to_bar_chart_data(
        execution_rates,
        label_field='project_name',
        value_field='execution_rate',
        title='Budget Execution Rate by Project'
    )

    # Category distribution
    category_dist = list(executions.values('expense_category').annotate(
        total=Sum('amount')
    ).order_by('expense_category'))

    category_distribution_data = to_pie_chart_data(
        category_dist,
        label_field='expense_category',
        value_field='total',
        title='Budget by Category'
    )

    context = {
        'execution_rate_data': execution_rate_data,
        'category_distribution_data': category_distribution_data,
    }

    return render(request, 'analytics/research_budget.html', context)


@login_required(login_url='/login/')
def students_view(request):
    """
    Student enrollment and demographics view.

    Shows:
    - Enrollment by year
    - Department distribution
    - Student status breakdown

    Template: analytics/students.html
    """
    # Check if user is active
    if not _check_user_active(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Your account is pending approval.')

    # Apply permission filtering
    students = apply_user_permission_filter(Student.objects.all(), request.user)

    # Aggregator
    student_aggregator = StudentAggregator()

    # Total students
    total_students = students.count()

    # Enrollment by year
    enrollment_by_year = list(students.values('admission_year').annotate(
        count=Count('id')
    ).order_by('admission_year'))

    enrollment_by_year_data = to_bar_chart_data(
        enrollment_by_year,
        label_field='admission_year',
        value_field='count',
        title='Enrollment by Year'
    )

    # Department distribution
    dept_dist = list(students.values('department').annotate(
        count=Count('id')
    ).order_by('department'))

    department_distribution_data = to_pie_chart_data(
        dept_dist,
        label_field='department',
        value_field='count',
        title='Students by Department'
    )

    context = {
        'total_students': total_students,
        'enrollment_by_year_data': enrollment_by_year_data,
        'department_distribution_data': department_distribution_data,
    }

    return render(request, 'analytics/students.html', context)
