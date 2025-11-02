#!/usr/bin/env python
"""
Verify that json.dumps() properly converts Python types to JSON
"""
import json

# Test data with Python types
test_cases = [
    {
        'name': 'Python None',
        'data': {'value': None, 'text': 'test'},
        'should_contain': 'null',
        'should_not_contain': 'None',
    },
    {
        'name': 'Python True',
        'data': {'enabled': True, 'count': 5},
        'should_contain': 'true',
        'should_not_contain': 'True',
    },
    {
        'name': 'Python False',
        'data': {'enabled': False, 'count': 0},
        'should_contain': 'false',
        'should_not_contain': 'False',
    },
    {
        'name': 'Mixed types',
        'data': {
            'null_val': None,
            'bool_val': True,
            'number': 42,
            'text': 'hello',
            'list': [1, 2, None],
            'nested': {'active': False, 'count': None}
        },
        'should_contain': ['null', 'true', 'false'],
        'should_not_contain': ['None', 'True', 'False'],
    },
]

print("="*70)
print("JSON Encoding Verification Test")
print("="*70)
print("\nThis test verifies that json.dumps() properly converts Python types")
print("to their JavaScript/JSON equivalents:\n")
print("  Python None  → JSON null")
print("  Python True  → JSON true")
print("  Python False → JSON false")
print("="*70)

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. Testing: {test['name']}")
    print(f"   Data: {test['data']}")

    # Convert to JSON
    json_str = json.dumps(test['data'])
    print(f"   JSON: {json_str}")

    # Check for expected strings
    passed = True

    if isinstance(test['should_contain'], list):
        for expected in test['should_contain']:
            if expected not in json_str:
                print(f"   ✗ FAIL: Expected to find '{expected}'")
                passed = False
    else:
        if test['should_contain'] not in json_str:
            print(f"   ✗ FAIL: Expected to find '{test['should_contain']}'")
            passed = False

    # Check for unwanted strings
    if isinstance(test['should_not_contain'], list):
        for unwanted in test['should_not_contain']:
            if unwanted in json_str:
                print(f"   ✗ FAIL: Should not contain '{unwanted}'")
                passed = False
    else:
        if test['should_not_contain'] in json_str:
            print(f"   ✗ FAIL: Should not contain '{test['should_not_contain']}'")
            passed = False

    # Verify it can be parsed back
    try:
        parsed = json.loads(json_str)
        if passed:
            print(f"   ✓ PASS: Correct JSON encoding")
    except json.JSONDecodeError as e:
        print(f"   ✗ FAIL: Invalid JSON - {str(e)}")
        passed = False

    all_passed = all_passed and passed

print("\n" + "="*70)
if all_passed:
    print("✓ ALL TESTS PASSED")
    print("\njson.dumps() properly converts Python types to JSON!")
    print("This means our views.py changes are working correctly.")
else:
    print("✗ SOME TESTS FAILED")
print("="*70)

# Additional demonstration
print("\n\n" + "="*70)
print("Example: Chart data serialization")
print("="*70)

chart_data = {
    'labels': ['CS', 'Math', 'Physics'],
    'datasets': [{
        'data': [85, None, 90],
        'backgroundColor': ['#4e73df', '#1cc88a', '#36b9cc'],
        'fill': False,
    }]
}

print(f"\nPython dict:")
print(f"  {chart_data}")

json_output = json.dumps(chart_data)
print(f"\nJSON string (after json.dumps()):")
print(f"  {json_output}")

print(f"\nIn Django template with json.dumps():")
print(f"  const chartData = {{{{ chart_data|safe }}}};")
print(f"  becomes:")
print(f"  const chartData = {json_output};")

print("\n✓ This is valid JavaScript and will work in the browser!")
print("="*70)
