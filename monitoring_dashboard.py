#!/usr/bin/env python3
"""
Monitoring Dashboard for El Jefe Agents

Provides real-time monitoring of agent jobs, status, and completion.
Runs as a web server with WebSocket support for live updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import websockets
import aiofiles
from aiohttp import web, WSMsgType
import aiohttp_cors
from dataclasses import dataclass, asdict

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.orchestrator import Orchestrator
    from src.streaming_orchestrator import StreamingOrchestrator
    from src.monitoring import ProgressMonitor
    from src.scheduler import WorkflowScheduler
    from src.shared_monitoring_state import get_shared_monitoring_state
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    Orchestrator = None
    StreamingOrchestrator = None
    ProgressMonitor = None
    WorkflowScheduler = None
    get_shared_monitoring_state = None


@dataclass
class AgentJob:
    """Represents an agent job with status tracking."""
    job_id: str
    agent_type: str
    task: str
    status: str  # 'running', 'completed', 'failed', 'paused'
    started_at: str
    completed_at: Optional[str] = None
    progress: float = 0.0
    current_step: str = ""
    workspace: str = ""
    error_message: Optional[str] = None
    tokens_used: int = 0
    words_generated: int = 0


@dataclass
class WorkflowSession:
    """Represents a complete workflow session."""
    session_id: str
    goal: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    total_steps: int = 0
    completed_steps: int = 0
    current_step: int = 0
    agents_used: List[str] = None
    workspace: str = ""
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.agents_used is None:
            self.agents_used = []
        if self.metrics is None:
            self.metrics = {}


class MonitoringDashboard:
    """Main monitoring dashboard server."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.clients = set()
        self.agent_jobs: Dict[str, AgentJob] = {}
        self.workflow_sessions: Dict[str, WorkflowSession] = {}

        # Initialize monitoring components
        self.orchestrator = None
        self.streaming_orchestrator = None
        self.monitor = None
        self.scheduler = None

        # Setup routes and CORS
        self.setup_routes()
        self.setup_cors()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_cors(self):
        """Setup CORS for all routes."""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    def setup_routes(self):
        """Setup HTTP and WebSocket routes."""
        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)

        # API endpoints
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/agents', self.get_agents)
        self.app.router.add_get('/api/workflows', self.get_workflows)
        self.app.router.add_get('/api/metrics', self.get_metrics)
        self.app.router.add_get('/api/history', self.get_history)

        # Serve static files
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_static('/', path='static/', name='static')

    async def initialize_components(self):
        """Initialize monitoring components."""
        try:
            if Orchestrator is not None:
                self.orchestrator = Orchestrator(base_dir="workspaces", interactive=False)

            if StreamingOrchestrator is not None:
                self.streaming_orchestrator = StreamingOrchestrator(
                    base_dir="workspaces",
                    enable_monitoring=True,
                    enable_streaming=True
                )

            if ProgressMonitor is not None:
                self.monitor = ProgressMonitor()
                self.monitor.start_monitoring()

            if WorkflowScheduler is not None:
                from pathlib import Path
                scheduler_path = Path("workspaces") / "scheduler"
                scheduler_path.mkdir(parents=True, exist_ok=True)
                self.scheduler = WorkflowScheduler(scheduler_path)
                await self.scheduler.load_scheduled_workflows()

            # Load monitoring state file
            await self._load_monitoring_state()

            self.logger.info("Monitoring components initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")

    async def _load_monitoring_state(self):
        """Load monitoring state from file."""
        try:
            state_file = Path("monitoring_state.json")
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)

                # Convert to internal data structures
                for job_id, job_data in state_data.get("agent_jobs", {}).items():
                    job = AgentJob(
                        job_id=job_data["job_id"],
                        agent_type=job_data["agent_type"],
                        task=job_data["task"],
                        status=job_data["status"],
                        started_at=job_data["started_at"],
                        completed_at=job_data.get("completed_at"),
                        progress=job_data.get("progress", 0.0),
                        current_step=job_data.get("current_step", ""),
                        workspace=job_data.get("workspace", ""),
                        tokens_used=job_data.get("tokens_used", 0),
                        words_generated=job_data.get("words_generated", 0)
                    )
                    self.agent_jobs[job_id] = job

                for session_id, session_data in state_data.get("workflow_sessions", {}).items():
                    session = WorkflowSession(
                        session_id=session_data["session_id"],
                        goal=session_data["goal"],
                        status=session_data["status"],
                        started_at=session_data["started_at"],
                        completed_at=session_data.get("completed_at"),
                        total_steps=session_data.get("total_steps", 0),
                        completed_steps=session_data.get("completed_steps", 0),
                        current_step=session_data.get("current_step", 0),
                        agents_used=session_data.get("agents_used", []),
                        workspace=session_data.get("workspace", ""),
                        metrics=session_data.get("metrics", {})
                    )
                    self.workflow_sessions[session_id] = session

                self.logger.info(f"Loaded {len(self.workflow_sessions)} workflows and {len(self.agent_jobs)} agent jobs from state file")

        except Exception as e:
            self.logger.error(f"Failed to load monitoring state: {e}")

    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.clients.add(ws)
        self.logger.info(f"New WebSocket client connected: {len(self.clients)} total")

        try:
            # Send initial data
            await self.send_to_client(ws, {
                "type": "initial_data",
                "agents": {job_id: asdict(job) for job_id, job in self.agent_jobs.items()},
                "workflows": {session_id: asdict(session) for session_id, session in self.workflow_sessions.items()}
            })

            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_client_message(ws, data)
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')

        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.clients.discard(ws)
            self.logger.info(f"WebSocket client disconnected: {len(self.clients)} remaining")

        return ws

    async def handle_client_message(self, ws, data):
        """Handle messages from WebSocket clients."""
        message_type = data.get("type")

        if message_type == "refresh":
            await self.send_to_client(ws, await self.get_current_status())
        elif message_type == "interrupt_workflow":
            session_id = data.get("session_id")
            await self.interrupt_workflow(session_id)
        elif message_type == "pause_workflow":
            session_id = data.get("session_id")
            await self.pause_workflow(session_id)
        elif message_type == "resume_workflow":
            session_id = data.get("session_id")
            await self.resume_workflow(session_id)

    async def send_to_client(self, ws, data):
        """Send data to a specific WebSocket client."""
        try:
            await ws.send_str(json.dumps(data))
        except Exception as e:
            self.logger.error(f"Error sending to client: {e}")
            self.clients.discard(ws)

    async def broadcast_to_clients(self, data):
        """Broadcast data to all connected WebSocket clients."""
        if not self.clients:
            return

        # Create a copy of clients to avoid modification during iteration
        clients_copy = self.clients.copy()
        for ws in clients_copy:
            try:
                await ws.send_str(json.dumps(data))
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {e}")
                self.clients.discard(ws)

    async def update_agent_job(self, job_data: Dict[str, Any]):
        """Update or create an agent job."""
        job_id = job_data["job_id"]

        if job_id in self.agent_jobs:
            # Update existing job
            for key, value in job_data.items():
                if hasattr(self.agent_jobs[job_id], key):
                    setattr(self.agent_jobs[job_id], key, value)
        else:
            # Create new job
            self.agent_jobs[job_id] = AgentJob(**job_data)

        # Broadcast update
        await self.broadcast_to_clients({
            "type": "agent_update",
            "job": asdict(self.agent_jobs[job_id])
        })

    async def update_workflow_session(self, session_data: Dict[str, Any]):
        """Update or create a workflow session."""
        session_id = session_data["session_id"]

        if session_id in self.workflow_sessions:
            # Update existing session
            for key, value in session_data.items():
                if hasattr(self.workflow_sessions[session_id], key):
                    setattr(self.workflow_sessions[session_id], key, value)
        else:
            # Create new session
            self.workflow_sessions[session_id] = WorkflowSession(**session_data)

        # Broadcast update
        await self.broadcast_to_clients({
            "type": "workflow_update",
            "session": asdict(self.workflow_sessions[session_id])
        })

    # API Handlers
    async def get_status(self, request):
        """Get overall system status."""
        # Use shared state if available
        if get_shared_monitoring_state:
            status = get_shared_monitoring_state().get_system_status()
            status["system"]["connected_clients"] = len(self.clients)
            return web.json_response(status)
        else:
            # Fallback to internal state
            status = {
                "system": {
                    "status": "running",
                    "uptime": "active",
                    "active_agents": len(self.agent_jobs),
                    "active_workflows": len(self.workflow_sessions),
                    "connected_clients": len(self.clients)
                },
                "agents": {job_id: asdict(job) for job_id, job in self.agent_jobs.items()},
                "workflows": {session_id: asdict(session) for session_id, session in self.workflow_sessions.items()}
            }
            return web.json_response(status)

    async def get_agents(self, request):
        """Get all agent jobs."""
        try:
            # First try to load from monitoring state file directly
            state_file = Path("monitoring_state.json")
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                return web.json_response(state_data.get("agent_jobs", {}))
        except Exception as e:
            self.logger.error(f"Error reading agents from state file: {e}")

        # Fallback to internal state
        agents = {job_id: asdict(job) for job_id, job in self.agent_jobs.items()}
        return web.json_response(agents)

    async def get_workflows(self, request):
        """Get all workflow sessions."""
        try:
            # First try to load from monitoring state file directly
            state_file = Path("monitoring_state.json")
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                return web.json_response(state_data.get("workflow_sessions", {}))
        except Exception as e:
            self.logger.error(f"Error reading workflows from state file: {e}")

        # Fallback to internal state
        workflows = {session_id: asdict(session) for session_id, session in self.workflow_sessions.items()}
        return web.json_response(workflows)

    async def get_metrics(self, request):
        """Get system metrics."""
        if get_shared_monitoring_state:
            metrics = get_shared_monitoring_state().get_metrics()
            metrics["average_completion_time"] = self.calculate_avg_completion_time()
            return web.json_response(metrics)
        else:
            metrics = {
                "total_jobs": len(self.agent_jobs),
                "completed_jobs": len([j for j in self.agent_jobs.values() if j.status == "completed"]),
                "failed_jobs": len([j for j in self.agent_jobs.values() if j.status == "failed"]),
                "running_jobs": len([j for j in self.agent_jobs.values() if j.status == "running"]),
                "total_workflows": len(self.workflow_sessions),
                "completed_workflows": len([w for w in self.workflow_sessions.values() if w.status == "completed"]),
                "total_tokens": sum(job.tokens_used for job in self.agent_jobs.values()),
                "total_words": sum(job.words_generated for job in self.agent_jobs.values()),
                "average_completion_time": self.calculate_avg_completion_time()
            }
            return web.json_response(metrics)

    async def get_history(self, request):
        """Get historical data."""
        limit = int(request.query.get("limit", 50))

        # Get recent workspaces from orchestrator
        history = []
        if self.orchestrator:
            try:
                workspaces = await self.orchestrator.list_workspaces(limit)
                history = workspaces
            except Exception as e:
                self.logger.error(f"Error getting history: {e}")

        return web.json_response({"history": history, "limit": limit})

    async def serve_index(self, request):
        """Serve the main dashboard HTML page."""
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            # Return a basic HTML page if static files don't exist
            return web.Response(text=self.get_basic_html(), content_type="text/html")

    def get_basic_html(self) -> str:
        """Get a basic HTML page for the dashboard."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>El Jefe - Agent Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .status-running { color: #27ae60; }
        .status-completed { color: #3498db; }
        .status-failed { color: #e74c3c; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .metric { text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; }
        .connections { float: right; background: #27ae60; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 El Jefe Agent Monitoring Dashboard</h1>
            <div class="connections" id="connections">🟢 Connected</div>
        </div>

        <div class="metrics">
            <div class="card metric">
                <div class="metric-value" id="active-agents">0</div>
                <div>Active Agents</div>
            </div>
            <div class="card metric">
                <div class="metric-value" id="active-workflows">0</div>
                <div>Active Workflows</div>
            </div>
            <div class="card metric">
                <div class="metric-value" id="completed-jobs">0</div>
                <div>Completed Jobs</div>
            </div>
            <div class="card metric">
                <div class="metric-value" id="total-tokens">0</div>
                <div>Total Tokens</div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 Active Agents</h2>
            <div id="agents-list">No active agents</div>
        </div>

        <div class="card">
            <h2>📋 Workflow Sessions</h2>
            <div id="workflows-list">No active workflows</div>
        </div>

        <div class="card">
            <h2>📊 System Status</h2>
            <div id="system-status">Loading...</div>
        </div>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:8080/ws');
        const connectionsEl = document.getElementById('connections');

        ws.onopen = function() {
            connectionsEl.textContent = '🟢 Connected';
            connectionsEl.style.background = '#27ae60';
        };

        ws.onclose = function() {
            connectionsEl.textContent = '🔴 Disconnected';
            connectionsEl.style.background = '#e74c3c';
            // Try to reconnect every 5 seconds
            setTimeout(() => location.reload(), 5000);
        };

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            handleUpdate(data);
        };

        function handleUpdate(data) {
            console.log('Received update:', data);

            if (data.type === 'agent_update') {
                updateAgentsList();
            } else if (data.type === 'workflow_update') {
                updateWorkflowsList();
            } else if (data.type === 'initial_data') {
                updateAllData();
            }
        }

        function updateAllData() {
            fetch('/api/status').then(r => r.json()).then(data => {
                updateMetrics(data);
                updateAgentsList();
                updateWorkflowsList();
                updateSystemStatus(data.system);
            });
        }

        function updateMetrics(data) {
            document.getElementById('active-agents').textContent = data.system.active_agents;
            document.getElementById('active-workflows').textContent = data.system.active_workflows;

            fetch('/api/metrics').then(r => r.json()).then(metrics => {
                document.getElementById('completed-jobs').textContent = metrics.completed_jobs;
                document.getElementById('total-tokens').textContent = metrics.total_tokens.toLocaleString();
            });
        }

        function updateAgentsList() {
            fetch('/api/agents').then(r => r.json()).then(agents => {
                const listEl = document.getElementById('agents-list');
                const agentsArray = Object.values(agents);

                if (agentsArray.length === 0) {
                    listEl.innerHTML = 'No active agents';
                    return;
                }

                listEl.innerHTML = agentsArray.map(agent => `
                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                        <strong>${agent.agent_type}</strong> - ${agent.job_id}
                        <span class="status-${agent.status}">${agent.status}</span>
                        <br><small>Task: ${agent.task}</small>
                        <br><small>Progress: ${Math.round(agent.progress * 100)}%</small>
                    </div>
                `).join('');
            });
        }

        function updateWorkflowsList() {
            fetch('/api/workflows').then(r => r.json()).then(workflows => {
                const listEl = document.getElementById('workflows-list');
                const workflowsArray = Object.values(workflows);

                if (workflowsArray.length === 0) {
                    listEl.innerHTML = 'No active workflows';
                    return;
                }

                listEl.innerHTML = workflowsArray.map(workflow => `
                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                        <strong>${workflow.goal}</strong> - ${workflow.session_id}
                        <span class="status-${workflow.status}">${workflow.status}</span>
                        <br><small>Steps: ${workflow.completed_steps}/${workflow.total_steps}</small>
                        <br><small>Agents: ${workflow.agents_used.join(', ')}</small>
                    </div>
                `).join('');
            });
        }

        function updateSystemStatus(system) {
            document.getElementById('system-status').innerHTML = `
                <p><strong>Status:</strong> ${system.status}</p>
                <p><strong>Connected Clients:</strong> ${system.connected_clients}</p>
                <p><strong>Last Update:</strong> ${new Date().toLocaleString()}</p>
            `;
        }

        // Initial data load
        setTimeout(updateAllData, 1000);

        // Refresh data every 30 seconds
        setInterval(updateAllData, 30000);
    </script>
</body>
</html>
        """

    def calculate_avg_completion_time(self) -> float:
        """Calculate average completion time for completed jobs."""
        completed_jobs = [
            job for job in self.agent_jobs.values()
            if job.status == "completed" and job.completed_at
        ]

        if not completed_jobs:
            return 0.0

        total_time = 0
        for job in completed_jobs:
            start = datetime.fromisoformat(job.started_at)
            end = datetime.fromisoformat(job.completed_at)
            total_time += (end - start).total_seconds()

        return total_time / len(completed_jobs)

    async def interrupt_workflow(self, session_id: str):
        """Interrupt a running workflow."""
        try:
            if self.streaming_orchestrator:
                success = await self.streaming_orchestrator.interrupt_workflow(session_id)
                await self.broadcast_to_clients({
                    "type": "workflow_interrupted",
                    "session_id": session_id,
                    "success": success
                })
        except Exception as e:
            self.logger.error(f"Error interrupting workflow {session_id}: {e}")

    async def pause_workflow(self, session_id: str):
        """Pause a running workflow."""
        # Implementation would depend on orchestrator capabilities
        await self.broadcast_to_clients({
            "type": "workflow_paused",
            "session_id": session_id
        })

    async def resume_workflow(self, session_id: str):
        """Resume a paused workflow."""
        # Implementation would depend on orchestrator capabilities
        await self.broadcast_to_clients({
            "type": "workflow_resumed",
            "session_id": session_id
        })

    async def get_current_status(self) -> Dict[str, Any]:
        """Get current status of all agents and workflows."""
        return {
            "agents": {job_id: asdict(job) for job_id, job in self.agent_jobs.items()},
            "workflows": {session_id: asdict(session) for session_id, session in self.workflow_sessions.items()}
        }

    async def start(self):
        """Start the monitoring dashboard server."""
        await self.initialize_components()

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        # Start file monitoring task
        self._start_file_monitoring()

        self.logger.info(f"🚀 Monitoring dashboard started at http://{self.host}:{self.port}")
        self.logger.info(f"📊 WebSocket endpoint: ws://{self.host}:{self.port}/ws")

        return runner

    def _start_file_monitoring(self):
        """Start background task to monitor monitoring state file changes."""
        import asyncio
        import os

        async def monitor_file():
            state_file = Path("monitoring_state.json")
            last_mtime = None

            while True:
                try:
                    if state_file.exists():
                        current_mtime = os.path.getmtime(state_file)
                        if last_mtime is None or current_mtime > last_mtime:
                            # File changed, broadcast update to clients
                            await self.broadcast_to_clients({
                                "type": "file_update",
                                "message": "Monitoring state updated"
                            })
                            last_mtime = current_mtime

                    await asyncio.sleep(1)  # Check every second

                except Exception as e:
                    self.logger.error(f"File monitoring error: {e}")
                    await asyncio.sleep(5)  # Wait longer on error

        # Start the monitoring task
        asyncio.create_task(monitor_file())
        self.logger.info("📁 Started monitoring state file watcher")

    async def stop(self):
        """Stop the monitoring dashboard server."""
        if self.monitor:
            self.monitor.stop_monitoring()

        if self.streaming_orchestrator:
            await self.streaming_orchestrator.cleanup()


async def main():
    """Main entry point for the monitoring dashboard."""
    dashboard = MonitoringDashboard()

    try:
        runner = await dashboard.start()

        print("🤖 El Jefe Monitoring Dashboard")
        print("=" * 50)
        print(f"📊 Dashboard URL: http://localhost:8080")
        print(f"🔌 WebSocket API: ws://localhost:8080/ws")
        print(f"📡 REST API: http://localhost:8080/api/")
        print("\nPress Ctrl+C to stop the dashboard")

        # Keep the server running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️ Shutting down monitoring dashboard...")
        await dashboard.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())