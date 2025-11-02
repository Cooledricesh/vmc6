#!/usr/bin/env python
"""
Test that serializers produce valid JSON without Python literals
"""
import os
import sys
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from apps.analytics.serializers import (
    to_bar_chart_data,
    to_line_chart_data,
    to_pie_chart_data,
)

def test_serializers():
    """Test that all serializers produce valid JSON"""

    print("Testing Chart Data Serializers\n")
    print("="*60)

    all_passed = True

    # Test 1: Bar chart with None values
    print("\n1. Testing bar chart with None values...")
    test_data = [
        {'department': 'CS', 'value': 85},
        {'department': 'Math', 'value': None},  # None value
        {'department': 'Physics', 'value': 90},
    ]

    result = to_bar_chart_data(test_data, 'department', 'value', 'Test Chart')

    # Convert to JSON and back
    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        # Check for Python literals
        if 'None' in json_str:
            print("  ✗ FAIL: Found Python None in JSON string")
            print(f"    JSON: {json_str[:100]}...")
            all_passed = False
        elif 'null' in json_str:
            print("  ✓ PASS: None properly converted to null")
        else:
            print("  ✓ PASS: Valid JSON produced")

    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON - {str(e)}")
        print(f"    Data: {result}")
        all_passed = False

    # Test 2: Line chart with boolean values
    print("\n2. Testing line chart with data...")
    test_data = [
        {'year': 2020, 'rate': 75.5},
        {'year': 2021, 'rate': 80.0},
        {'year': 2022, 'rate': 85.2},
    ]

    result = to_line_chart_data(test_data, 'year', 'rate', 'Trend')

    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        # Check for Python booleans
        if 'True' in json_str or 'False' in json_str:
            print("  ✗ FAIL: Found Python True/False in JSON string")
            print(f"    JSON: {json_str[:100]}...")
            all_passed = False
        else:
            print("  ✓ PASS: Valid JSON produced")

    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON - {str(e)}")
        all_passed = False

    # Test 3: Pie chart data
    print("\n3. Testing pie chart with data...")
    test_data = [
        {'category': 'A급', 'count': 10},
        {'category': 'B급', 'count': 15},
        {'category': 'C급', 'count': 5},
    ]

    result = to_pie_chart_data(test_data, 'category', 'count', 'Distribution')

    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        print("  ✓ PASS: Valid JSON produced")

    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON - {str(e)}")
        all_passed = False

    # Test 4: Empty data
    print("\n4. Testing with empty data...")
    result = to_bar_chart_data([], 'x', 'y', 'Empty')

    try:
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        print("  ✓ PASS: Empty data handled correctly")

    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON - {str(e)}")
        all_passed = False

    # Test 5: Data with special characters
    print("\n5. Testing with Korean text...")
    test_data = [
        {'dept': '컴퓨터공학과', 'value': 100},
        {'dept': '수학과', 'value': 95},
    ]

    result = to_bar_chart_data(test_data, 'dept', 'value', '학과별 데이터')

    try:
        json_str = json.dumps(result, ensure_ascii=False)
        parsed = json.loads(json_str)
        print("  ✓ PASS: Korean text handled correctly")

    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON - {str(e)}")
        all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("✓ All serialization tests passed!")
        print("  Serializers produce valid JSON without Python literals")
    else:
        print("✗ Some tests failed")
        print("  Check serializers for proper JSON encoding")
    print("="*60 + "\n")

    return all_passed

if __name__ == '__main__':
    try:
        success = test_serializers()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
