"""
Comprehensive functional tests for El Jefe dashboard
"""
import pytest
import json
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from monitoring_dashboard import app

class TestDashboardAPI:
    """Test dashboard API endpoints"""

    def test_dashboard_index_unauthorized(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_dashboard_index_authorized(self, client, auth_headers):
        """Test dashboard index with authentication"""
        response = client.get('/', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'dashboard_url' in data

    def test_api_workflows_endpoint(self, client, auth_headers, sample_workflow_data):
        """Test workflows API endpoint"""
        with patch('monitoring_dashboard.workflow_sessions', sample_workflow_data['workflows']):
            response = client.get('/api/workflows', headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'workflows' in data
            assert len(data['workflows']) == 2

    def test_api_analytics_endpoint(self, client, auth_headers, sample_analytics_data):
        """Test analytics API endpoint"""
        with patch('monitoring_dashboard.get_analytics_data', return_value=sample_analytics_data):
            response = client.get('/api/analytics', headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'total_workflows' in data
            assert data['total_workflows'] == 25

    def test_api_agents_endpoint(self, client, auth_headers, mock_agent_responses):
        """Test agents API endpoint"""
        with patch('monitoring_dashboard.get_agents_data', return_value=mock_agent_responses):
            response = client.get('/api/agents', headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'agents' in data
            assert len(data['agents']) == 3

    def test_api_chat_endpoint_post(self, client, auth_headers):
        """Test chat message posting"""
        message_data = {
            "message": "Start a security audit",
            "session_id": "test-session"
        }
        response = client.post('/api/chat',
                             json=message_data,
                             headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert 'workflow_detected' in data

    def test_api_workflows_assignment(self, client, auth_headers):
        """Test workflow assignment endpoint"""
        workflow_data = {
            "type": "security-audit",
            "description": "Test security audit",
            "priority": "high"
        }
        response = client.post('/api/workflows/assign',
                             json=workflow_data,
                             headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'workflow_id' in data
        assert 'assigned_agent' in data

class TestDashboardPages:
    """Test dashboard page rendering"""

    def test_dashboard_v2_rendering(self, client, auth_headers):
        """Test dashboard v2 page rendering"""
        response = client.get('/dashboard-v2.html', headers=auth_headers)
        assert response.status_code == 200
        assert b'El Jefe Dashboard' in response.data

    def test_dashboard_charts_rendering(self, client, auth_headers):
        """Test dashboard charts page rendering"""
        response = client.get('/dashboard-charts.html', headers=auth_headers)
        assert response.status_code == 200
        assert b'Chart.js' in response.data

    def test_dashboard_advanced_rendering(self, client, auth_headers):
        """Test dashboard advanced page rendering"""
        response = client.get('/dashboard-advanced.html', headers=auth_headers)
        assert response.status_code == 200
        assert b'Predictive Analytics' in response.data

    def test_simple_dashboard_rendering(self, client, auth_headers):
        """Test simple dashboard page rendering"""
        response = client.get('/dashboard-simple.html', headers=auth_headers)
        assert response.status_code == 200
        assert b'Agent Status' in response.data

class TestWorkflowDetection:
    """Test workflow detection logic"""

    @pytest.mark.asyncio
    async def test_security_audit_detection(self):
        """Test detection of security audit workflows"""
        test_messages = [
            "I need to perform a security review",
            "Can you help with a vulnerability assessment?",
            "We need to audit our authentication system"
        ]

        for message in test_messages:
            workflow_type = await self.detect_workflow_type(message)
            assert workflow_type == "security-audit"

    @pytest.mark.asyncio
    async def test_feature_development_detection(self):
        """Test detection of feature development workflows"""
        test_messages = [
            "I want to add a new feature",
            "Let's implement user authentication",
            "We need to build a new API endpoint"
        ]

        for message in test_messages:
            workflow_type = await self.detect_workflow_type(message)
            assert workflow_type == "feature-development"

    async def detect_workflow_type(self, message):
        """Helper method to detect workflow type"""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ['security', 'audit', 'vulnerability', 'review']):
            return "security-audit"
        elif any(keyword in message_lower for keyword in ['feature', 'implement', 'build', 'add']):
            return "feature-development"
        elif any(keyword in message_lower for keyword in ['debug', 'fix', 'error', 'issue']):
            return "debugging-session"
        elif any(keyword in message_lower for keyword in ['document', 'docs', 'guide', 'manual']):
            return "documentation-update"
        elif any(keyword in message_lower for keyword in ['deploy', 'release', 'production']):
            return "deployment-prep"

        return None

class TestFileUploadFunctionality:
    """Test file upload functionality"""

    def test_file_upload_endpoint(self, client, auth_headers, temp_upload_dir):
        """Test file upload endpoint"""
        test_file_content = b"Test file content for upload"
        test_filename = "test_upload.txt"

        with patch('monitoring_dashboard.UPLOAD_FOLDER', temp_upload_dir):
            response = client.post('/api/upload',
                                 data={'file': (test_file_content, test_filename)},
                                 headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert 'filename' in data

    def test_file_upload_invalid_type(self, client, auth_headers):
        """Test file upload with invalid file type"""
        test_file_content = b"Invalid executable content"
        test_filename = "malicious.exe"

        response = client.post('/api/upload',
                             data={'file': (test_file_content, test_filename)},
                             headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestWebSocketFunctionality:
    """Test WebSocket functionality"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self, mock_websocket):
        """Test WebSocket connection establishment"""
        mock_websocket.accept.assert_called_once()
        assert mock_websocket.send.called

    @pytest.mark.asyncio
    async def test_websocket_message_handling(self, mock_websocket):
        """Test WebSocket message handling"""
        test_message = json.dumps({
            "type": "workflow_update",
            "workflow_id": "test-123",
            "status": "completed"
        })

        mock_websocket.receive.return_value = test_message

        # Simulate message handling
        received_data = json.loads(await mock_websocket.receive())
        assert received_data['type'] == 'workflow_update'
        assert received_data['workflow_id'] == 'test-123'

class TestAuthenticationSecurity:
    """Test authentication and security features"""

    def test_invalid_authentication(self, client):
        """Test authentication with invalid credentials"""
        invalid_headers = {'Authorization': 'Basic invalid_token'}
        response = client.get('/', headers=invalid_headers)
        assert response.status_code == 401

    def test_missing_authentication(self, client):
        """Test access without authentication"""
        response = client.get('/')
        assert response.status_code == 401

    def test_sql_injection_protection(self, client, auth_headers):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE users; --"

        # Test with various endpoints
        endpoints = ['/api/workflows', '/api/analytics', '/api/agents']

        for endpoint in endpoints:
            response = client.get(f'{endpoint}?id={malicious_input}', headers=auth_headers)
            # Should not return 500 (server error)
            assert response.status_code not in [500, 502]

    def test_xss_protection(self, client, auth_headers):
        """Test XSS protection"""
        xss_payload = "<script>alert('xss')</script>"

        response = client.post('/api/chat',
                             json={"message": xss_payload, "session_id": "test"},
                             headers=auth_headers)

        data = json.loads(response.data)
        # Response should not contain unescaped script tags
        assert '<script>' not in data.get('response', '')

class TestPerformanceRequirements:
    """Test performance requirements"""

    def test_api_response_time(self, client, auth_headers):
        """Test API response times meet requirements"""
        import time

        endpoints = ['/api/workflows', '/api/analytics', '/api/agents']

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint, headers=auth_headers)
            end_time = time.time()

            response_time = end_time - start_time
            assert response_time < 1.0  # Should respond within 1 second
            assert response.status_code == 200

    def test_concurrent_requests(self, client, auth_headers):
        """Test handling of concurrent requests"""
        import threading
        import time

        results = []

        def make_request():
            start_time = time.time()
            response = client.get('/api/workflows', headers=auth_headers)
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })

        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert all(result['status_code'] == 200 for result in results)
        # Response times should be reasonable
        assert all(result['response_time'] < 2.0 for result in results)

class TestErrorHandling:
    """Test error handling"""

    def test_404_handling(self, client, auth_headers):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_json_handling(self, client, auth_headers):
        """Test handling of invalid JSON data"""
        response = client.post('/api/chat',
                             data="invalid json",
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400

    def test_missing_required_fields(self, client, auth_headers):
        """Test handling of missing required fields"""
        incomplete_data = {"session_id": "test"}  # Missing 'message' field

        response = client.post('/api/chat',
                             json=incomplete_data,
                             headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestDataValidation:
    """Test data validation"""

    def test_workflow_type_validation(self, client, auth_headers):
        """Test workflow type validation"""
        invalid_workflow_data = {
            "type": "invalid-workflow-type",
            "description": "Test workflow"
        }

        response = client.post('/api/workflows/assign',
                             json=invalid_workflow_data,
                             headers=auth_headers)
        assert response.status_code == 400

    def test_message_content_validation(self, client, auth_headers):
        """Test chat message content validation"""
        # Test empty message
        response = client.post('/api/chat',
                             json={"message": "", "session_id": "test"},
                             headers=auth_headers)
        assert response.status_code == 400

        # Test overly long message
        long_message = "a" * 10001  # Assuming max length is 10000
        response = client.post('/api/chat',
                             json={"message": long_message, "session_id": "test"},
                             headers=auth_headers)
        assert response.status_code == 400

# Integration tests
class TestDashboardIntegration:
    """Integration tests for dashboard components"""

    def test_full_workflow_lifecycle(self, client, auth_headers):
        """Test complete workflow from assignment to completion"""
        # 1. Assign a new workflow
        workflow_data = {
            "type": "security-audit",
            "description": "Integration test security audit",
            "priority": "medium"
        }

        response = client.post('/api/workflows/assign',
                             json=workflow_data,
                             headers=auth_headers)
        assert response.status_code == 200
        assign_data = json.loads(response.data)
        workflow_id = assign_data['workflow_id']

        # 2. Check workflow appears in list
        response = client.get('/api/workflows', headers=auth_headers)
        assert response.status_code == 200
        workflows_data = json.loads(response.data)
        workflow_ids = [w['id'] for w in workflows_data['workflows']]
        assert workflow_id in workflow_ids

        # 3. Update workflow status
        update_data = {
            "status": "completed",
            "progress": 100
        }

        response = client.put(f'/api/workflows/{workflow_id}',
                            json=update_data,
                            headers=auth_headers)
        assert response.status_code == 200

    def test_chat_workflow_integration(self, client, auth_headers):
        """Test chat integration with workflow system"""
        # 1. Send chat message that should trigger workflow detection
        chat_data = {
            "message": "I need to perform a security audit of our authentication system",
            "session_id": "integration-test-session"
        }

        response = client.post('/api/chat',
                             json=chat_data,
                             headers=auth_headers)
        assert response.status_code == 200
        chat_response = json.loads(response.data)

        # 2. Verify workflow was detected
        assert chat_response.get('workflow_detected') == True
        assert chat_response.get('workflow_type') == 'security-audit'

        # 3. Verify workflow was created
        if 'workflow_id' in chat_response:
            workflow_id = chat_response['workflow_id']
            response = client.get('/api/workflows', headers=auth_headers)
            workflows_data = json.loads(response.data)
            workflow_ids = [w['id'] for w in workflows_data['workflows']]
            assert workflow_id in workflow_ids

if __name__ == '__main__':
    pytest.main([__file__, '-v'])