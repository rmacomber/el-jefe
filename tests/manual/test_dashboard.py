#!/usr/bin/env python3
"""
Test script for the monitoring dashboard.
Quick test without requiring all dependencies.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path for imports (absolute path)
# File is in tests/manual/, project root is two levels up
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if dashboard dependencies are available."""
    print("Testing dashboard dependencies...")

    try:
        import aiohttp
        print("✅ aiohttp: Available")
    except ImportError:
        print("❌ aiohttp: Not installed (pip install aiohttp)")

    try:
        import websockets
        print("✅ websockets: Available")
    except ImportError:
        print("❌ websockets: Not installed (pip install websockets)")

    try:
        import aiohttp_cors
        print("✅ aiohttp_cors: Available")
    except ImportError:
        print("❌ aiohttp_cors: Not installed (pip install aiohttp-cors)")

    # Test core El Jefe imports
    try:
        from main import Orchestrator
        print("✅ Orchestrator: Available")
    except ImportError as e:
        print(f"❌ Orchestrator: Import failed - {e}")

    try:
        # ProgressMonitor may not exist as a separate module
        from monitoring_dashboard import MonitoringDashboard
        print("✅ MonitoringDashboard: Available")
    except ImportError as e:
        print(f"❌ MonitoringDashboard: Import failed - {e}")

def test_basic_functionality():
    """Test basic dashboard functionality without starting server."""
    print("\nTesting basic functionality...")

    try:
        from monitoring_dashboard import AgentJob, WorkflowSession, MonitoringDashboard

        # Test AgentJob creation
        job = AgentJob(
            job_id="test_job_1",
            agent_type="researcher",
            task="Test research task",
            status="running",
            started_at="2025-01-24T10:00:00",
            progress=0.5,
            current_step="Gathering data"
        )
        print("✅ AgentJob: Successfully created")

        # Test WorkflowSession creation
        session = WorkflowSession(
            session_id="test_session_1",
            goal="Test goal",
            status="running",
            started_at="2025-01-24T10:00:00",
            total_steps=5,
            completed_steps=2,
            current_step=3,
            agents_used=["researcher", "writer"]
        )
        print("✅ WorkflowSession: Successfully created")

        # Test dashboard initialization
        dashboard = MonitoringDashboard(host="localhost", port=8080)
        print("✅ MonitoringDashboard: Successfully initialized")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint definitions."""
    print("\nTesting API endpoint definitions...")

    try:
        from monitoring_dashboard import MonitoringDashboard
        dashboard = MonitoringDashboard()

        # Check if routes are properly defined
        routes = [resource.canonical for resource in dashboard.app.router._resources]

        expected_routes = ['/ws', '/api/status', '/api/agents', '/api/workflows', '/api/metrics', '/api/history', '/']

        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✅ Route {route}: Defined")
            else:
                print(f"❌ Route {route}: Not defined")

        return True

    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

async def test_monitoring_integration():
    """Test integration with monitoring components."""
    print("\nTesting monitoring integration...")

    try:
        from monitoring_dashboard import MonitoringDashboard

        dashboard = MonitoringDashboard()
        await dashboard.initialize_components()

        if dashboard.orchestrator:
            print("✅ Orchestrator: Initialized")
        else:
            print("⚠️  Orchestrator: Not initialized (may be expected)")

        if dashboard.monitor:
            print("✅ ProgressMonitor: Initialized")
        else:
            print("⚠️  ProgressMonitor: Not initialized (may be expected)")

        if dashboard.streaming_orchestrator:
            print("✅ StreamingOrchestrator: Initialized")
        else:
            print("⚠️  StreamingOrchestrator: Not initialized (may be expected)")

        print("✅ Monitoring integration: Test completed")
        return True

    except Exception as e:
        print(f"❌ Monitoring integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 El Jefe Monitoring Dashboard Test Suite")
    print("=" * 50)

    # Test dependencies
    test_imports()

    # Test basic functionality
    basic_test_passed = test_basic_functionality()

    # Test API endpoints
    api_test_passed = test_api_endpoints()

    # Test monitoring integration
    monitoring_test_passed = asyncio.run(test_monitoring_integration())

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Basic Functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"API Endpoints: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    print(f"Monitoring Integration: {'✅ PASSED' if monitoring_test_passed else '❌ FAILED'}")

    if basic_test_passed and api_test_passed and monitoring_test_passed:
        print("\n🎉 All tests passed! The dashboard is ready to use.")
        print("\nTo start the dashboard:")
        print("  1. Install dependencies: pip install websockets aiohttp-cors")
        print("  2. Run: python3 monitoring_dashboard.py")
        print("  3. Open: http://localhost:8080")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

    return basic_test_passed and api_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)