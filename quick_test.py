#!/usr/bin/env python
"""
Quick test to verify chart data JSON serialization
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from apps.analytics import views
import json

User = get_user_model()

def test_view_serialization():
    """Test that views properly serialize chart data"""

    print("Testing chart data JSON serialization...\n")

    # Get or create test user
    user, created = User.objects.get_or_create(
        email='test_admin@example.com',
        defaults={
            'name': 'Test Admin',
            'department': 'Computer Science',
            'role': 'admin',
            'status': 'active'
        }
    )

    if created:
        user.set_password('testpass123')
        user.save()

    # Create request factory
    factory = RequestFactory()

    # Test views
    test_views = [
        (views.dashboard_view, '/dashboard/', 'Dashboard'),
        (views.department_kpi_view, '/analytics/department-kpi/', 'Department KPI'),
        (views.publications_view, '/analytics/publications/', 'Publications'),
        (views.research_budget_view, '/analytics/research-budget/', 'Research Budget'),
        (views.students_view, '/analytics/students/', 'Students'),
    ]

    all_passed = True

    for view_func, url, name in test_views:
        print(f"Testing {name}...")

        # Create request
        request = factory.get(url)
        request.user = user

        try:
            # Call view
            response = view_func(request)

            # Check status code
            if response.status_code != 200:
                print(f"  ✗ Failed with status code: {response.status_code}")
                all_passed = False
                continue

            # Get rendered content
            content = response.content.decode('utf-8')

            # Check for Python literals that shouldn't be in HTML
            issues = []

            # Check for patterns like: const data = {... None ...}
            if ' None' in content or 'None,' in content:
                # Could be legitimate use, check if it's in a data context
                import re
                # Look for variable assignments with None
                if re.search(r'(?:const|var|let)\s+\w+\s*=\s*[^\n]*None', content):
                    issues.append("Found Python None in JavaScript variable assignment")

            # Check for Python booleans
            if re.search(r'(?:const|var|let)\s+\w+\s*=\s*[^\n]*(?:True|False)(?![a-z])', content):
                issues.append("Found Python True/False in JavaScript")

            # More specifically, check for JSON.parse errors
            # Extract all JSON data assignments
            json_pattern = r'(?:const|var|let)\s+(\w+)\s*=\s*({.*?});'
            matches = re.finditer(json_pattern, content, re.DOTALL)

            for match in matches:
                var_name = match.group(1)
                json_str = match.group(2)

                # Try to parse as JSON
                try:
                    json.loads(json_str)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in variable '{var_name}': {str(e)}")

            if issues:
                print(f"  ✗ Issues found:")
                for issue in issues:
                    print(f"    - {issue}")
                all_passed = False
            else:
                print(f"  ✓ Passed - chart data properly serialized")

        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✓ All serialization tests passed!")
        print("  Chart data is properly JSON-encoded")
    else:
        print("✗ Some tests failed")
    print("="*60)

    return all_passed

if __name__ == '__main__':
    try:
        success = test_view_serialization()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
