"""
Locust load testing file for El Jefe dashboard with proper authentication
"""
from locust import HttpUser, task, between
import json
import random
import time
from datetime import datetime, timezone

class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts"""
        # Authenticate with dynamic timestamp
        self.login()
        # Store user session info
        self.user_id = f"user_{random.randint(1000, 9999)}"

    def login(self):
        """Login to get authentication token with dynamic timestamp"""
        import hashlib
        import base64

        password = "eljefe_admin"
        # Use current timestamp for realistic authentication
        timestamp = datetime.now(timezone.utc).isoformat()
        combined = f"{password}:{timestamp}"
        token = hashlib.sha256(combined.encode()).hexdigest()
        encoded = base64.b64encode(f"eljefe_admin:{token}:{timestamp}".encode()).decode()

        self.client.headers.update({
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json',
            'User-Agent': f'Locust-LoadTest-{self.user_id}'
        })

        # Store authentication info for potential refresh
        self.auth_timestamp = timestamp
        self.auth_token = token

    @task(3)
    def view_dashboard(self):
        """View main dashboard"""
        self.client.get("/")

    @task(2)
    def view_analytics(self):
        """View analytics data"""
        self.client.get("/api/analytics")

    @task(2)
    def view_workflows(self):
        """View workflows list"""
        self.client.get("/api/workflows")

    @task(1)
    def view_agents(self):
        """View agent status"""
        self.client.get("/api/agents")

    @task(3)
    def send_chat_message(self):
        """Send chat messages"""
        messages = [
            "I need help with a security audit",
            "Can you help me implement a new feature?",
            "I found a bug that needs fixing",
            "We need to update the documentation",
            "Prepare for deployment"
        ]

        message = random.choice(messages)
        session_id = f"session-{random.randint(1000, 9999)}"

        payload = {
            "message": message,
            "session_id": session_id
        }

        self.client.post("/api/chat", json=payload)

    @task(1)
    def assign_workflow(self):
        """Assign new workflows"""
        workflow_types = ["feature-development", "security-audit", "documentation-update", "debugging-session"]

        payload = {
            "type": random.choice(workflow_types),
            "description": f"Test workflow {random.randint(1, 100)}",
            "priority": random.choice(["low", "medium", "high"])
        }

        self.client.post("/api/workflows/assign", json=payload)

    @task(1)
    def view_dashboard_pages(self):
        """View different dashboard versions"""
        pages = [
            "/dashboard-v2.html",
            "/dashboard-charts.html",
            "/dashboard-advanced.html",
            "/dashboard-simple.html"
        ]

        page = random.choice(pages)
        self.client.get(page)

    @task(1)
    def upload_file(self):
        """Simulate file upload (mock)"""
        # Note: This would require actual file data in real testing
        payload = {
            "filename": f"test_file_{random.randint(1, 100)}.txt",
            "content": "Test file content"
        }

        # Mock file upload endpoint
        self.client.post("/api/upload/mock", json=payload)

    def refresh_auth_if_needed(self):
        """Refresh authentication if it's too old (5+ minutes)"""
        current_time = datetime.now(timezone.utc)
        auth_time = datetime.fromisoformat(self.auth_timestamp.replace('Z', '+00:00'))

        # Refresh if auth is older than 5 minutes
        if (current_time - auth_time).total_seconds() > 300:
            self.login()

    @task(5)
    def heartbeat_request(self):
        """Lightweight heartbeat request to keep session alive"""
        self.refresh_auth_if_needed()
        self.client.get("/api/status")

    @task(1)
    def check_health(self):
        """Check system health endpoint"""
        self.refresh_auth_if_needed()
        self.client.get("/health")

class AdminUser(DashboardUser):
    """Admin user with higher privileges"""
    wait_time = between(0.5, 2)

    def login(self):
        """Admin login with enhanced credentials"""
        import hashlib
        import base64

        password = "eljefe_admin"  # Admin password
        timestamp = datetime.now(timezone.utc).isoformat()
        combined = f"{password}:{timestamp}"
        token = hashlib.sha256(combined.encode()).hexdigest()
        encoded = base64.b64encode(f"eljefe_admin:{token}:{timestamp}".encode()).decode()

        self.client.headers.update({
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json',
            'User-Agent': f'Locust-Admin-{self.user_id}',
            'X-User-Role': 'admin'
        })

        self.auth_timestamp = timestamp
        self.auth_token = token

    @task(2)
    def view_logs(self):
        """View system logs"""
        self.refresh_auth_if_needed()
        self.client.get("/api/logs")

    @task(1)
    def view_debug_info(self):
        """View debug information"""
        self.refresh_auth_if_needed()
        self.client.get("/api/debug")

    @task(3)
    def admin_system_status(self):
        """Check detailed system status"""
        self.refresh_auth_if_needed()
        self.client.get("/api/admin/status")

class MobileUser(DashboardUser):
    """Mobile user simulation"""
    wait_time = between(2, 5)  # Slower interaction time

    def on_start(self):
        """Mobile user login"""
        super().on_start()
        # Set mobile user agent
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })

    @task(5)
    def view_dashboard_mobile(self):
        """Mobile users view dashboard more frequently"""
        self.client.get("/dashboard-v2.html")

    @task(2)
    def use_chat_mobile(self):
        """Mobile users chat frequently"""
        messages = [
            "Quick security check",
            "Status update",
            "Help needed",
            "Urgent issue"
        ]

        message = random.choice(messages)
        session_id = f"mobile-session-{random.randint(1000, 9999)}"

        payload = {
            "message": message,
            "session_id": session_id,
            "user_agent": "mobile"
        }

        self.client.post("/api/chat", json=payload)

    @task(3)
    def check_analytics_mobile(self):
        """Check analytics on mobile"""
        self.client.get("/api/analytics")


class APIKeyUser(HttpUser):
    """User using API key authentication instead of Basic auth"""
    wait_time = between(1, 4)

    def on_start(self):
        """Initialize API key authentication"""
        self.setup_api_key_auth()
        self.user_id = f"api_user_{random.randint(1000, 9999)}"

    def setup_api_key_auth(self):
        """Setup API key based authentication"""
        import hashlib
        import secrets

        # Generate a unique API key for this test user
        api_key = f"test_key_{secrets.token_hex(16)}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create signature for API key authentication
        signature_data = f"{api_key}:{timestamp}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()

        self.client.headers.update({
            'Authorization': f'Bearer {api_key}',
            'X-Signature': signature,
            'X-Timestamp': timestamp,
            'Content-Type': 'application/json',
            'User-Agent': f'API-Client-{self.user_id}'
        })

        self.api_key = api_key
        self.api_timestamp = timestamp
        self.api_signature = signature

    @task(4)
    def api_get_agents(self):
        """Get agents via API"""
        self.client.get("/api/agents")

    @task(3)
    def api_get_workflows(self):
        """Get workflows via API"""
        self.client.get("/api/workflows")

    @task(2)
    def api_get_analytics(self):
        """Get analytics via API"""
        self.client.get("/api/analytics")

    @task(1)
    def api_create_workflow(self):
        """Create workflow via API"""
        workflow_data = {
            "type": "api-test-workflow",
            "description": f"API generated workflow {random.randint(1, 1000)}",
            "priority": "medium",
            "source": "api_test"
        }

        self.client.post("/api/workflows", json=workflow_data)

    def refresh_api_key_auth(self):
        """Refresh API key authentication if needed"""
        current_time = datetime.now(timezone.utc)
        api_time = datetime.fromisoformat(self.api_timestamp.replace('Z', '+00:00'))

        # Refresh API auth if older than 10 minutes
        if (current_time - api_time).total_seconds() > 600:
            self.setup_api_key_auth()