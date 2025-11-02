#!/usr/bin/env python
"""
Quick script to test analytics URLs for FieldErrors.
This script will attempt to import views and check if they can be called without errors.
"""
import os
import sys
import django

# Add the project to path
sys.path.insert(0, '/Users/seunghyun/Test/vmc6')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.test import RequestFactory
from apps.authentication.models import User
from apps.analytics.views import (
    dashboard_view,
    department_kpi_view,
    publications_view,
    research_budget_view,
    students_view
)

def test_view_no_field_errors(view_func, view_name):
    """Test if a view can be called without FieldError"""
    factory = RequestFactory()

    # Create a test admin user (or use existing)
    try:
        admin = User.objects.get(email='admin@test.com')
    except User.DoesNotExist:
        admin = User.objects.create_user(
            email='admin@test.com',
            username='testadmin',
            password='testpass123',
            role='admin',
            status='active'
        )

    # Create a GET request
    request = factory.get('/test/')
    request.user = admin

    try:
        response = view_func(request)
        print(f"✓ {view_name}: SUCCESS (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ {view_name}: FAILED - {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing Analytics Views for FieldErrors...")
    print("=" * 60)

    views_to_test = [
        (dashboard_view, 'dashboard_view'),
        (department_kpi_view, 'department_kpi_view'),
        (publications_view, 'publications_view'),
        (research_budget_view, 'research_budget_view'),
        (students_view, 'students_view'),
    ]

    results = []
    for view_func, view_name in views_to_test:
        results.append(test_view_no_field_errors(view_func, view_name))

    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} views passed")

    if all(results):
        print("\n✓ All views are working correctly!")
        sys.exit(0)
    else:
        print("\n✗ Some views have errors. Please check the output above.")
        sys.exit(1)
