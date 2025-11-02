"""
URL Configuration for Analytics App

Maps URL patterns to analytics view functions.

URL Patterns:
- / or /dashboard/ - Main dashboard
- /department-kpi/ - Department KPI visualization
- /publications/ - Publications analysis
- /research-budget/ - Research budget analysis
- /students/ - Student statistics
"""
from django.urls import path
from apps.analytics import views

app_name = 'analytics'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alt'),

    # Department KPI
    path('department-kpi/', views.department_kpi_view, name='department_kpi'),

    # Publications
    path('publications/', views.publications_view, name='publications'),

    # Research Budget
    path('research-budget/', views.research_budget_view, name='research_budget'),

    # Students
    path('students/', views.students_view, name='students'),
]
