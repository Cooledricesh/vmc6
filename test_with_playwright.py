#!/usr/bin/env python
"""
Test script using Playwright to verify all analytics pages render correctly
and charts are displayed without JavaScript errors.
"""
import asyncio
import sys
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "test_admin@example.com"
TEST_PASSWORD = "testpass123"

async def test_pages():
    """Test all analytics pages with Playwright"""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Collect console messages and errors
        console_messages = []
        js_errors = []

        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        page.on("pageerror", lambda exc: js_errors.append(str(exc)))

        try:
            # Step 1: Login
            print("Step 1: Logging in...")
            await page.goto(f"{BASE_URL}/login/")
            await page.wait_for_load_state("networkidle")

            # Fill login form
            await page.fill('input[name="username"]', TEST_EMAIL)
            await page.fill('input[name="password"]', TEST_PASSWORD)
            await page.click('button[type="submit"]')

            # Wait for redirect
            await page.wait_for_url(f"{BASE_URL}/dashboard/", timeout=10000)
            print("✓ Login successful\n")

            # Test pages
            pages_to_test = [
                ("/dashboard/", "Dashboard"),
                ("/analytics/department-kpi/", "Department KPI"),
                ("/analytics/publications/", "Publications"),
                ("/analytics/research-budget/", "Research Budget"),
                ("/analytics/students/", "Students"),
            ]

            all_passed = True

            for url, name in pages_to_test:
                print(f"Testing {name} ({url})...")

                # Clear previous errors
                js_errors.clear()
                console_messages.clear()

                # Navigate to page
                try:
                    response = await page.goto(f"{BASE_URL}{url}")
                    await page.wait_for_load_state("networkidle")

                    # Check response status
                    if response.status != 200:
                        print(f"  ✗ HTTP {response.status}")
                        all_passed = False
                        continue

                    # Wait a bit for charts to render
                    await asyncio.sleep(1)

                    # Check for JavaScript errors
                    if js_errors:
                        print(f"  ✗ JavaScript errors found:")
                        for error in js_errors:
                            print(f"    - {error}")
                        all_passed = False
                        continue

                    # Check console for specific errors
                    error_messages = [
                        msg for msg in console_messages
                        if msg["type"] == "error"
                    ]

                    if error_messages:
                        print(f"  ✗ Console errors found:")
                        for msg in error_messages:
                            print(f"    - {msg['text']}")
                        all_passed = False
                        continue

                    # Check for Python literals in page source
                    content = await page.content()

                    issues = []

                    # Check for "None" in JavaScript context
                    if 'value="None"' in content:
                        issues.append("Found Python None in HTML attributes")

                    # Check for Python boolean literals in script tags
                    if '<script>' in content:
                        # Look for patterns like: var x = False or const y = True
                        import re

                        # Extract script content
                        scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
                        for script in scripts:
                            if re.search(r'(?:const|var|let)\s+\w+\s*=\s*(?:True|False|None)', script):
                                issues.append("Found Python literals (True/False/None) in JavaScript")

                            # Check for unparseable values
                            if '"None"' in script and 'value' in script:
                                issues.append("Found 'None' string in chart data")

                    # Check if canvas elements exist (charts should be rendered)
                    canvas_elements = await page.query_selector_all('canvas')
                    canvas_count = len(canvas_elements)

                    if canvas_count == 0:
                        issues.append("No canvas elements found - charts may not be rendering")

                    if issues:
                        print(f"  ✗ Issues found:")
                        for issue in issues:
                            print(f"    - {issue}")
                        all_passed = False
                    else:
                        print(f"  ✓ Page loaded successfully")
                        print(f"    - {canvas_count} chart(s) rendered")

                except Exception as e:
                    print(f"  ✗ Exception: {str(e)}")
                    all_passed = False

            print("\n" + "="*60)
            if all_passed:
                print("✓ All tests passed!")
            else:
                print("✗ Some tests failed")
            print("="*60)

            await browser.close()
            return all_passed

        except Exception as e:
            print(f"✗ Fatal error: {str(e)}")
            await browser.close()
            return False

async def main():
    """Main entry point"""
    try:
        success = await test_pages()
        return 0 if success else 1
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
