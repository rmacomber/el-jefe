#!/usr/bin/env python3
"""
Comprehensive test runner for El Jefe dashboard testing
"""
import subprocess
import sys
import json
import time
import os
import argparse
from pathlib import Path

def run_command(cmd, description, timeout=300):
    """Run a command with timeout and error handling"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def run_unit_tests():
    """Run unit tests with pytest"""
    return run_command(
        "python3 -m pytest tests/test_dashboard_functionality.py -v --tb=short",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        "python3 -m pytest tests/test_functionality_validation.py -v --tb=short",
        "Integration Tests"
    )

def run_e2e_tests():
    """Run end-to-end tests with Playwright"""
    return run_command(
        "python3 -m pytest tests/test_end_to_end.py -v --tb=short --browser chromium",
        "End-to-End Tests",
        timeout=600
    )

def run_e2e_auth_tests():
    """Run end-to-end tests with authentication"""
    return run_command(
        "python3 tests/test_e2e_with_auth.py",
        "E2E Authentication Tests",
        timeout=300
    )

def run_performance_tests():
    """Run performance tests with Locust"""
    print("\n🚀 Starting Performance Tests with Locust...")
    print("Note: Locust will run in headless mode. For web UI, run manually.")

    return run_command(
        "locust -f tests/locustfile.py --headless --users 20 --spawn-rate 5 --run-time 60s --host http://localhost:8080",
        "Performance Tests",
        timeout=120
    )

def run_security_tests():
    """Run security-focused tests"""
    return run_command(
        "python3 -m pytest tests/test_dashboard_functionality.py::TestAuthenticationSecurity -v --tb=short",
        "Security Tests"
    )

def check_dashboard_running():
    """Check if the dashboard is running"""
    try:
        import requests
        response = requests.get("http://localhost:8080", timeout=5)
        return response.status_code in [200, 401]  # 401 is expected (requires auth)
    except:
        return False

def start_dashboard_if_needed():
    """Start the dashboard if not running"""
    if not check_dashboard_running():
        print("🚀 Starting El Jefe dashboard...")
        # Start dashboard in background
        import subprocess
        import time

        try:
            process = subprocess.Popen(
                [sys.executable, "monitoring_dashboard.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for dashboard to start
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if check_dashboard_running():
                    print("✅ Dashboard started successfully")
                    return process
                if i % 5 == 0:
                    print(f"Waiting for dashboard to start... ({i}/30s)")

            print("❌ Failed to start dashboard")
            return None

        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return None
    else:
        print("✅ Dashboard is already running")
        return None

def generate_test_report():
    """Generate a comprehensive test report"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_suite": "El Jefe Dashboard Testing",
        "tests": []
    }

    # Load test results if they exist
    test_results_dir = Path("test_results")
    if test_results_dir.exists():
        for result_file in test_results_dir.glob("*.json"):
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    report["tests"].append({
                        "file": result_file.name,
                        "data": data
                    })
            except:
                pass

    # Save consolidated report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("📊 Test report generated: test_report.json")

def main():
    parser = argparse.ArgumentParser(description="El Jefe Dashboard Test Runner")
    parser.add_argument("--test-type", choices=[
        "unit", "integration", "e2e", "e2e-auth", "performance", "security", "all"
    ], default="all", help="Type of test to run")
    parser.add_argument("--no-start-dashboard", action="store_true",
                       help="Don't start the dashboard automatically")
    parser.add_argument("--report-only", action="store_true",
                       help="Only generate report from existing test results")

    args = parser.parse_args()

    print("🧪 El Jefe Dashboard Test Runner")
    print("=" * 50)

    if args.report_only:
        generate_test_report()
        return

    # Start dashboard if needed
    dashboard_process = None
    if not args.no_start_dashboard:
        dashboard_process = start_dashboard_if_needed()
        if dashboard_process is None and not check_dashboard_running():
            print("❌ Cannot proceed without running dashboard")
            return

    # Track results
    results = {}

    try:
        # Run tests based on selection
        if args.test_type in ["unit", "all"]:
            results["unit"] = run_unit_tests()

        if args.test_type in ["integration", "all"]:
            results["integration"] = run_integration_tests()

        if args.test_type in ["e2e", "all"] and check_dashboard_running():
            results["e2e"] = run_e2e_tests()

        if args.test_type in ["e2e-auth", "all"] and check_dashboard_running():
            results["e2e-auth"] = run_e2e_auth_tests()

        if args.test_type in ["performance", "all"] and check_dashboard_running():
            results["performance"] = run_performance_tests()

        if args.test_type in ["security", "all"]:
            results["security"] = run_security_tests()

    finally:
        # Clean up dashboard process
        if dashboard_process:
            print("\n🛑 Stopping dashboard...")
            dashboard_process.terminate()
            dashboard_process.wait()

    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_type, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_type.title():<15} {status}")

    print("-" * 50)
    print(f"Overall: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

    # Generate report
    generate_test_report()

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()