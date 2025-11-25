"""
Pytest configuration for El Jefe dashboard testing
"""
import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import Mock, AsyncMock

# Add the parent directory to the path to import the main app
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring_dashboard import MonitoringDashboard

# Create a dashboard instance for testing
dashboard = MonitoringDashboard()

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    import hashlib
    import base64

    password = "eljefe_admin"
    timestamp = "2025-01-01T00:00:00Z"
    combined = f"{password}:{timestamp}"
    token = hashlib.sha256(combined.encode()).hexdigest()
    encoded = base64.b64encode(f"eljefe_admin:{token}:{timestamp}".encode()).decode()

    return {'Authorization': f'Basic {encoded}'}

@pytest.fixture
def mock_asyncio_event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing"""
    return {
        "workflows": [
            {
                "id": "test-workflow-1",
                "name": "Feature Development Workflow",
                "type": "feature-development",
                "status": "in_progress",
                "created_at": "2025-01-24T10:00:00Z",
                "updated_at": "2025-01-24T10:30:00Z",
                "progress": 65,
                "estimated_completion": "2025-01-24T12:00:00Z",
                "assigned_agent": "claude-code-expert",
                "description": "Develop user authentication feature"
            },
            {
                "id": "test-workflow-2",
                "name": "Security Audit",
                "type": "security-audit",
                "status": "completed",
                "created_at": "2025-01-24T08:00:00Z",
                "updated_at": "2025-01-24T11:00:00Z",
                "progress": 100,
                "estimated_completion": "2025-01-24T11:00:00Z",
                "assigned_agent": "security-reviewer",
                "description": "Quarterly security assessment"
            }
        ]
    }

@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        "total_workflows": 25,
        "active_workflows": 8,
        "completed_workflows": 17,
        "agent_utilization": {
            "claude-code-expert": 85,
            "security-reviewer": 72,
            "debugger": 60,
            "technical-writer": 45,
            "it-specialist": 30
        },
        "workflow_types": {
            "feature-development": 40,
            "security-audit": 25,
            "documentation-update": 20,
            "debugging-session": 10,
            "deployment-prep": 5
        }
    }

@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing"""
    return {
        "session_id": "test-session-1",
        "messages": [
            {
                "id": "msg-1",
                "type": "user",
                "content": "Start a new security audit workflow",
                "timestamp": "2025-01-24T10:00:00Z"
            },
            {
                "id": "msg-2",
                "type": "assistant",
                "content": "I'll help you start a security audit workflow. Let me detect the requirements and set up the appropriate agents.",
                "timestamp": "2025-01-24T10:00:05Z",
                "workflow_detected": True,
                "workflow_type": "security-audit"
            }
        ],
        "session_created_at": "2025-01-24T10:00:00Z"
    }

@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# WebSocket mock for testing
@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection"""
    mock_ws = Mock()
    mock_ws.send = AsyncMock()
    mock_ws.receive = AsyncMock(return_value=json.dumps({"type": "ping"}))
    mock_ws.accept = AsyncMock()
    return mock_ws

# Performance testing data
@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing"""
    return {
        "api_response_time": 1.0,  # seconds
        "page_load_time": 2.0,     # seconds
        "websocket_latency": 0.5,  # seconds
        "concurrent_users": 100,
        "memory_usage": 512 * 1024 * 1024,  # 512MB
        "cpu_usage": 80  # percentage
    }

# Security testing payloads
@pytest.fixture
def security_test_payloads():
    """Common security test payloads"""
    return {
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onmouseover=alert('xss')",
            "';alert('xss');//"
        ],
        "sql_injection_payloads": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users"
        ],
        "path_traversal_payloads": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd"
        ]
    }

@pytest.fixture
def mock_agent_responses():
    """Mock responses from different agents"""
    return {
        "claude-code-expert": {
            "status": "ready",
            "capabilities": ["code_review", "development", "architecture"],
            "current_tasks": 2,
            "response_time": 0.3
        },
        "security-reviewer": {
            "status": "ready",
            "capabilities": ["security_audit", "vulnerability_assessment", "compliance"],
            "current_tasks": 1,
            "response_time": 0.5
        },
        "debugger": {
            "status": "busy",
            "capabilities": ["testing", "debugging", "performance_analysis"],
            "current_tasks": 3,
            "response_time": 0.8
        }
    }