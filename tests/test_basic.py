"""
Basic tests to verify the testing setup works
"""
import pytest
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import_dashboard():
    """Test that we can import the dashboard"""
    try:
        from monitoring_dashboard import MonitoringDashboard
        assert MonitoringDashboard is not None
        print("✅ Successfully imported MonitoringDashboard")
    except ImportError as e:
        pytest.fail(f"Failed to import dashboard: {e}")

def test_dashboard_instantiation():
    """Test that we can create a dashboard instance"""
    try:
        from monitoring_dashboard import MonitoringDashboard
        dashboard = MonitoringDashboard()
        assert dashboard is not None
        print("✅ Successfully created dashboard instance")
    except Exception as e:
        pytest.fail(f"Failed to create dashboard instance: {e}")

def test_test_configuration():
    """Test that test configuration loads correctly"""
    import json
    config_path = Path(__file__).parent / "test_config.json"

    assert config_path.exists(), f"test_config.json should exist at {config_path}"

    with open(config_path) as f:
        config = json.load(f)

    assert "test_settings" in config
    assert "dashboard_url" in config["test_settings"]
    assert "performance_thresholds" in config
    assert config["test_settings"]["dashboard_url"] == "http://localhost:8080"
    print("✅ Test configuration loaded correctly")

def test_pytest_environment():
    """Test that pytest environment is working"""
    assert True  # Basic sanity check
    print("✅ Pytest environment is working")

if __name__ == "__main__":
    # Run tests manually if executed directly
    test_import_dashboard()
    test_dashboard_instantiation()
    test_test_configuration()
    test_pytest_environment()
    print("\n🎉 All basic tests passed!")