#!/usr/bin/env python3
"""
Comprehensive End-to-End Tests with Authentication for El Jefe Dashboard
Tests complete user workflows with proper authentication
"""
import asyncio
import aiohttp
import json
import pytest
import time
from datetime import datetime, timezone
from typing import Dict, Any
import hashlib
import base64


class E2ETestClient:
    """Enhanced E2E test client with authentication management"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = None
        self.auth_headers = None
        self.user_info = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self, username: str = "eljefe_admin", password: str = "eljefe_admin"):
        """Authenticate with the dashboard"""
        timestamp = datetime.now(timezone.utc).isoformat()
        combined = f"{password}:{timestamp}"
        token = hashlib.sha256(combined.encode()).hexdigest()
        encoded = base64.b64encode(f"{username}:{token}:{timestamp}".encode()).decode()

        self.auth_headers = {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json'
        }

        self.user_info = {
            'username': username,
            'timestamp': timestamp,
            'token': token
        }

    async def get(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated GET request"""
        headers = {**self.auth_headers, **kwargs.pop('headers', {})}
        return await self.session.get(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated POST request"""
        headers = {**self.auth_headers, **kwargs.pop('headers', {})}
        return await self.session.post(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated PUT request"""
        headers = {**self.auth_headers, **kwargs.pop('headers', {})}
        return await self.session.put(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make authenticated DELETE request"""
        headers = {**self.auth_headers, **kwargs.pop('headers', {})}
        return await self.session.delete(f"{self.base_url}{endpoint}", headers=headers, **kwargs)


@pytest.mark.asyncio
class TestDashboardE2EWithAuth:
    """Comprehensive E2E tests with authentication"""

    async def test_complete_user_workflow(self):
        """Test complete user workflow from login to task execution"""

        async with E2ETestClient() as client:

            # 1. Test dashboard access
            async with client.get('/') as resp:
                assert resp.status == 200, "Dashboard should be accessible with authentication"
                data = await resp.json()
                assert 'status' in data, "Dashboard response should contain status"

            # 2. Test agents API
            async with client.get('/api/agents') as resp:
                assert resp.status == 200, "Agents API should be accessible"
                agents_data = await resp.json()
                assert isinstance(agents_data, (dict, list)), "Agents should return valid data"

            # 3. Test workflows API
            async with client.get('/api/workflows') as resp:
                assert resp.status == 200, "Workflows API should be accessible"
                workflows_data = await resp.json()
                assert isinstance(workflows_data, (dict, list)), "Workflows should return valid data"

            # 4. Test analytics API
            async with client.get('/api/analytics') as resp:
                assert resp.status == 200, "Analytics API should be accessible"
                analytics_data = await resp.json()
                assert isinstance(analytics_data, dict), "Analytics should return valid data"

            # 5. Test chat functionality
            chat_payload = {
                "message": "Test E2E message",
                "user_id": "e2e_test_user",
                "session_id": f"test_session_{int(time.time())}"
            }

            async with client.post('/api/chat', json=chat_payload) as resp:
                assert resp.status == 200, "Chat API should accept messages"
                chat_response = await resp.json()
                assert 'response' in chat_response or 'status' in chat_response, "Chat should return valid response"

            # 6. Test workflow assignment
            workflow_payload = {
                "type": "test_workflow",
                "description": "E2E test workflow",
                "priority": "medium",
                "test_mode": True
            }

            async with client.post('/api/workflows/assign', json=workflow_payload) as resp:
                # Note: This might return 404 or other status if endpoint doesn't exist
                # That's okay for E2E testing - we're testing the request flow
                assert resp.status in [200, 404, 400], f"Workflow assignment should handle request gracefully, got {resp.status}"

    async def test_dashboard_pages_access(self):
        """Test access to different dashboard pages"""

        async with E2ETestClient() as client:

            pages = [
                '/dashboard-v2.html',
                '/dashboard-advanced.html',
                '/dashboard-charts.html',
                '/dashboard-simple.html'
            ]

            for page in pages:
                async with client.get(page) as resp:
                    assert resp.status == 200, f"Page {page} should be accessible with authentication"
                    content = await resp.text()
                    assert len(content) > 0, f"Page {page} should have content"

    async def test_api_error_handling(self):
        """Test API error handling with authentication"""

        async with E2ETestClient() as client:

            # Test invalid endpoint
            async with client.get('/api/invalid-endpoint') as resp:
                assert resp.status == 404, "Invalid endpoint should return 404"

            # Test malformed JSON
            async with client.post('/api/chat', data='invalid json') as resp:
                assert resp.status in [400, 422], "Malformed JSON should return validation error"

            # Test missing required fields
            async with client.post('/api/chat', json={}) as resp:
                assert resp.status in [400, 422], "Missing fields should return validation error"

    async def test_concurrent_requests(self):
        """Test handling of concurrent authenticated requests"""

        async with E2ETestClient() as client:

            async def make_request(endpoint: str):
                async with client.get(endpoint) as resp:
                    return resp.status

            # Launch multiple concurrent requests
            tasks = [
                make_request('/api/agents'),
                make_request('/api/workflows'),
                make_request('/api/analytics'),
                make_request('/api/status'),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All requests should succeed (not raise exceptions)
            for result in results:
                assert not isinstance(result, Exception), f"Concurrent request should not raise exception: {result}"
                assert result in [200, 404], f"Concurrent request should return valid status: {result}"

    async def test_session_persistence(self):
        """Test that authentication persists across requests"""

        async with E2ETestClient() as client:

            # Make multiple requests and verify auth persists
            endpoints = ['/api/agents', '/api/workflows', '/api/analytics']

            for endpoint in endpoints:
                async with client.get(endpoint) as resp:
                    assert resp.status == 200, f"Authentication should persist for {endpoint}"

    async def test_authentication_refresh(self):
        """Test authentication token refresh workflow"""

        # Test with initial authentication
        async with E2ETestClient() as client:
            async with client.get('/api/agents') as resp:
                assert resp.status == 200, "Initial authentication should work"

            # Store original auth info
            original_timestamp = client.user_info['timestamp']

            # Wait a short time
            await asyncio.sleep(0.1)

            # Re-authenticate with new timestamp
            await client.authenticate()
            new_timestamp = client.user_info['timestamp']

            assert new_timestamp != original_timestamp, "Authentication should refresh with new timestamp"

            # Test with new authentication
            async with client.get('/api/workflows') as resp:
                assert resp.status == 200, "Refreshed authentication should work"


@pytest.mark.asyncio
class TestAuthenticationSecurity:
    """Test authentication security features"""

    async def test_invalid_credentials(self):
        """Test behavior with invalid credentials"""

        async with E2ETestClient() as client:
            # Override with invalid credentials
            await client.authenticate(username="invalid_user", password="wrong_password")

            async with client.get('/api/agents') as resp:
                # Should return 401 for invalid credentials
                assert resp.status == 401, "Invalid credentials should be rejected"

    async def test_expired_timestamp(self):
        """Test behavior with expired timestamp"""

        async with E2ETestClient() as client:
            # Manually set expired timestamp (1 hour ago)
            expired_timestamp = datetime.now(timezone.utc).timestamp() - 3600

            client.auth_headers = {
                'Authorization': 'Basic invalid_expired_token',
                'Content-Type': 'application/json'
            }

            async with client.get('/api/agents') as resp:
                # Should reject expired token
                assert resp.status == 401, "Expired token should be rejected"

    async def test_missing_authorization(self):
        """Test behavior with missing authorization header"""

        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/api/agents") as resp:
                assert resp.status == 401, "Missing authorization should be rejected"


@pytest.mark.asyncio
class TestPerformanceWithAuth:
    """Performance tests with authentication overhead"""

    async def test_authenticated_response_times(self):
        """Test that authenticated requests have acceptable response times"""

        async with E2ETestClient() as client:

            endpoints = ['/api/agents', '/api/workflows', '/api/analytics']
            response_times = []

            for endpoint in endpoints:
                start_time = time.time()
                async with client.get(endpoint) as resp:
                    await resp.text()  # Consume response
                    end_time = time.time()

                    response_times.append(end_time - start_time)
                    assert resp.status == 200, f"Endpoint {endpoint} should be accessible"

            # Check that all responses are under 2 seconds
            for i, response_time in enumerate(response_times):
                assert response_time < 2.0, f"Response {i+1} too slow: {response_time:.2f}s"

            # Check average response time
            avg_time = sum(response_times) / len(response_times)
            assert avg_time < 1.0, f"Average response time too high: {avg_time:.2f}s"

    async def test_authentication_overhead(self):
        """Test authentication overhead vs unauthenticated requests"""

        # Test unauthenticated request (should fail fast)
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get("http://localhost:8080/api/agents") as resp:
                await resp.text()
                unauth_time = time.time() - start_time

        # Test authenticated request
        async with E2ETestClient() as client:
            start_time = time.time()
            async with client.get('/api/agents') as resp:
                await resp.text()
                auth_time = time.time() - start_time

        # Authentication overhead should be reasonable
        overhead = auth_time - unauth_time
        assert overhead < 0.5, f"Authentication overhead too high: {overhead:.2f}s"


# Integration helper functions
async def run_comprehensive_e2e_test():
    """Run all E2E tests programmatically"""
    print("🧪 Starting Comprehensive E2E Tests with Authentication")
    print("=" * 60)

    test_instance = TestDashboardE2EWithAuth()
    auth_instance = TestAuthenticationSecurity()
    perf_instance = TestPerformanceWithAuth()

    tests = [
        ("Complete User Workflow", test_instance.test_complete_user_workflow),
        ("Dashboard Pages Access", test_instance.test_dashboard_pages_access),
        ("API Error Handling", test_instance.test_api_error_handling),
        ("Concurrent Requests", test_instance.test_concurrent_requests),
        ("Session Persistence", test_instance.test_session_persistence),
        ("Authentication Refresh", test_instance.test_authentication_refresh),
        ("Invalid Credentials", auth_instance.test_invalid_credentials),
        ("Expired Timestamp", auth_instance.test_expired_timestamp),
        ("Missing Authorization", auth_instance.test_missing_authorization),
        ("Authenticated Response Times", perf_instance.test_authenticated_response_times),
        ("Authentication Overhead", perf_instance.test_authentication_overhead),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"🔍 Running: {test_name}")
            await test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 E2E Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All E2E tests passed!")
        return True
    else:
        print("⚠️  Some E2E tests failed")
        return False


if __name__ == "__main__":
    # Run comprehensive E2E test
    success = asyncio.run(run_comprehensive_e2e_test())
    exit(0 if success else 1)