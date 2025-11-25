"""
Locust load testing file for El Jefe dashboard
"""
from locust import HttpUser, task, between
import json
import random

class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts"""
        # Authenticate
        self.login()

    def login(self):
        """Login to get authentication token"""
        import hashlib
        import base64

        password = "eljefe_admin"
        timestamp = "2025-01-01T00:00:00Z"
        combined = f"{password}:{timestamp}"
        token = hashlib.sha256(combined.encode()).hexdigest()
        encoded = base64.b64encode(f"eljefe_admin:{token}:{timestamp}".encode()).decode()

        self.client.headers.update({
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json'
        })

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

class AdminUser(DashboardUser):
    """Admin user with higher privileges"""
    wait_time = between(0.5, 2)

    @task(2)
    def view_logs(self):
        """View system logs"""
        self.client.get("/api/logs")

    @task(1)
    def view_debug_info(self):
        """View debug information"""
        self.client.get("/api/debug")

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
            "session_id": session_id
        }

        self.client.post("/api/chat", json=payload)