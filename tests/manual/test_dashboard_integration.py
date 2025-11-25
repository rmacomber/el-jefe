#!/usr/bin/env python3
"""
Test script for El Jefe Dashboard Integration

Tests all the different ways to launch the monitoring dashboard from El Jefe.
"""

import subprocess
import time
import requests
import sys
import os


def test_cli_dashboard():
    """Test CLI dashboard option."""
    print("🧪 Testing CLI Dashboard Integration...")
    print("=" * 50)

    try:
        # Test help message
        result = subprocess.run([
            sys.executable, "main.py", "--help"
        ], capture_output=True, text=True, timeout=10)

        if "--dashboard" in result.stdout:
            print("✅ CLI --dashboard option: Available in help")
        else:
            print("❌ CLI --dashboard option: Missing from help")
            return False

        print("✅ CLI Integration: Test passed")
        return True

    except Exception as e:
        print(f"❌ CLI Integration test failed: {e}")
        return False


def test_dashboard_api():
    """Test dashboard API endpoints."""
    print("\n🧪 Testing Dashboard API...")
    print("=" * 50)

    try:
        # Start dashboard in background
        print("🚀 Starting dashboard for API test...")
        dashboard_process = subprocess.Popen([
            sys.executable, "monitoring_dashboard.py"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Give it time to start
        time.sleep(3)

        # Test API endpoints
        endpoints = [
            "http://localhost:8080/api/status",
            "http://localhost:8080/api/agents",
            "http://localhost:8080/api/workflows",
            "http://localhost:8080/api/metrics"
        ]

        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint.split('/')[-1]}: Working")
                else:
                    print(f"❌ {endpoint.split('/')[-1]}: Status {response.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"❌ {endpoint.split('/')[-1]}: Error {e}")
                all_passed = False

        # Cleanup
        dashboard_process.terminate()
        dashboard_process.wait(timeout=5)

        if all_passed:
            print("✅ Dashboard API: All endpoints working")
        else:
            print("❌ Dashboard API: Some endpoints failed")

        return all_passed

    except Exception as e:
        print(f"❌ Dashboard API test failed: {e}")
        return False


def test_chat_interface():
    """Test chat interface dashboard command."""
    print("\n🧪 Testing Chat Interface Integration...")
    print("=" * 50)

    try:
        # Import the chat interface
        sys.path.insert(0, "src")

        # Test import without creating instance (avoids async issues)
        from chat_interface import ChatInterface

        print("✅ Chat Interface: Import successful")

        # Check if dashboard command is available by checking the file content
        with open("src/chat_interface.py", "r") as f:
            chat_content = f.read()

        if "/dashboard" in chat_content and "cmd_dashboard" in chat_content:
            print("✅ Chat Interface: /dashboard command found in code")
            return True
        else:
            print("❌ Chat Interface: /dashboard command missing from code")
            return False

    except Exception as e:
        print(f"❌ Chat Interface test failed: {e}")
        return False


def test_dashboard_files():
    """Test if all dashboard files exist and are valid."""
    print("\n🧪 Testing Dashboard Files...")
    print("=" * 50)

    required_files = [
        "monitoring_dashboard.py",
        "static/index.html",
        "src/dashboard_launcher.py",
        "test_dashboard.py"
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Exists")
        else:
            print(f"❌ {file_path}: Missing")
            all_exist = False

    # Check if main.py has dashboard integration
    try:
        with open("main.py", "r") as f:
            main_content = f.read()
            if "--dashboard" in main_content and "start_dashboard" in main_content:
                print("✅ main.py: Dashboard integration found")
            else:
                print("❌ main.py: Dashboard integration missing")
                all_exist = False
    except Exception as e:
        print(f"❌ main.py: Error checking - {e}")
        all_exist = False

    # Check if chat_interface.py has dashboard command
    try:
        with open("src/chat_interface.py", "r") as f:
            chat_content = f.read()
            if "/dashboard" in chat_content and "cmd_dashboard" in chat_content:
                print("✅ chat_interface.py: Dashboard command found")
            else:
                print("❌ chat_interface.py: Dashboard command missing")
                all_exist = False
    except Exception as e:
        print(f"❌ chat_interface.py: Error checking - {e}")
        all_exist = False

    if all_exist:
        print("✅ Dashboard Files: All files present and integrated")
    else:
        print("❌ Dashboard Files: Some files missing or not integrated")

    return all_exist


def show_usage_examples():
    """Show usage examples for the dashboard."""
    print("\n📚 Dashboard Usage Examples")
    print("=" * 50)

    print("🎯 Method 1: CLI Command")
    print("   python3 main.py --dashboard")
    print("   python3 main.py -d")
    print()

    print("🎯 Method 2: Interactive Chat Mode")
    print("   python3 main.py  # (launches interactive mode)")
    print("   /dashboard      # (in chat interface)")
    print()

    print("🎯 Method 3: Direct Launch")
    print("   python3 monitoring_dashboard.py")
    print()

    print("🎯 Method 4: Dashboard Launcher")
    print("   python3 src/dashboard_launcher.py")
    print()

    print("🌐 Access Points:")
    print("   Web Interface: http://localhost:8080")
    print("   WebSocket API: ws://localhost:8080/ws")
    print("   REST API: http://localhost:8080/api/")
    print()

    print("📊 Available Commands:")
    print("   /status      - Show system status")
    print("   /agents      - Show active agents")
    print("   /workflows   - Show workflow sessions")
    print("   /metrics     - Show performance metrics")
    print("   /history     - Show historical data")


def main():
    """Run all integration tests."""
    print("🚀 El Jefe Dashboard Integration Test Suite")
    print("=" * 60)

    # Run all tests
    tests = [
        ("CLI Dashboard Option", test_cli_dashboard),
        ("Dashboard API", test_dashboard_api),
        ("Chat Interface", test_chat_interface),
        ("Dashboard Files", test_dashboard_files)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Show summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print("=" * 60)
    print(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed!")
        print("✅ The dashboard is fully integrated with El Jefe!")
        show_usage_examples()
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)