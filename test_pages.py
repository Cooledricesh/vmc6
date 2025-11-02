#!/usr/bin/env python
"""
Test script to verify all analytics pages load without JavaScript errors.
This script uses Django's test client to check if pages return 200 status
and that chart data is properly JSON-encoded.
"""
import os
import sys
import django
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_pages():
    """Test all analytics pages"""

    # Create test client
    client = Client()

    # Get or create a test user with admin role
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
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"✓ Using existing test user: {user.email}")

    # Login
    login_success = client.login(username=user.email, password='testpass123')
    if not login_success:
        print("✗ Failed to login")
        return False

    print("✓ Logged in successfully\n")

    # Test pages
    pages = [
        ('/dashboard/', 'Dashboard'),
        ('/analytics/department-kpi/', 'Department KPI'),
        ('/analytics/publications/', 'Publications'),
        ('/analytics/research-budget/', 'Research Budget'),
        ('/analytics/students/', 'Students'),
    ]

    all_passed = True

    for url, name in pages:
        print(f"Testing {name} ({url})...")

        try:
            response = client.get(url)

            # Check status code
            if response.status_code != 200:
                print(f"  ✗ Failed with status code: {response.status_code}")
                all_passed = False
                continue

            # Check if response contains HTML
            content = response.content.decode('utf-8')

            # Check for Python-specific strings that shouldn't be in rendered HTML
            errors = []

            if 'None' in content and 'value="None"' in content:
                errors.append("Found Python None in HTML")

            if 'False' in content and not 'false' in content.lower():
                # Check if it's JavaScript False (not false)
                if 'var ' in content and 'False' in content:
                    errors.append("Found Python False instead of JavaScript false")

            if 'True' in content and not 'true' in content.lower():
                # Check if it's JavaScript True (not true)
                if 'var ' in content and 'True' in content:
                    errors.append("Found Python True instead of JavaScript true")

            # Check for proper JSON encoding in script tags
            if '<script>' in content:
                # Extract script content
                import re
                scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
                for script in scripts:
                    # Check if there are chart data assignments
                    if 'const ' in script or 'var ' in script or 'let ' in script:
                        # Try to find JSON data
                        json_matches = re.findall(r'(?:const|var|let)\s+\w+\s*=\s*({.*?});', script, re.DOTALL)
                        for json_str in json_matches:
                            try:
                                json.loads(json_str)
                            except json.JSONDecodeError:
                                # Check if it contains Python literals
                                if 'None' in json_str or 'True' in json_str or 'False' in json_str:
                                    errors.append("Chart data contains Python literals instead of JSON")

            if errors:
                print(f"  ✗ Found issues:")
                for error in errors:
                    print(f"    - {error}")
                all_passed = False
            else:
                print(f"  ✓ Page loaded successfully without Python literal errors")

        except Exception as e:
            print(f"  ✗ Exception occurred: {str(e)}")
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*50)

    return all_passed

if __name__ == '__main__':
    success = test_pages()
    sys.exit(0 if success else 1)
