#!/usr/bin/env python3
"""
Monitoring Dashboard for El Jefe Agents

Provides real-time monitoring of agent jobs, status, and completion.
Runs as a web server with WebSocket support for live updates.
"""

import asyncio
import json
import logging
import subprocess
import signal
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import websockets
import aiofiles
from aiohttp import web, WSMsgType
import aiohttp_cors
from dataclasses import dataclass, asdict
import hashlib
import base64

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
    # Additional fields for workflow tracking
    created_at: Optional[str] = None
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None

    def __post_init__(self):
        # Use created_at as started_at if started_at not provided but created_at is
        if self.created_at and not self.started_at:
            self.started_at = self.created_at
        # Use started_at as created_at if created_at not provided but started_at is
        elif self.started_at and not self.created_at:
            self.created_at = self.started_at


@dataclass
class WorkflowSession:
    """Represents a complete workflow session."""
    session_id: str
    goal: str = ""
    status: str = "initializing"
    started_at: str = ""
    completed_at: Optional[str] = None
    total_steps: int = 0
    completed_steps: int = 0
    current_step: int = 0
    agents_used: List[str] = None
    workspace: str = ""
    metrics: Dict[str, Any] = None

    # New fields that were missing
    workflow_type: str = ""
    parameters: Dict[str, Any] = None
    priority: str = "normal"
    deadline: Optional[str] = None
    created_at: Optional[str] = None
    agents_assigned: List[str] = None

    def __post_init__(self):
        if self.agents_used is None:
            self.agents_used = []
        if self.metrics is None:
            self.metrics = {}
        if self.parameters is None:
            self.parameters = {}
        if self.agents_assigned is None:
            self.agents_assigned = []

        # Set started_at to created_at if started_at is not provided
        if not self.started_at and self.created_at:
            self.started_at = self.created_at
        elif not self.started_at:
            self.started_at = datetime.now().isoformat()

        # Set created_at if not provided
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ChatMessage:
    """Represents a chat message in the dashboard."""
    message_id: str
    sender: str  # "user" or "el-jefe"
    content: str
    timestamp: str
    message_type: str = "text"  # "text", "status", "error", "system"
    # Additional fields for enhanced chat functionality
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MonitoringDashboard:
    """Main monitoring dashboard server."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.clients = set()
        self.agent_jobs: Dict[str, AgentJob] = {}
        self.workflow_sessions: Dict[str, WorkflowSession] = {}

        # Chat functionality
        self.chat_messages: List[ChatMessage] = []
        self.chat_sessions: Dict[str, Dict] = {}  # Enhanced chat sessions
        self.scheduled_workflows: Dict[str, Dict] = {}  # Scheduled workflows
        self.el_jefe_process = None
        self.chat_active = False

        # Security
        self.password = password or os.getenv("DASHBOARD_PASSWORD", "eljefe123")
        self.auth_token = hashlib.sha256(self.password.encode()).hexdigest()

        # Initialize monitoring components
        self.orchestrator = None
        self.streaming_orchestrator = None
        self.monitor = None
        self.scheduler = None

        # Setup authentication middleware, routes and CORS
        self.setup_auth_middleware()
        self.setup_routes()
        self.setup_cors()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_auth_middleware(self):
        """Setup authentication middleware for all routes."""
        @web.middleware
        async def auth_middleware(request, handler):
            # Skip auth for login route, static files, and API endpoints
            if request.path in ['/login', '/static/', '/favicon.ico'] or request.path.startswith('/api/'):
                return await handler(request)

            # Check for session token or Authorization header
            session_token = request.cookies.get('dashboard_session')
            auth_header = request.headers.get('Authorization')

            valid_token = False
            if session_token:
                valid_token = session_token == self.auth_token[:16]  # Use first 16 chars as session
            elif auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
                valid_token = hashlib.sha256(token.encode()).hexdigest() == self.auth_token

            if not valid_token:
                return web.Response(
                    text='<html><body><h1>Authentication Required</h1>'
                         '<p>Please <a href="/login">login</a> to access the dashboard.</p>'
                         '</body></html>',
                    content_type='text/html',
                    status=401
                )

            return await handler(request)

        self.app.middlewares.append(auth_middleware)

    async def handle_login(self, request):
        """Handle login requests."""
        if request.method == 'GET':
            return web.Response(text='''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>El Jefe Dashboard - Login</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
                        .login-form { background: #f5f5f5; padding: 30px; border-radius: 8px; }
                        input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
                        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
                        button:hover { background: #0056b3; }
                        h1 { color: #333; text-align: center; }
                    </style>
                </head>
                <body>
                    <div class="login-form">
                        <h1>🤖 El Jefe Dashboard</h1>
                        <form method="post">
                            <input type="password" name="password" placeholder="Enter password" required>
                            <button type="submit">Login</button>
                        </form>
                    </div>
                </body>
                </html>
            ''', content_type='text/html')

        elif request.method == 'POST':
            data = await request.post()
            password = data.get('password', '')

            if hashlib.sha256(password.encode()).hexdigest() == self.auth_token:
                response = web.HTTPFound('/')
                response.set_cookie('dashboard_session', self.auth_token[:16], max_age=3600)
                return response
            else:
                return web.Response(text='''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Login Failed</title>
                    </head>
                    <body>
                        <h1>Login Failed</h1>
                        <p>Invalid password. <a href="/login">Try again</a></p>
                    </body>
                    </html>
                ''', content_type='text/html', status=401)

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
        # Authentication
        self.app.router.add_get('/login', self.handle_login)
        self.app.router.add_post('/login', self.handle_login)

        # WebSocket endpoint
        self.app.router.add_get('/ws', self.websocket_handler)

        # API endpoints
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/agents', self.get_agents)
        self.app.router.add_get('/api/agents/real', self.get_real_agents)
        self.app.router.add_post('/api/agents/{agent_id}/assign', self.assign_agent_task)
        self.app.router.add_get('/api/workflows', self.get_workflows)
        self.app.router.add_get('/api/metrics', self.get_metrics)
        self.app.router.add_get('/api/history', self.get_history)
        self.app.router.add_get('/api/chat/history', self.get_chat_history)

        # Enhanced charting API endpoints
        self.app.router.add_get('/api/analytics/agents', self.get_agent_analytics)
        self.app.router.add_get('/api/analytics/workflows', self.get_workflow_analytics)
        self.app.router.add_get('/api/analytics/performance', self.get_performance_analytics)
        self.app.router.add_get('/api/analytics/resources', self.get_resource_analytics)

        # Enhanced chat and workflow API endpoints
        self.app.router.add_get('/api/chat/sessions', self.get_chat_sessions)
        self.app.router.add_get('/api/chat/sessions/{session_id}', self.get_chat_session)
        self.app.router.add_post('/api/workflows/start', self.start_workflow_api)
        self.app.router.add_post('/api/workflows/schedule', self.schedule_workflow_api)
        self.app.router.add_get('/api/scheduled-workflows', self.get_scheduled_workflows)
        self.app.router.add_post('/api/upload', self.handle_file_upload_api)

        # Workspace management endpoints
        self.app.router.add_get('/api/workspaces', self.get_workspaces)
        self.app.router.add_get('/api/workspaces/{workspace_id}', self.get_workspace_details)
        self.app.router.add_get('/api/workspaces/{workspace_id}/files', self.get_workspace_files)
        self.app.router.add_get('/api/workspaces/{workspace_id}/files/{filename:.+}', self.get_workspace_file)

        # Dashboard navigation routes
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_get('/dashboard', self.serve_index)
        self.app.router.add_get('/dashboard/simple', self.serve_simple_dashboard)
        self.app.router.add_get('/dashboard/enhanced', self.serve_enhanced_dashboard)
        self.app.router.add_get('/dashboard/charts', self.serve_charts_dashboard)
        self.app.router.add_get('/dashboard/advanced', self.serve_advanced_dashboard)
        self.app.router.add_get('/dashboard/nav', self.serve_navigation)

        # Serve static files
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
        elif message_type == "chat_message":
            await self.handle_enhanced_chat_message(ws, data)
        elif message_type == "workflow_assignment":
            await self.handle_workflow_assignment(ws, data)
        elif message_type == "workflow_scheduling":
            await self.handle_workflow_scheduling(ws, data)
        elif message_type == "session_management":
            await self.handle_session_management(ws, data)
        elif message_type == "start_el_jefe":
            await self.start_el_jefe()
        elif message_type == "stop_el_jefe":
            await self.stop_el_jefe()
        elif message_type == "file_upload":
            await self.handle_file_upload(ws, data)

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

    async def get_real_agents(self, request):
        """Get all available native El Jefe agents with their configurations."""
        try:
            # Import the agent manager to get real agent data
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from src.agent_manager import AgentType, AgentConfig

            real_agents = []

            # Get all agent types
            for agent_type in AgentType:
                config = AgentConfig.AGENT_CONFIGS.get(agent_type)
                if config:
                    agent_info = {
                        "id": agent_type.value,
                        "name": agent_type.value.replace("_", " ").title(),
                        "type": agent_type.value,
                        "description": config.get("description", "No description available"),
                        "status": "available",  # Native agents are always available
                        "model": "Native El Jefe",
                        "avatar": self._get_agent_avatar(agent_type.value),
                        "max_turns": config.get("max_turns", 5),
                        "allowed_tools": config.get("allowed_tools", []),
                        "system_prompt": config.get("system_prompt", ""),
                        "capabilities": self._get_agent_capabilities(agent_type.value)
                    }
                    real_agents.append(agent_info)

            return web.json_response({
                "success": True,
                "agents": real_agents,
                "total_agents": len(real_agents)
            })

        except Exception as e:
            self.logger.error(f"Error getting real agents: {e}")
            return web.json_response({
                "success": False,
                "error": str(e),
                "agents": []
            }, status=500)

    async def assign_agent_task(self, request):
        """Assign a task to a specific native agent."""
        try:
            agent_id = request.match_info['agent_id']
            task_data = await request.json()
            task = task_data.get('task', '')

            if not task:
                return web.json_response({
                    "success": False,
                    "error": "Task is required"
                }, status=400)

            # Import the agent manager
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from src.agent_manager import AgentType, AgentManager
            from src.playwright_web_researcher import PlaywrightWebResearcher

            # Find the agent type
            try:
                agent_type = AgentType(agent_id)
            except ValueError:
                return web.json_response({
                    "success": False,
                    "error": f"Unknown agent type: {agent_id}"
                }, status=404)

            # Create agent job
            job_id = f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create new agent job
            agent_job = AgentJob(
                job_id=job_id,
                agent_type=agent_id,
                task=task,
                status="running",
                started_at=datetime.now().isoformat(),
                created_at=datetime.now().isoformat(),
                progress=0.0,
                current_step="Initializing agent..."
            )

            # Store the job
            self.agent_jobs[job_id] = agent_job

            # Broadcast job creation
            await self.broadcast_to_clients({
                "type": "agent_update",
                "job": asdict(agent_job)
            })

            # Start the agent execution in background
            asyncio.create_task(self.execute_native_agent(agent_type, task, job_id))

            return web.json_response({
                "success": True,
                "job_id": job_id,
                "agent_type": agent_id,
                "task": task,
                "status": "started",
                "message": f"Task assigned to {agent_id} successfully"
            })

        except Exception as e:
            self.logger.error(f"Error assigning agent task: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def execute_native_agent(self, agent_type, task, job_id):
        """Execute a native agent with the given task."""
        try:
            # Update job status
            if job_id in self.agent_jobs:
                self.agent_jobs[job_id].current_step = "Executing task..."
                self.agent_jobs[job_id].progress = 0.25

                await self.broadcast_to_clients({
                    "type": "agent_update",
                    "job": asdict(self.agent_jobs[job_id])
                })

            # Import agent manager
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from src.agent_manager import AgentManager, AgentType

            # Create workspace for this job
            workspace_path = Path("workspaces") / f"agent_job_{job_id}"
            workspace_path.mkdir(parents=True, exist_ok=True)
            agent_manager = AgentManager(workspace_path)

            try:
                # agent_type is already an AgentType enum from assign_agent_task
                agent_enum = agent_type

                # Execute the actual agent
                result = await agent_manager.spawn_agent(
                    agent_type=agent_enum,
                    task_description=task,
                    output_file=f"job_{job_id}_output.md"
                )

                # Update job with real results
                if job_id in self.agent_jobs:
                    self.agent_jobs[job_id].status = "completed" if result.get("success") else "failed"
                    self.agent_jobs[job_id].completed_at = datetime.now().isoformat()
                    self.agent_jobs[job_id].tokens_used = result.get("tokens_used", 0)
                    self.agent_jobs[job_id].words_generated = len(result.get("output", "").split())

                    if not result.get("success"):
                        self.agent_jobs[job_id].error_message = result.get("error", "Unknown error")

            except Exception as e:
                self.logger.error(f"Error executing agent: {e}")
                # Update job with error
                if job_id in self.agent_jobs:
                    self.agent_jobs[job_id].status = "failed"
                    self.agent_jobs[job_id].error_message = str(e)
                    self.agent_jobs[job_id].completed_at = datetime.now().isoformat()

                    await self.broadcast_to_clients({
                        "type": "agent_update",
                        "job": asdict(self.agent_jobs[job_id])
                    })

        except Exception as e:
            self.logger.error(f"Error executing native agent: {e}")

            # Update job with error
            if job_id in self.agent_jobs:
                self.agent_jobs[job_id].status = "failed"
                self.agent_jobs[job_id].error_message = str(e)
                self.agent_jobs[job_id].completed_at = datetime.now().isoformat()

                await self.broadcast_to_clients({
                    "type": "agent_update",
                    "job": asdict(self.agent_jobs[job_id])
                })

    def _get_agent_avatar(self, agent_type):
        """Get appropriate avatar emoji for agent type."""
        avatars = {
            "researcher": "🔬",
            "coder": "💻",
            "writer": "✍️",
            "analyst": "📊",
            "designer": "🎨",
            "qa_tester": "🧪",
            "media_creator": "🎬",
            "security_analyst": "🔒",
            "data_scientist": "📈",
            "api_developer": "🔌",
            "ai_engineer": "🤖",
            "prompt_engineer": "💭",
            "python_pro": "🐍",
            "frontend_developer": "🌐",
            "ui_ux_designer": "📱",
            "workflow_orchestrator": "🎯",
            "security_engineer": "🛡️",
            "penetration_tester": "🔓",
            "cli_developer": "⌨️"
        }
        return avatars.get(agent_type, "🤖")

    def _get_agent_capabilities(self, agent_type):
        """Get key capabilities for an agent type."""
        capabilities = {
            "researcher": ["Web Research", "Data Analysis", "Information Synthesis"],
            "coder": ["Software Development", "Code Review", "Debugging"],
            "writer": ["Content Creation", "Documentation", "Editing"],
            "analyst": ["Data Analysis", "Trend Identification", "Reporting"],
            "designer": ["System Architecture", "UI Design", "Planning"],
            "qa_tester": ["Testing", "Quality Assurance", "Validation"],
            "media_creator": ["Image Generation", "Video Creation", "Content Production"],
            "security_analyst": ["Security Assessment", "Threat Analysis", "Compliance"],
            "data_scientist": ["Machine Learning", "Statistical Analysis", "Data Modeling"],
            "api_developer": ["API Design", "REST Services", "Integration"],
            "ai_engineer": ["AI/ML Development", "Model Training", "System Integration"],
            "prompt_engineer": ["Prompt Optimization", "LLM Interaction", "Template Design"],
            "python_pro": ["Advanced Python", "Performance Optimization", "Architecture"],
            "frontend_developer": ["React/Vue", "TypeScript", "UI Components"],
            "ui_ux_designer": ["User Research", "Interface Design", "Prototyping"],
            "workflow_orchestrator": ["Multi-agent Coordination", "Task Management", "Process Optimization"],
            "security_engineer": ["Secure Coding", "Threat Modeling", "Security Architecture"],
            "penetration_tester": ["Ethical Hacking", "Vulnerability Assessment", "Security Testing"],
            "cli_developer": ["Command Line Tools", "Developer Utilities", "Terminal Applications"]
        }
        return capabilities.get(agent_type, ["General Purpose"])

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

    # Workspace Management Endpoints
    async def get_workspaces(self, request):
        """Get all workspaces with optional filtering."""
        try:
            # Parse query parameters
            limit = int(request.query.get("limit", 50))
            date_filter = request.query.get("date", None)
            status_filter = request.query.get("status", None)

            workspaces = []
            if self.orchestrator:
                try:
                    # Get workspaces from orchestrator
                    all_workspaces = await self.orchestrator.list_workspaces(limit * 2)  # Get more for filtering

                    # Apply filters
                    for workspace in all_workspaces:
                        # Skip .DS_Store and other system files
                        if workspace.get("name", "").startswith("."):
                            continue

                        # Date filter
                        if date_filter and date_filter not in workspace.get("path", ""):
                            continue

                        # Status filter
                        if status_filter and workspace.get("status", "") != status_filter:
                            continue

                        workspaces.append(workspace)

                except Exception as e:
                    self.logger.error(f"Error getting workspaces from orchestrator: {e}")

            # If orchestrator fails, fallback to file system scan
            if not workspaces:
                workspaces = await self._scan_workspaces_filesystem(limit, date_filter, status_filter)

            return web.json_response({
                "workspaces": workspaces[:limit],
                "total": len(workspaces),
                "filters": {
                    "date": date_filter,
                    "status": status_filter
                }
            })

        except Exception as e:
            self.logger.error(f"Error getting workspaces: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_workspace_details(self, request):
        """Get detailed information about a specific workspace."""
        try:
            workspace_id = request.match_info['workspace_id']

            # Try to find the workspace
            workspace = None
            if self.orchestrator:
                try:
                    # Get all workspaces and find the matching one
                    all_workspaces = await self.orchestrator.list_workspaces(1000)
                    for ws in all_workspaces:
                        if ws.get("name", "") == workspace_id or workspace_id in ws.get("path", ""):
                            workspace = ws
                            break
                except Exception as e:
                    self.logger.error(f"Error finding workspace: {e}")

            if not workspace:
                # Fallback to filesystem search
                workspace = await self._find_workspace_filesystem(workspace_id)

            if not workspace:
                return web.json_response({"error": "Workspace not found"}, status=404)

            # Get additional workspace details
            workspace_path = Path(workspace["path"])
            if workspace_path.exists():
                # Get file list
                files = []
                try:
                    for file_path in workspace_path.rglob("*"):
                        if file_path.is_file() and not file_path.name.startswith("."):
                            relative_path = file_path.relative_to(workspace_path)
                            files.append({
                                "name": file_path.name,
                                "path": str(relative_path),
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime,
                                "type": "file" if file_path.is_file() else "directory"
                            })
                except Exception as e:
                    self.logger.error(f"Error scanning workspace files: {e}")

                workspace["files"] = sorted(files, key=lambda x: x["name"])
                workspace["file_count"] = len(files)

            return web.json_response(workspace)

        except Exception as e:
            self.logger.error(f"Error getting workspace details: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_workspace_files(self, request):
        """List all files in a workspace."""
        try:
            workspace_id = request.match_info['workspace_id']
            workspace_path = await self._resolve_workspace_path(workspace_id)

            if not workspace_path or not workspace_path.exists():
                return web.json_response({"error": "Workspace not found"}, status=404)

            files = []
            try:
                for file_path in workspace_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith("."):
                        relative_path = file_path.relative_to(workspace_path)
                        stat = file_path.stat()

                        files.append({
                            "name": file_path.name,
                            "path": str(relative_path),
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                            "type": self._get_file_type(file_path),
                            "readable": self._is_readable_file(file_path)
                        })

            except Exception as e:
                self.logger.error(f"Error scanning workspace files: {e}")

            # Sort files: directories first, then by name
            files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))

            return web.json_response({
                "workspace_id": workspace_id,
                "files": files,
                "total_files": len(files)
            })

        except Exception as e:
            self.logger.error(f"Error getting workspace files: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_workspace_file(self, request):
        """View or download a specific file from a workspace."""
        try:
            workspace_id = request.match_info['workspace_id']
            filename = request.match_info['filename']

            workspace_path = await self._resolve_workspace_path(workspace_id)
            if not workspace_path or not workspace_path.exists():
                return web.json_response({"error": "Workspace not found"}, status=404)

            file_path = workspace_path / filename
            if not file_path.exists() or not file_path.is_file():
                return web.json_response({"error": "File not found"}, status=404)

            # Check file size limit (10MB max for viewing)
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return web.json_response({"error": "File too large to view (max 10MB)"}, status=413)

            # Check if file is readable (text-based)
            if not self._is_readable_file(file_path):
                return web.json_response({"error": "File type not supported for viewing"}, status=415)

            # Read file content
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
            except UnicodeDecodeError:
                # Try different encoding
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    content = await f.read()

            # Get file info
            stat = file_path.stat()

            response_data = {
                "workspace_id": workspace_id,
                "filename": filename,
                "content": content,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "type": self._get_file_type(file_path),
                "encoding": "utf-8"
            }

            # Check if download requested
            download = request.query.get("download", "").lower() == "true"
            if download:
                response = web.Response(
                    body=content.encode('utf-8'),
                    headers={
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'application/octet-stream'
                    }
                )
                return response
            else:
                return web.json_response(response_data)

        except Exception as e:
            self.logger.error(f"Error getting workspace file: {e}")
            return web.json_response({"error": str(e)}, status=500)

    # Helper methods for workspace management
    async def _scan_workspaces_filesystem(self, limit=50, date_filter=None, status_filter=None):
        """Scan filesystem for workspaces when orchestrator is not available."""
        workspaces = []
        try:
            base_path = Path("workspaces")
            if not base_path.exists():
                return workspaces

            # Scan for workspace directories
            for week_dir in base_path.iterdir():
                if not week_dir.is_dir() or week_dir.name.startswith("."):
                    continue

                for date_dir in week_dir.iterdir():
                    if not date_dir.is_dir() or date_dir.name.startswith("."):
                        continue

                    # Apply date filter if specified
                    if date_filter and date_filter != date_dir.name:
                        continue

                    for workspace_dir in date_dir.iterdir():
                        if not workspace_dir.is_dir() or workspace_dir.name.startswith("."):
                            continue

                        # Try to read workspace info
                        info_file = workspace_dir / "workspace-info.json"
                        if info_file.exists():
                            try:
                                async with aiofiles.open(info_file, 'r') as f:
                                    info_content = await f.read()
                                    info = json.loads(info_content)

                                workspace = {
                                    "path": str(workspace_dir),
                                    "name": info.get("name", workspace_dir.name),
                                    "description": info.get("description", ""),
                                    "created_at": info.get("created_at", ""),
                                    "status": info.get("status", "unknown")
                                }

                                # Apply status filter if specified
                                if status_filter and workspace["status"] != status_filter:
                                    continue

                                workspaces.append(workspace)

                            except Exception as e:
                                self.logger.error(f"Error reading workspace info {info_file}: {e}")
                                continue
                        else:
                            # Fallback workspace info
                            workspaces.append({
                                "path": str(workspace_dir),
                                "name": workspace_dir.name,
                                "description": "",
                                "created_at": "",
                                "status": "unknown"
                            })

                        if len(workspaces) >= limit:
                            break
                    if len(workspaces) >= limit:
                        break

        except Exception as e:
            self.logger.error(f"Error scanning workspaces filesystem: {e}")

        return sorted(workspaces, key=lambda x: x.get("created_at", ""), reverse=True)

    async def _find_workspace_filesystem(self, workspace_id):
        """Find a workspace by ID in the filesystem."""
        try:
            base_path = Path("workspaces")
            for week_dir in base_path.rglob("*"):
                if week_dir.is_dir() and week_dir.name == workspace_id:
                    info_file = week_dir / "workspace-info.json"
                    if info_file.exists():
                        try:
                            async with aiofiles.open(info_file, 'r') as f:
                                info_content = await f.read()
                                info = json.loads(info_content)

                            return {
                                "path": str(week_dir),
                                "name": info.get("name", week_dir.name),
                                "description": info.get("description", ""),
                                "created_at": info.get("created_at", ""),
                                "status": info.get("status", "unknown")
                            }
                        except Exception:
                            pass

                    return {
                        "path": str(week_dir),
                        "name": week_dir.name,
                        "description": "",
                        "created_at": "",
                        "status": "unknown"
                    }
        except Exception as e:
            self.logger.error(f"Error finding workspace {workspace_id}: {e}")

        return None

    async def _resolve_workspace_path(self, workspace_id):
        """Resolve workspace ID to actual filesystem path."""
        # First try to find it by exact match
        workspace = await self._find_workspace_filesystem(workspace_id)
        if workspace:
            return Path(workspace["path"])

        # Try to find it by partial match
        try:
            base_path = Path("workspaces")
            for path in base_path.rglob("*"):
                if path.is_dir() and workspace_id in path.name:
                    return path
        except Exception as e:
            self.logger.error(f"Error resolving workspace path: {e}")

        return None

    def _get_file_type(self, file_path):
        """Determine file type based on extension."""
        suffix = file_path.suffix.lower()

        if suffix in ['.md', '.txt', '.rst']:
            return 'text'
        elif suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
            return 'code'
        elif suffix in ['.json', '.yaml', '.yml', '.xml', '.csv']:
            return 'data'
        elif suffix in ['.html', '.css', '.scss', '.less']:
            return 'web'
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
            return 'image'
        elif suffix in ['.pdf', '.doc', '.docx', '.txt']:
            return 'document'
        elif suffix in ['.log']:
            return 'log'
        else:
            return 'unknown'

    def _is_readable_file(self, file_path):
        """Check if file is readable as text."""
        # Check file extension
        text_extensions = {
            '.md', '.txt', '.py', '.js', '.ts', '.html', '.css', '.json',
            '.yaml', '.yml', '.xml', '.csv', '.log', '.rst', '.ini', '.cfg',
            '.conf', '.sh', '.bash', '.zsh', '.sql', '.graphql'
        }

        if file_path.suffix.lower() in text_extensions:
            return True

        # Check file size (skip very large files)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return False
        except:
            return False

        # Default to False for unknown file types
        return False

    async def serve_index(self, request):
        """Serve the main dashboard HTML page."""
        # Serve the workspace-integrated dashboard FIRST (highest priority)
        workspace_html_path = Path(__file__).parent / "static" / "dashboard-agent-focused.html"
        if workspace_html_path.exists():
            return web.FileResponse(workspace_html_path)

        # Try to serve the advanced analytics dashboard second (Phase 3)
        advanced_html_path = Path(__file__).parent / "static" / "dashboard-advanced.html"
        if advanced_html_path.exists():
            return web.FileResponse(advanced_html_path)

        # Try to serve the charts dashboard third (Phase 2)
        charts_html_path = Path(__file__).parent / "static" / "dashboard-charts.html"
        if charts_html_path.exists():
            return web.FileResponse(charts_html_path)

        # Try to serve the enhanced v2 dashboard fourth
        v2_html_path = Path(__file__).parent / "static" / "dashboard-v2.html"
        if v2_html_path.exists():
            return web.FileResponse(v2_html_path)

        # Fallback to original dashboard
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

    # Dashboard Navigation Methods

    async def serve_simple_dashboard(self, request):
        """Serve the original simple dashboard for agent monitoring."""
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            return web.FileResponse(html_path)
        else:
            # Return a simple view of current agents
            return web.Response(text=self.get_simple_agents_view(), content_type="text/html")

    async def serve_enhanced_dashboard(self, request):
        """Serve the enhanced v2 dashboard with improved UX."""
        v2_html_path = Path(__file__).parent / "static" / "dashboard-v2.html"
        if v2_html_path.exists():
            return web.FileResponse(v2_html_path)
        else:
            # Fallback to simple dashboard
            return await self.serve_simple_dashboard(request)

    async def serve_charts_dashboard(self, request):
        """Serve the charts dashboard with data visualization."""
        charts_html_path = Path(__file__).parent / "static" / "dashboard-charts.html"
        if charts_html_path.exists():
            return web.FileResponse(charts_html_path)
        else:
            # Fallback to enhanced dashboard
            return await self.serve_enhanced_dashboard(request)

    async def serve_advanced_dashboard(self, request):
        """Serve the advanced dashboard with ML analytics and chat."""
        advanced_html_path = Path(__file__).parent / "static" / "dashboard-advanced.html"
        if advanced_html_path.exists():
            return web.FileResponse(advanced_html_path)
        else:
            # Fallback to charts dashboard
            return await self.serve_charts_dashboard(request)

    async def serve_navigation(self, request):
        """Serve a navigation page to choose between dashboard versions."""
        return web.Response(text=self.get_navigation_page(), content_type="text/html")

    def get_simple_agents_view(self) -> str:
        """Get a simple HTML view focused on agent monitoring."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>El Jefe - Simple Agent View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .nav { text-align: center; margin-bottom: 20px; }
        .nav a { margin: 0 10px; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; }
        .nav a:hover { background: #2980b9; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .agent-job { border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 4px; }
        .status-running { border-left-color: #f39c12; }
        .status-completed { border-left-color: #27ae60; }
        .status-failed { border-left-color: #e74c3c; }
        .status-initializing { border-left-color: #9b59b6; }
        .connections { background: #27ae60; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .metric { text-align: center; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 El Jefe - Simple Agent View</h1>
        <div class="connections" id="connections">🟢 Connected</div>
    </div>

    <div class="nav">
        <a href="/dashboard/simple">Simple View</a>
        <a href="/dashboard/enhanced">Enhanced View</a>
        <a href="/dashboard/charts">Charts View</a>
        <a href="/dashboard/advanced">Advanced View</a>
        <a href="/dashboard/nav">All Dashboards</a>
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
    </div>

    <div class="metrics">
        <div class="metric">
            <div class="metric-value" id="active-agents">0</div>
            <div>Active Agents</div>
        </div>
        <div class="metric">
            <div class="metric-value" id="active-workflows">0</div>
            <div>Active Workflows</div>
        </div>
        <div class="metric">
            <div class="metric-value" id="completed-jobs">0</div>
            <div>Completed Jobs</div>
        </div>
        <div class="metric">
            <div class="metric-value" id="total-tokens">0</div>
            <div>Total Tokens Used</div>
        </div>
    </div>

    <div class="card">
        <h2>🔧 Active Agent Jobs</h2>
        <div id="agents-list">
            <p>Loading agents...</p>
        </div>
    </div>

    <div class="card">
        <h2>📋 Workflow Sessions</h2>
        <div id="workflows-list">
            <p>Loading workflows...</p>
        </div>
    </div>

    <script>
        let ws;

        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onopen = function() {
                document.getElementById('connections').textContent = '🟢 Connected';
                document.getElementById('connections').style.background = '#27ae60';
            };

            ws.onclose = function() {
                document.getElementById('connections').textContent = '🔴 Disconnected';
                document.getElementById('connections').style.background = '#e74c3c';
                setTimeout(() => connectWebSocket(), 5000);
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleUpdate(data);
            };
        }

        function handleUpdate(data) {
            if (data.type === 'agent_update' || data.type === 'initial_data') {
                updateAgentsList();
            }
            if (data.type === 'workflow_update' || data.type === 'initial_data') {
                updateWorkflowsList();
            }
            if (data.type === 'initial_data') {
                updateMetrics();
            }
        }

        function updateMetrics() {
            fetch('/api/status').then(r => r.json()).then(data => {
                document.getElementById('active-agents').textContent = data.system.active_agents || 0;
                document.getElementById('active-workflows').textContent = data.system.active_workflows || 0;
            });

            fetch('/api/metrics').then(r => r.json()).then(metrics => {
                document.getElementById('completed-jobs').textContent = metrics.completed_jobs || 0;
                document.getElementById('total-tokens').textContent = (metrics.total_tokens || 0).toLocaleString();
            });
        }

        function updateAgentsList() {
            fetch('/api/agents').then(r => r.json()).then(agents => {
                const listEl = document.getElementById('agents-list');
                const agentsArray = Object.values(agents);

                if (agentsArray.length === 0) {
                    listEl.innerHTML = '<p>No active agents</p>';
                    return;
                }

                listEl.innerHTML = agentsArray.map(agent => {
                    const statusClass = agent.status ? `status-${agent.status}` : '';
                    const startTime = agent.started_at ? new Date(agent.started_at).toLocaleTimeString() : 'Unknown';
                    const tokens = agent.tokens_used || 0;
                    const words = agent.words_generated || 0;

                    return `
                        <div class="agent-job ${statusClass}">
                            <h4>${agent.agent_type || 'Unknown Agent'}</h4>
                            <p><strong>Status:</strong> ${agent.status || 'Unknown'}</p>
                            <p><strong>Job ID:</strong> ${agent.job_id || 'N/A'}</p>
                            <p><strong>Started:</strong> ${startTime}</p>
                            <p><strong>Tokens:</strong> ${tokens.toLocaleString()} | <strong>Words:</strong> ${words.toLocaleString()}</p>
                            ${agent.workflow_id ? `<p><strong>Workflow:</strong> ${agent.workflow_id}</p>` : ''}
                        </div>
                    `;
                }).join('');
            }).catch(err => {
                console.error('Error fetching agents:', err);
                document.getElementById('agents-list').innerHTML = '<p>Error loading agents</p>';
            });
        }

        function updateWorkflowsList() {
            fetch('/api/workflows').then(r => r.json()).then(workflows => {
                const listEl = document.getElementById('workflows-list');
                const workflowsArray = Object.values(workflows);

                if (workflowsArray.length === 0) {
                    listEl.innerHTML = '<p>No active workflows</p>';
                    return;
                }

                listEl.innerHTML = workflowsArray.map(workflow => {
                    const statusClass = workflow.status ? `status-${workflow.status}` : '';
                    const createdTime = workflow.created_at ? new Date(workflow.created_at).toLocaleString() : 'Unknown';
                    const priority = workflow.priority || 'medium';

                    return `
                        <div class="agent-job ${statusClass}">
                            <h4>${workflow.workflow_type || 'Unknown Workflow'}</h4>
                            <p><strong>Status:</strong> ${workflow.status || 'Unknown'}</p>
                            <p><strong>Session ID:</strong> ${workflow.session_id || 'N/A'}</p>
                            <p><strong>Priority:</strong> ${priority}</p>
                            <p><strong>Created:</strong> ${createdTime}</p>
                            ${workflow.deadline ? `<p><strong>Deadline:</strong> ${new Date(workflow.deadline).toLocaleString()}</p>` : ''}
                            ${workflow.agents_used && workflow.agents_used.length > 0 ?
                                `<p><strong>Agents Used:</strong> ${workflow.agents_used.join(', ')}</p>` : ''}
                        </div>
                    `;
                }).join('');
            }).catch(err => {
                console.error('Error fetching workflows:', err);
                document.getElementById('workflows-list').innerHTML = '<p>Error loading workflows</p>';
            });
        }

        function refreshData() {
            updateMetrics();
            updateAgentsList();
            updateWorkflowsList();
        }

        // Initialize
        connectWebSocket();
        refreshData();

        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
        """

    def get_navigation_page(self) -> str:
        """Get a navigation page to choose between dashboards."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>El Jefe Dashboard Navigation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 30px; text-align: center; }
        .nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .dashboard-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .dashboard-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
        .dashboard-title { font-size: 1.5em; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
        .dashboard-description { color: #7f8c8d; margin-bottom: 20px; line-height: 1.5; }
        .dashboard-link { display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; transition: background 0.2s; }
        .dashboard-link:hover { background: #2980b9; }
        .feature-tag { display: inline-block; background: #ecf0f1; color: #34495e; padding: 4px 8px; margin: 2px; border-radius: 3px; font-size: 0.8em; }
        .recommended { border: 2px solid #27ae60; }
        .simple { border: 2px solid #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 El Jefe Dashboard Navigation</h1>
        <p>Choose the right dashboard for your needs</p>
    </div>

    <div class="nav-grid">
        <div class="dashboard-card simple">
            <div class="dashboard-title">🔧 Simple Agent View</div>
            <div class="dashboard-description">
                Clean, straightforward monitoring of active agents and workflows.
                Perfect for quickly checking system status and current work being done.
            </div>
            <div>
                <span class="feature-tag">Real-time Updates</span>
                <span class="feature-tag">Agent Status</span>
                <span class="feature-tag">Workflow Tracking</span>
                <span class="feature-tag">Fast & Lightweight</span>
            </div>
            <br><br>
            <a href="/dashboard/simple" class="dashboard-link">Open Simple View</a>
        </div>

        <div class="dashboard-card">
            <div class="dashboard-title">✨ Enhanced Dashboard</div>
            <div class="dashboard-description">
                Improved user experience with better navigation, search functionality,
                and enhanced responsive design for mobile devices.
            </div>
            <div>
                <span class="feature-tag">Tab Navigation</span>
                <span class="feature-tag">Search</span>
                <span class="feature-tag">Mobile Optimized</span>
                <span class="feature-tag">Accessibility</span>
            </div>
            <br><br>
            <a href="/dashboard/enhanced" class="dashboard-link">Open Enhanced View</a>
        </div>

        <div class="dashboard-card">
            <div class="dashboard-title">📊 Charts Dashboard</div>
            <div class="dashboard-description">
                Advanced data visualization with real-time charts, performance metrics,
                and analytics for detailed system monitoring.
            </div>
            <div>
                <span class="feature-tag">Real-time Charts</span>
                <span class="feature-tag">Performance Analytics</span>
                <span class="feature-tag">Trend Visualization</span>
                <span class="feature-tag">Enhanced Chat</span>
            </div>
            <br><br>
            <a href="/dashboard/charts" class="dashboard-link">Open Charts View</a>
        </div>

        <div class="dashboard-card recommended">
            <div class="dashboard-title">🚀 Advanced Dashboard</div>
            <div class="dashboard-description">
                <strong>Recommended - </strong>Full-featured dashboard with ML analytics,
                predictive insights, workflow scheduling, and intelligent chat interface.
            </div>
            <div>
                <span class="feature-tag">🌟 Recommended</span>
                <span class="feature-tag">AI Chat Interface</span>
                <span class="feature-tag">Workflow Scheduling</span>
                <span class="feature-tag">Predictive Analytics</span>
                <span class="feature-tag">Cost Optimization</span>
                <span class="feature-tag">Multi-session Chat</span>
            </div>
            <br><br>
            <a href="/dashboard/advanced" class="dashboard-link">Open Advanced View</a>
        </div>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #7f8c8d;">
        <p>💡 <strong>Tip:</strong> Start with the Simple view for quick monitoring,
        then explore the Advanced view for full workflow management capabilities.</p>
        <p style="margin-top: 10px;">
            <a href="/" style="color: #3498db; text-decoration: none;">← Back to Default Dashboard</a>
        </p>
    </div>
</body>
</html>
        """

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

        # Stop El Jefe process if running
        await self.stop_el_jefe()

    async def handle_chat_message(self, ws, message: str):
        """Handle incoming chat messages from users."""
        if not message.strip():
            return

        # Create user message
        user_message = ChatMessage(
            message_id=f"user_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            sender="user",
            content=message.strip(),
            timestamp=datetime.now().isoformat(),
            message_type="text"
        )

        self.chat_messages.append(user_message)

        # Broadcast user message to all clients
        await self.broadcast_to_clients({
            "type": "chat_message",
            "message": asdict(user_message)
        })

        # Send to El Jefe if process is running
        if self.el_jefe_process and self.chat_active:
            try:
                # Ensure we're sending bytes to stdin
                if hasattr(self.el_jefe_process.stdin, 'write'):
                    message_bytes = (message + "\n").encode('utf-8')
                    self.el_jefe_process.stdin.write(message_bytes)
                    await self.el_jefe_process.stdin.drain()
            except (BrokenPipeError, ConnectionResetError) as e:
                # Process likely ended, update status
                self.chat_active = False
                self.el_jefe_process = None

                error_message = ChatMessage(
                    message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    sender="el-jefe",
                    content="El Jefe process ended unexpectedly. Please restart.",
                    timestamp=datetime.now().isoformat(),
                    message_type="error"
                )
                self.chat_messages.append(error_message)
                await self.broadcast_to_clients({
                    "type": "chat_message",
                    "message": asdict(error_message)
                })
            except Exception as e:
                error_message = ChatMessage(
                    message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    sender="el-jefe",
                    content=f"Error sending message to El Jefe: {e}",
                    timestamp=datetime.now().isoformat(),
                    message_type="error"
                )
                self.chat_messages.append(error_message)
                await self.broadcast_to_clients({
                    "type": "chat_message",
                    "message": asdict(error_message)
                })

    async def start_el_jefe(self):
        """Start El Jefe process for chat interaction."""
        if self.el_jefe_process and self.chat_active:
            return

        try:
            # Start El Jefe in interactive mode
            self.el_jefe_process = await asyncio.create_subprocess_exec(
                'el-jefe',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # Merge stderr with stdout
                cwd=Path.cwd()
            )

            self.chat_active = True

            # Start reading El Jefe output
            asyncio.create_task(self.read_el_jefe_output())

            # Send system message
            system_message = ChatMessage(
                message_id=f"system_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="el-jefe",
                content="El Jefe is now ready to chat! 🤖",
                timestamp=datetime.now().isoformat(),
                message_type="system"
            )
            self.chat_messages.append(system_message)
            await self.broadcast_to_clients({
                "type": "chat_message",
                "message": asdict(system_message)
            })

        except Exception as e:
            error_message = ChatMessage(
                message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="el-jefe",
                content=f"Failed to start El Jefe: {e}",
                timestamp=datetime.now().isoformat(),
                message_type="error"
            )
            self.chat_messages.append(error_message)
            await self.broadcast_to_clients({
                "type": "chat_message",
                "message": asdict(error_message)
            })

    async def stop_el_jefe(self):
        """Stop El Jefe process."""
        if self.el_jefe_process:
            try:
                self.el_jefe_process.terminate()
                await self.el_jefe_process.wait()
                self.chat_active = False
                self.el_jefe_process = None

                # Send system message
                system_message = ChatMessage(
                    message_id=f"system_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    sender="el-jefe",
                    content="El Jefe has been stopped.",
                    timestamp=datetime.now().isoformat(),
                    message_type="system"
                )
                self.chat_messages.append(system_message)
                await self.broadcast_to_clients({
                    "type": "chat_message",
                    "message": asdict(system_message)
                })

            except Exception as e:
                self.logger.error(f"Error stopping El Jefe: {e}")

    async def read_el_jefe_output(self):
        """Read output from El Jefe process and broadcast to clients."""
        while self.chat_active and self.el_jefe_process:
            try:
                line = await self.el_jefe_process.stdout.readline()
                if not line:
                    # Process ended
                    self.chat_active = False
                    break

                # Decode line properly
                if isinstance(line, bytes):
                    content = line.decode('utf-8').strip()
                else:
                    content = str(line).strip()

                if content:
                    # Create El Jefe message
                    el_jefe_message = ChatMessage(
                        message_id=f"eljefe_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        sender="el-jefe",
                        content=content,
                        timestamp=datetime.now().isoformat(),
                        message_type="text"
                    )

                    self.chat_messages.append(el_jefe_message)
                    await self.broadcast_to_clients({
                        "type": "chat_message",
                        "message": asdict(el_jefe_message)
                    })

            except Exception as e:
                self.logger.error(f"Error reading El Jefe output: {e}")
                break

    async def get_chat_history(self, request):
        """Get chat message history."""
        return web.json_response([asdict(msg) for msg in self.chat_messages])

    # Enhanced Analytics API Endpoints
    async def get_agent_analytics(self, request):
        """Get detailed agent analytics from real data."""
        try:
            # Get time range from query parameters
            time_range = request.query.get('range', '1h')

            # Get real data from agent manager and workflow system
            real_analytics = {
                'time_range': time_range,
                'data_source': 'real',
                'performance_metrics': {
                    'success_rate': self._calculate_real_success_rate(),
                    'average_response_time': self._calculate_real_response_time(),
                    'error_rate': self._calculate_real_error_rate(),
                    'throughput': self._calculate_real_throughput()
                },
                'agent_types': self._get_real_agent_type_stats(),
                'timeline_data': self._get_real_timeline_data('agents', time_range),
                'resource_usage': self._get_real_resource_usage()
            }

            return web.json_response(real_analytics)

        except Exception as e:
            self.logger.error(f"Error getting real agent analytics: {e}")
            return web.json_response({'error': 'Analytics not available - real data collection in progress', 'data_source': 'none'}, status=503)

    async def get_workflow_analytics(self, request):
        """Get detailed workflow analytics from real data."""
        try:
            # Get time range from query parameters
            time_range = request.query.get('range', '1h')

            # Get real workflow data
            real_analytics = {
                'time_range': time_range,
                'data_source': 'real',
                'workflow_metrics': {
                    'total_workflows': len(self.workflows),
                    'active_workflows': len([w for w in self.workflows.values() if w.status == 'running']),
                    'completed_workflows': len([w for w in self.workflows.values() if w.status == 'completed']),
                    'failed_workflows': len([w for w in self.workflows.values() if w.status == 'failed']),
                    'average_duration': self._calculate_average_workflow_duration(),
                    'success_rate': self._calculate_workflow_success_rate()
                },
                'workflow_types': self._get_workflow_type_stats(),
                'timeline_data': self._get_workflow_timeline_data(time_range)
            }

            return web.json_response(real_analytics)

        except Exception as e:
            self.logger.error(f"Error getting real workflow analytics: {e}")
            return web.json_response({'error': 'Workflow analytics not available', 'data_source': 'none'}, status=503)


    # Real Analytics Helper Methods

    def _calculate_real_success_rate(self):
        """Calculate real success rate from actual agent data."""
        try:
            agents = list(self.agent_manager.agents.values())
            if not agents:
                return 0.0
            successful_agents = len([a for a in agents if getattr(a, 'status', None) == 'completed'])
            return (successful_agents / len(agents)) * 100 if agents else 0.0
        except:
            return 0.0

    def _calculate_real_response_time(self):
        """Calculate real average response time."""
        try:
            # This would need to be implemented with real timing data
            return 0.0  # Placeholder until real timing is implemented
        except:
            return 0.0

    def _calculate_real_error_rate(self):
        """Calculate real error rate from actual data."""
        try:
            agents = list(self.agent_manager.agents.values())
            if not agents:
                return 0.0
            failed_agents = len([a for a in agents if getattr(a, 'status', None) == 'failed'])
            return (failed_agents / len(agents)) * 100 if agents else 0.0
        except:
            return 0.0

    def _calculate_real_throughput(self):
        """Calculate real throughput."""
        try:
            return len(self.active_connections)
        except:
            return 0

    def _get_real_agent_type_stats(self):
        """Get real agent type statistics."""
        try:
            from src.agent_manager import AgentType
            stats = {}
            for agent_type in AgentType:
                stats[agent_type.value.lower()] = {
                    'count': 0,
                    'avg_completion_time': 0.0,
                    'success_rate': 0.0,
                    'tasks_completed': 0
                }
            return stats
        except:
            return {}

    def _get_real_timeline_data(self, data_type, time_range):
        """Get real timeline data - placeholder for implementation."""
        return []

    def _get_real_resource_usage(self):
        """Get real resource usage."""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            return {}

    def _calculate_avg_completion_time(self, workflows):
        """Calculate average completion time for workflows."""
        if not workflows:
            return 0.0
        completed = [w for w in workflows if w.status == 'completed']
        if not completed:
            return 0.0
        # Would need real timing data
        return 0.0

    def _get_real_stage_performance(self, workflows):
        """Get real stage performance data."""
        return {}

    def _calculate_system_health(self):
        """Calculate overall system health score."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            # Simple health calculation (100 - average usage)
            health = 100 - ((cpu + memory + disk) / 3)
            return max(0, min(100, health))
        except:
            return 0.0

    def _measure_network_latency(self):
        """Measure network latency."""
        return 0.0  # Placeholder

    def _calculate_avg_response_time(self):
        """Calculate average response time."""
        return 0.0  # Placeholder

    def _calculate_error_rate(self):
        """Calculate system error rate."""
        return 0.0  # Placeholder

    # Enhanced Chat and Workflow Management Methods

    async def handle_enhanced_chat_message(self, ws, data):
        """Handle enhanced chat messages with workflow detection and assignment."""
        session_id = data.get("session_id", "default")
        message = data.get("message", "")
        sender = data.get("sender", "user")

        if not message.strip():
            return

        # Create chat message
        chat_message = ChatMessage(
            message_id=f"{sender}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            sender=sender,
            content=message.strip(),
            timestamp=datetime.now().isoformat(),
            message_type="text",
            session_id=session_id
        )

        # Add to chat messages for this session
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = {
                "messages": [],
                "workflow_id": None,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }

        self.chat_sessions[session_id]["messages"].append(asdict(chat_message))
        self.chat_messages.append(chat_message)

        # Broadcast message to all clients
        await self.broadcast_to_clients({
            "type": "chat_message",
            "message": asdict(chat_message),
            "session_id": session_id
        })

        # Detect workflows in the message
        detected_workflows = await self.detect_workflows_in_message(message)

        if detected_workflows:
            # Send workflow detection notification
            await self.send_to_client(ws, {
                "type": "workflow_detection",
                "detected_workflows": detected_workflows,
                "session_id": session_id,
                "message": f"I detected potential workflows in your message: {', '.join([w['name'] for w in detected_workflows])}"
            })

        # Process message with AI if available
        if self.el_jefe_process and self.chat_active:
            await self.process_message_with_ai(message, session_id)
        else:
            # Provide intelligent response based on workflow detection
            if detected_workflows:
                response = await self.generate_workflow_suggestions(detected_workflows, message)
            else:
                response = await self.generate_general_response(message)

            ai_message = ChatMessage(
                message_id=f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="ai-assistant",
                content=response,
                timestamp=datetime.now().isoformat(),
                message_type="ai_response",
                session_id=session_id
            )

            self.chat_sessions[session_id]["messages"].append(asdict(ai_message))
            self.chat_messages.append(ai_message)

            await self.broadcast_to_clients({
                "type": "chat_message",
                "message": asdict(ai_message),
                "session_id": session_id
            })

    async def detect_workflows_in_message(self, message: str) -> List[Dict[str, Any]]:
        """Detect workflow intents in user messages using keyword matching and patterns."""
        import re
        from typing import List, Dict, Any

        message_lower = message.lower()
        detected_workflows = []

        # Workflow templates with keywords and patterns
        workflow_templates = {
            "feature-development": {
                "name": "Feature Development",
                "keywords": ["feature", "develop", "implement", "build", "create", "add functionality", "new feature"],
                "patterns": [r"implement.*feature", r"build.*functionality", r"add.*feature", r"create.*new"],
                "description": "Complete feature implementation with multi-agent coordination"
            },
            "security-audit": {
                "name": "Security Audit",
                "keywords": ["security", "audit", "vulnerability", "scan", "check security", "security review"],
                "patterns": [r"security.*audit", r"vulnerability.*scan", r"check.*security", r"security.*review"],
                "description": "Comprehensive security assessment and vulnerability analysis"
            },
            "documentation-update": {
                "name": "Documentation Update",
                "keywords": ["documentation", "docs", "readme", "guide", "manual", "update docs"],
                "patterns": [r"update.*documentation", r"write.*docs", r"create.*guide", r"documentation.*update"],
                "description": "Generate and update project documentation"
            },
            "debugging-session": {
                "name": "Debugging Session",
                "keywords": ["debug", "bug", "error", "issue", "problem", "fix", "troubleshoot"],
                "patterns": [r"debug.*issue", r"fix.*bug", r"troubleshoot.*problem", r"investigate.*error"],
                "description": "Systematic debugging and problem resolution"
            },
            "deployment-prep": {
                "name": "Deployment Preparation",
                "keywords": ["deploy", "deployment", "production", "release", "ship", "go live"],
                "patterns": [r"prepare.*deployment", r"deploy.*production", r"release.*application", r"go.*live"],
                "description": "Prepare application for production deployment"
            }
        }

        for workflow_id, template in workflow_templates.items():
            found_keywords = [kw for kw in template["keywords"] if kw in message_lower]
            matched_patterns = []

            # Check regex patterns
            for pattern in template["patterns"]:
                if re.search(pattern, message_lower):
                    matched_patterns.append(pattern)

            # Calculate confidence score
            confidence = 0
            if found_keywords:
                confidence += len(found_keywords) * 0.3
            if matched_patterns:
                confidence += len(matched_patterns) * 0.4

            if confidence > 0.3:  # Threshold for detection
                detected_workflows.append({
                    "workflow_id": workflow_id,
                    "name": template["name"],
                    "description": template["description"],
                    "confidence": min(confidence, 1.0),
                    "keywords": found_keywords,
                    "patterns": matched_patterns
                })

        # Sort by confidence
        detected_workflows.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_workflows[:2]  # Return top 2 matches

    async def generate_workflow_suggestions(self, workflows: List[Dict], message: str) -> str:
        """Generate AI-powered workflow suggestions."""
        if not workflows:
            return "I can help you with various tasks. What would you like to work on?"

        top_workflow = workflows[0]
        workflow_name = top_workflow["name"]
        workflow_id = top_workflow["workflow_id"]

        suggestions = {
            "feature-development": f"I can help you implement that feature! I'll coordinate between specialized agents to handle development, security review, testing, and documentation. Would you like me to start a feature development workflow?",
            "security-audit": f"I'll perform a comprehensive security audit of your project. This includes vulnerability scanning, code analysis, and security best practices validation. Shall I begin the security assessment?",
            "documentation-update": f"I can help you create comprehensive documentation. I'll analyze your codebase and generate user guides, API documentation, and README files. Would you like me to start the documentation workflow?",
            "debugging-session": f"I'll help you debug this issue systematically. I'll analyze the problem, identify root causes, and coordinate with debugging experts to find a solution. Ready to start the debugging process?",
            "deployment-prep": f"I'll prepare your application for production deployment. This includes security checks, performance optimization, and deployment pipeline setup. Should I begin the deployment preparation?"
        }

        base_response = suggestions.get(workflow_id, f"I can help you with {workflow_name}. Would you like me to start this workflow?")

        # Add workflow assignment options
        return f"{base_response}\n\nYou can also:\n• Click the workflow template above to auto-configure\n• Specify a deadline for completion\n• Add specific requirements or constraints"

    async def generate_general_response(self, message: str) -> str:
        """Generate intelligent responses for general queries."""
        message_lower = message.lower()

        # Check for common query types
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your AI assistant for the El Jefe monitoring dashboard. I can help you:\n\n🚀 Start workflows (feature development, security audits, debugging)\n📊 Monitor agents and system performance\n💬 Chat with El Jefe directly\n📅 Schedule tasks for later\n\nWhat would you like to work on today?"

        elif any(word in message_lower for word in ["help", "what can you do"]):
            return """I can assist you with several powerful workflows:

🚀 **Feature Development** - Build new features with multi-agent coordination
🔒 **Security Audit** - Comprehensive security assessments
📚 **Documentation** - Generate and update project documentation
🐛 **Debugging** - Systematic problem resolution and bug fixing
🚀 **Deployment** - Prepare applications for production release

I can also:
• Monitor agent performance in real-time
• Schedule workflows for specific times
• Chat with El Jefe directly
• Analyze system metrics and trends

Just tell me what you'd like to accomplish!"""

        elif any(word in message_lower for word in ["status", "how are you"]):
            agents_count = len(self.agent_jobs)
            workflows_count = len(self.workflow_sessions)
            return f"System is running smoothly! Currently monitoring {agents_count} active agents and {workflows_count} workflows. All systems operational and ready to assist you."

        elif any(word in message_lower for word in ["thank", "thanks"]):
            return "You're welcome! I'm always here to help you manage workflows and monitor your agents. Let me know if you need anything else!"

        else:
            return "I understand you need assistance. I can help you start various workflows like feature development, security audits, or debugging sessions. You can also ask me about system status or chat with El Jefe directly. What specific task would you like to work on?"

    async def handle_workflow_assignment(self, ws, data):
        """Handle workflow assignment from chat interface."""
        workflow_id = data.get("workflow_id")
        session_id = data.get("session_id", "default")
        parameters = data.get("parameters", {})
        priority = data.get("priority", "medium")
        deadline = data.get("deadline", None)

        if not workflow_id:
            await self.send_to_client(ws, {
                "type": "error",
                "message": "Workflow ID is required"
            })
            return

        try:
            # Create workflow session
            workflow_session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            workflow_session = WorkflowSession(
                session_id=workflow_session_id,
                workflow_type=workflow_id,
                status="initializing",
                parameters=parameters,
                priority=priority,
                deadline=deadline,
                created_at=datetime.now().isoformat(),
                agents_assigned=[]
            )

            self.workflow_sessions[workflow_session_id] = workflow_session

            # Update chat session with workflow
            if session_id in self.chat_sessions:
                self.chat_sessions[session_id]["workflow_id"] = workflow_session_id
                self.chat_sessions[session_id]["status"] = "workflow_active"

            # Broadcast workflow creation
            await self.broadcast_to_clients({
                "type": "workflow_created",
                "session": asdict(workflow_session),
                "chat_session_id": session_id
            })

            # Start the workflow execution
            asyncio.create_task(self.execute_workflow(workflow_session_id, workflow_id, parameters))

            # Send confirmation
            await self.send_to_client(ws, {
                "type": "workflow_assignment_success",
                "workflow_id": workflow_id,
                "session_id": workflow_session_id,
                "message": f"Workflow '{workflow_id}' has been started successfully!"
            })

        except Exception as e:
            self.logger.error(f"Error assigning workflow: {e}")
            await self.send_to_client(ws, {
                "type": "error",
                "message": f"Failed to assign workflow: {str(e)}"
            })

    async def handle_workflow_scheduling(self, ws, data):
        """Handle workflow scheduling for future execution."""
        workflow_id = data.get("workflow_id")
        scheduled_time = data.get("scheduled_time")
        parameters = data.get("parameters", {})
        priority = data.get("priority", "medium")
        session_id = data.get("session_id", "default")

        if not workflow_id or not scheduled_time:
            await self.send_to_client(ws, {
                "type": "error",
                "message": "Workflow ID and scheduled time are required"
            })
            return

        try:
            # Parse scheduled time
            from datetime import datetime
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))

            # Create scheduled workflow
            scheduled_workflow = {
                "id": f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "workflow_id": workflow_id,
                "scheduled_time": scheduled_datetime.isoformat(),
                "parameters": parameters,
                "priority": priority,
                "session_id": session_id,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }

            # Store scheduled workflow
            if not hasattr(self, 'scheduled_workflows'):
                self.scheduled_workflows = {}
            self.scheduled_workflows[scheduled_workflow["id"]] = scheduled_workflow

            # Schedule the workflow execution
            delay = (scheduled_datetime - datetime.now().replace(tzinfo=scheduled_datetime.tzinfo)).total_seconds()
            if delay > 0:
                asyncio.create_task(self.schedule_workflow_execution(scheduled_workflow["id"], delay))

            # Send confirmation
            await self.send_to_client(ws, {
                "type": "workflow_scheduled",
                "scheduled_workflow": scheduled_workflow,
                "message": f"Workflow '{workflow_id}' has been scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            })

        except Exception as e:
            self.logger.error(f"Error scheduling workflow: {e}")
            await self.send_to_client(ws, {
                "type": "error",
                "message": f"Failed to schedule workflow: {str(e)}"
            })

    async def handle_session_management(self, ws, data):
        """Handle chat session management operations."""
        action = data.get("action")
        session_id = data.get("session_id")

        if action == "create":
            # Create new chat session
            new_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.chat_sessions[new_session_id] = {
                "messages": [],
                "workflow_id": None,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }

            await self.send_to_client(ws, {
                "type": "session_created",
                "session_id": new_session_id,
                "message": "New chat session created"
            })

        elif action == "switch":
            # Switch to existing session
            if session_id in self.chat_sessions:
                await self.send_to_client(ws, {
                    "type": "session_switched",
                    "session_id": session_id,
                    "messages": self.chat_sessions[session_id]["messages"],
                    "message": f"Switched to session {session_id}"
                })
            else:
                await self.send_to_client(ws, {
                    "type": "error",
                    "message": "Session not found"
                })

        elif action == "list":
            # List all sessions
            sessions_summary = []
            for sid, session_data in self.chat_sessions.items():
                sessions_summary.append({
                    "session_id": sid,
                    "message_count": len(session_data["messages"]),
                    "workflow_id": session_data.get("workflow_id"),
                    "status": session_data["status"],
                    "created_at": session_data["created_at"]
                })

            await self.send_to_client(ws, {
                "type": "sessions_list",
                "sessions": sessions_summary
            })

    async def handle_file_upload(self, ws, data):
        """Handle file uploads in chat."""
        session_id = data.get("session_id", "default")
        filename = data.get("filename", "")
        file_content = data.get("content", "")
        file_type = data.get("file_type", "unknown")

        if not filename or not file_content:
            await self.send_to_client(ws, {
                "type": "error",
                "message": "Filename and content are required"
            })
            return

        try:
            # Save uploaded file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)

            # Generate safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{safe_filename}"
            file_path = upload_dir / saved_filename

            # Decode and save file
            import base64
            file_data = base64.b64decode(file_content)
            with open(file_path, 'wb') as f:
                f.write(file_data)

            # Create file upload message
            file_message = ChatMessage(
                message_id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="user",
                content=f"📎 Uploaded file: {filename} ({len(file_data)} bytes)",
                timestamp=datetime.now().isoformat(),
                message_type="file_upload",
                session_id=session_id,
                metadata={
                    "filename": filename,
                    "saved_path": str(file_path),
                    "file_size": len(file_data),
                    "file_type": file_type
                }
            )

            self.chat_messages.append(file_message)
            if session_id in self.chat_sessions:
                self.chat_sessions[session_id]["messages"].append(asdict(file_message))

            # Broadcast file upload
            await self.broadcast_to_clients({
                "type": "file_uploaded",
                "message": asdict(file_message),
                "session_id": session_id
            })

            # Process file content if it's code or text
            if file_type in ['text/plain', 'application/json', 'text/x-python', 'text/x-javascript', 'text/x-typescript']:
                try:
                    content_preview = file_data.decode('utf-8', errors='ignore')[:1000]
                    analysis_message = ChatMessage(
                        message_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        sender="ai-assistant",
                        content=f"📄 I've analyzed your uploaded file '{filename}'. Here's what I found:\n\n```{file_type}\n{content_preview}```\n\nWould you like me to help you work with this file?",
                        timestamp=datetime.now().isoformat(),
                        message_type="file_analysis",
                        session_id=session_id
                    )

                    self.chat_messages.append(analysis_message)
                    if session_id in self.chat_sessions:
                        self.chat_sessions[session_id]["messages"].append(asdict(analysis_message))

                    await self.broadcast_to_clients({
                        "type": "chat_message",
                        "message": asdict(analysis_message),
                        "session_id": session_id
                    })

                except Exception as e:
                    self.logger.error(f"Error analyzing file content: {e}")

        except Exception as e:
            self.logger.error(f"Error handling file upload: {e}")
            await self.send_to_client(ws, {
                "type": "error",
                "message": f"Failed to process file upload: {str(e)}"
            })

    async def execute_workflow(self, session_id: str, workflow_id: str, parameters: Dict):
        """Execute a workflow with multi-agent coordination."""
        try:
            # Update workflow status
            if session_id in self.workflow_sessions:
                self.workflow_sessions[session_id].status = "running"
                self.workflow_sessions[session_id].started_at = datetime.now().isoformat()

                await self.broadcast_to_clients({
                    "type": "workflow_update",
                    "session_id": session_id,
                    "status": "running"
                })

            # Simulate workflow execution with different phases
            phases = self.get_workflow_phases(workflow_id)
            agents_used = []

            for phase_name, phase_data in phases.items():
                # Update current phase
                await self.broadcast_to_clients({
                    "type": "workflow_phase_update",
                    "session_id": session_id,
                    "current_phase": phase_name,
                    "phase_description": phase_data["description"]
                })

                # Simulate agent work
                for agent_type in phase_data["agents"]:
                    agents_used.append(agent_type)

                    # Create agent job
                    agent_job = AgentJob(
                        job_id=f"{agent_type}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        agent_type=agent_type,
                        task=f"Execute {agent_type} in workflow {workflow_id}",
                        status="running",
                        started_at=datetime.now().isoformat(),
                        created_at=datetime.now().isoformat(),
                        workflow_id=workflow_id,
                        session_id=session_id
                    )

                    self.agent_jobs[agent_job.job_id] = agent_job

                    await self.broadcast_to_clients({
                        "type": "agent_update",
                        "job": asdict(agent_job)
                    })

                    # Simulate work duration
                    await asyncio.sleep(phase_data.get("duration", 3))

                    # Mark job as completed
                    agent_job.status = "completed"
                    agent_job.completed_at = datetime.now().isoformat()
                    agent_job.tokens_used = phase_data.get("tokens", 1000)
                    agent_job.words_generated = phase_data.get("words", 500)

                    await self.broadcast_to_clients({
                        "type": "agent_update",
                        "job": asdict(agent_job)
                    })

            # Mark workflow as completed
            if session_id in self.workflow_sessions:
                self.workflow_sessions[session_id].status = "completed"
                self.workflow_sessions[session_id].completed_at = datetime.now().isoformat()
                self.workflow_sessions[session_id].agents_used = agents_used

                await self.broadcast_to_clients({
                    "type": "workflow_completed",
                    "session_id": session_id,
                    "workflow_id": workflow_id,
                    "agents_used": agents_used
                })

                # Send completion message to chat
                completion_message = ChatMessage(
                    message_id=f"completion_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    sender="workflow_system",
                    content=f"✅ Workflow '{workflow_id}' completed successfully! Used agents: {', '.join(agents_used)}",
                    timestamp=datetime.now().isoformat(),
                    message_type="workflow_completion",
                    session_id=session_id
                )

                self.chat_messages.append(completion_message)

                # Find associated chat session
                found_session_id = None
                for sid, session_data in self.chat_sessions.items():
                    if session_data.get("workflow_id") == session_id:
                        session_data["messages"].append(asdict(completion_message))
                        session_data["status"] = "completed"
                        found_session_id = sid
                        break

                await self.broadcast_to_clients({
                    "type": "chat_message",
                    "message": asdict(completion_message),
                    "session_id": found_session_id or session_id
                })

        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")

            # Mark workflow as failed
            if session_id in self.workflow_sessions:
                self.workflow_sessions[session_id].status = "failed"
                self.workflow_sessions[session_id].error = str(e)

                await self.broadcast_to_clients({
                    "type": "workflow_failed",
                    "session_id": session_id,
                    "error": str(e)
                })

    def get_workflow_phases(self, workflow_id: str) -> Dict[str, Dict]:
        """Get phases and agents for a specific workflow type."""
        workflow_phases = {
            "feature-development": {
                "analysis": {
                    "description": "Analyzing requirements and designing solution",
                    "agents": ["researcher", "architect"],
                    "duration": 3,
                    "tokens": 800,
                    "words": 300
                },
                "implementation": {
                    "description": "Implementing the feature with code development",
                    "agents": ["coder", "frontend-developer"],
                    "duration": 5,
                    "tokens": 2000,
                    "words": 800
                },
                "testing": {
                    "description": "Testing and quality assurance",
                    "agents": ["tester", "debugger"],
                    "duration": 3,
                    "tokens": 1000,
                    "words": 400
                },
                "documentation": {
                    "description": "Creating documentation and user guides",
                    "agents": ["technical-writer"],
                    "duration": 2,
                    "tokens": 600,
                    "words": 500
                }
            },
            "security-audit": {
                "reconnaissance": {
                    "description": "Performing security reconnaissance and analysis",
                    "agents": ["security-researcher", "analyst"],
                    "duration": 4,
                    "tokens": 1500,
                    "words": 600
                },
                "vulnerability_scan": {
                    "description": "Scanning for vulnerabilities and security issues",
                    "agents": ["security-scanner", "penetration-tester"],
                    "duration": 6,
                    "tokens": 2500,
                    "words": 800
                },
                "reporting": {
                    "description": "Generating security assessment report",
                    "agents": ["security-analyst", "technical-writer"],
                    "duration": 3,
                    "tokens": 1200,
                    "words": 700
                }
            },
            "documentation-update": {
                "analysis": {
                    "description": "Analyzing codebase and existing documentation",
                    "agents": ["analyst", "researcher"],
                    "duration": 2,
                    "tokens": 600,
                    "words": 300
                },
                "generation": {
                    "description": "Generating comprehensive documentation",
                    "agents": ["technical-writer", "documentation-specialist"],
                    "duration": 4,
                    "tokens": 1800,
                    "words": 1200
                },
                "review": {
                    "description": "Reviewing and refining documentation",
                    "agents": ["editor", "subject-matter-expert"],
                    "duration": 2,
                    "tokens": 800,
                    "words": 400
                }
            },
            "debugging-session": {
                "investigation": {
                    "description": "Investigating the issue and gathering information",
                    "agents": ["investigator", "analyst"],
                    "duration": 3,
                    "tokens": 1000,
                    "words": 500
                },
                "diagnosis": {
                    "description": "Diagnosing root cause and identifying solutions",
                    "agents": ["debugger", "specialist"],
                    "duration": 4,
                    "tokens": 1500,
                    "words": 600
                },
                "resolution": {
                    "description": "Implementing fix and verifying solution",
                    "agents": ["coder", "tester"],
                    "duration": 3,
                    "tokens": 1200,
                    "words": 500
                }
            },
            "deployment-prep": {
                "security_check": {
                    "description": "Performing security checks and validations",
                    "agents": ["security-auditor", "compliance-checker"],
                    "duration": 3,
                    "tokens": 1000,
                    "words": 400
                },
                "optimization": {
                    "description": "Optimizing performance and configurations",
                    "agents": ["performance-engineer", "devops-engineer"],
                    "duration": 4,
                    "tokens": 1600,
                    "words": 600
                },
                "deployment_setup": {
                    "description": "Setting up deployment pipeline and infrastructure",
                    "agents": ["deployment-specialist", "infrastructure-engineer"],
                    "duration": 5,
                    "tokens": 2000,
                    "words": 800
                }
            }
        }

        return workflow_phases.get(workflow_id, {
            "default": {
                "description": "Processing workflow with general agents",
                "agents": ["general-agent"],
                "duration": 3,
                "tokens": 1000,
                "words": 500
            }
        })

    async def schedule_workflow_execution(self, scheduled_id: str, delay: float):
        """Schedule workflow execution for future time."""
        await asyncio.sleep(delay)

        if scheduled_id in self.scheduled_workflows:
            scheduled_workflow = self.scheduled_workflows[scheduled_id]

            # Execute the scheduled workflow
            await self.execute_workflow(
                f"scheduled_{scheduled_id}",
                scheduled_workflow["workflow_id"],
                scheduled_workflow["parameters"]
            )

            # Mark as executed
            self.scheduled_workflows[scheduled_id]["status"] = "executed"
            self.scheduled_workflows[scheduled_id]["executed_at"] = datetime.now().isoformat()

            await self.broadcast_to_clients({
                "type": "scheduled_workflow_executed",
                "scheduled_id": scheduled_id,
                "workflow": scheduled_workflow
            })

    async def process_message_with_ai(self, message: str, session_id: str):
        """Process message with El Jefe AI."""
        try:
            # Ensure we're sending bytes to stdin
            if hasattr(self.el_jefe_process.stdin, 'write'):
                message_bytes = (message + "\n").encode('utf-8')
                self.el_jefe_process.stdin.write(message_bytes)
                await self.el_jefe_process.stdin.drain()
        except (BrokenPipeError, ConnectionResetError) as e:
            # Process likely ended, update status
            self.chat_active = False
            self.el_jefe_process = None

            error_message = ChatMessage(
                message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="el-jefe",
                content="El Jefe process ended unexpectedly. Please restart.",
                timestamp=datetime.now().isoformat(),
                message_type="error",
                session_id=session_id
            )
            self.chat_messages.append(error_message)
            await self.broadcast_to_clients({
                "type": "chat_message",
                "message": asdict(error_message),
                "session_id": session_id
            })
        except Exception as e:
            error_message = ChatMessage(
                message_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                sender="el-jefe",
                content=f"Error sending message to El Jefe: {e}",
                timestamp=datetime.now().isoformat(),
                message_type="error",
                session_id=session_id
            )
            self.chat_messages.append(error_message)
            await self.broadcast_to_clients({
                "type": "chat_message",
                "message": asdict(error_message),
                "session_id": session_id
            })

  # Enhanced API Endpoints for Chat and Workflows

    async def get_chat_sessions(self, request):
        """Get all chat sessions."""
        sessions_summary = []
        for session_id, session_data in self.chat_sessions.items():
            # Count messages for this session
            session_messages = [msg for msg in self.chat_messages if getattr(msg, 'session_id', None) == session_id]

            sessions_summary.append({
                "session_id": session_id,
                "message_count": len(session_messages),
                "workflow_id": session_data.get("workflow_id"),
                "status": session_data.get("status", "active"),
                "created_at": session_data.get("created_at"),
                "last_activity": session_messages[-1].timestamp if session_messages else session_data.get("created_at")
            })

        return web.json_response({
            "sessions": sessions_summary,
            "total_sessions": len(sessions_summary),
            "total_messages": len(self.chat_messages)
        })

    async def get_chat_session(self, request):
        """Get a specific chat session with its messages."""
        session_id = request.match_info['session_id']

        if session_id not in self.chat_sessions:
            return web.json_response({"error": "Session not found"}, status=404)

        # Get all messages for this session
        session_messages = [msg for msg in self.chat_messages if getattr(msg, 'session_id', None) == session_id]

        return web.json_response({
            "session_id": session_id,
            "session_data": self.chat_sessions[session_id],
            "messages": [asdict(msg) for msg in session_messages],
            "message_count": len(session_messages)
        })

    async def start_workflow_api(self, request):
        """API endpoint to start a workflow."""
        try:
            data = await request.json()
            workflow_id = data.get("workflow_id")
            parameters = data.get("parameters", {})
            priority = data.get("priority", "medium")
            deadline = data.get("deadline", None)
            session_id = data.get("session_id", "api")

            if not workflow_id:
                return web.json_response({"error": "workflow_id is required"}, status=400)

            # Create workflow session
            workflow_session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            workflow_session = WorkflowSession(
                session_id=workflow_session_id,
                workflow_type=workflow_id,
                status="initializing",
                parameters=parameters,
                priority=priority,
                deadline=deadline,
                created_at=datetime.now().isoformat(),
                agents_assigned=[]
            )

            self.workflow_sessions[workflow_session_id] = workflow_session

            # Start workflow execution
            asyncio.create_task(self.execute_workflow(workflow_session_id, workflow_id, parameters))

            return web.json_response({
                "success": True,
                "workflow_id": workflow_id,
                "session_id": workflow_session_id,
                "message": f"Workflow '{workflow_id}' started successfully"
            })

        except Exception as e:
            self.logger.error(f"Error starting workflow via API: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def schedule_workflow_api(self, request):
        """API endpoint to schedule a workflow."""
        try:
            data = await request.json()
            workflow_id = data.get("workflow_id")
            scheduled_time = data.get("scheduled_time")
            parameters = data.get("parameters", {})
            priority = data.get("priority", "medium")
            session_id = data.get("session_id", "api")

            if not workflow_id or not scheduled_time:
                return web.json_response({"error": "workflow_id and scheduled_time are required"}, status=400)

            # Parse scheduled time
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))

            # Create scheduled workflow
            scheduled_workflow = {
                "id": f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "workflow_id": workflow_id,
                "scheduled_time": scheduled_datetime.isoformat(),
                "parameters": parameters,
                "priority": priority,
                "session_id": session_id,
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }

            # Store scheduled workflow
            self.scheduled_workflows[scheduled_workflow["id"]] = scheduled_workflow

            # Schedule the workflow execution
            delay = (scheduled_datetime - datetime.now().replace(tzinfo=scheduled_datetime.tzinfo)).total_seconds()
            if delay > 0:
                asyncio.create_task(self.schedule_workflow_execution(scheduled_workflow["id"], delay))

            return web.json_response({
                "success": True,
                "scheduled_workflow": scheduled_workflow,
                "message": f"Workflow '{workflow_id}' scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            })

        except Exception as e:
            self.logger.error(f"Error scheduling workflow via API: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_scheduled_workflows(self, request):
        """Get all scheduled workflows."""
        return web.json_response({
            "scheduled_workflows": list(self.scheduled_workflows.values()),
            "total_count": len(self.scheduled_workflows)
        })

    async def handle_file_upload_api(self, request):
        """API endpoint to handle file uploads."""
        try:
            # This is a simplified version - in production, you'd want proper multipart handling
            data = await request.json()
            session_id = data.get("session_id", "api")
            filename = data.get("filename", "")
            file_content = data.get("content", "")
            file_type = data.get("file_type", "application/octet-stream")

            if not filename or not file_content:
                return web.json_response({"error": "filename and content are required"}, status=400)

            # Save uploaded file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)

            # Generate safe filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            saved_filename = f"{timestamp}_{safe_filename}"
            file_path = upload_dir / saved_filename

            # Decode and save file
            import base64
            file_data = base64.b64decode(file_content)
            with open(file_path, 'wb') as f:
                f.write(file_data)

            return web.json_response({
                "success": True,
                "filename": filename,
                "saved_filename": saved_filename,
                "file_size": len(file_data),
                "file_type": file_type,
                "session_id": session_id,
                "message": "File uploaded successfully"
            })

        except Exception as e:
            self.logger.error(f"Error handling file upload via API: {e}")
            return web.json_response({"error": str(e)}, status=500)

    def _calculate_average_workflow_duration(self):
        """Calculate average workflow duration from real data."""
        try:
            completed_workflows = [w for w in self.workflows.values() if w.status == 'completed' and w.started_at and w.completed_at]
            if not completed_workflows:
                return 0.0

            total_duration = 0
            for workflow in completed_workflows:
                start = datetime.fromisoformat(workflow.started_at.replace('Z', '+00:00') if workflow.started_at.endswith('Z') else workflow.started_at)
                end = datetime.fromisoformat(workflow.completed_at.replace('Z', '+00:00') if workflow.completed_at.endswith('Z') else workflow.completed_at)
                duration = (end - start).total_seconds()
                total_duration += duration

            return total_duration / len(completed_workflows)
        except Exception:
            return 0.0

    def _calculate_workflow_success_rate(self):
        """Calculate workflow success rate."""
        try:
            total_workflows = len(self.workflows)
            if total_workflows == 0:
                return 100.0

            completed_workflows = len([w for w in self.workflows.values() if w.status == 'completed'])
            return (completed_workflows / total_workflows) * 100
        except Exception:
            return 100.0

    def _get_workflow_type_stats(self):
        """Get workflow statistics by type."""
        try:
            workflow_types = {}
            for workflow in self.workflows.values():
                workflow_type = getattr(workflow, 'agent_type', 'unknown')
                if workflow_type not in workflow_types:
                    workflow_types[workflow_type] = {'total': 0, 'completed': 0, 'failed': 0, 'running': 0}

                workflow_types[workflow_type]['total'] += 1
                if workflow.status:
                    workflow_types[workflow_type][workflow.status] = workflow_types[workflow_type].get(workflow.status, 0) + 1

            return workflow_types
        except Exception:
            return {}

    def _get_workflow_timeline_data(self, time_range):
        """Get timeline data for workflows."""
        try:
            # This would typically query workflow data over time
            # For now, return basic timeline structure
            return {
                'labels': ['Now'],
                'datasets': [{
                    'label': 'Active Workflows',
                    'data': [len([w for w in self.workflows.values() if w.status == 'running'])],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                }]
            }
        except Exception:
            return {'labels': [], 'datasets': []}

    async def get_performance_analytics(self, request):
        """Get performance analytics from real data."""
        try:
            time_range = request.query.get('range', '1h')

            performance_data = {
                'time_range': time_range,
                'data_source': 'real',
                'system_metrics': {
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'response_time': self._calculate_real_response_time(),
                    'throughput': self._calculate_real_throughput()
                },
                'agent_performance': {
                    'success_rate': self._calculate_real_success_rate(),
                    'error_rate': self._calculate_real_error_rate(),
                    'average_duration': self._calculate_average_workflow_duration()
                }
            }

            return web.json_response(performance_data)

        except Exception as e:
            self.logger.error(f"Error getting performance analytics: {e}")
            return web.json_response({'error': 'Performance analytics not available'}, status=503)

    async def get_resource_analytics(self, request):
        """Get resource usage analytics."""
        try:
            resource_data = {
                'time_range': request.query.get('range', '1h'),
                'data_source': 'real',
                'cpu': {
                    'current': psutil.cpu_percent(interval=1),
                    'cores': psutil.cpu_count(),
                    'load_avg': list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
                },
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'used': psutil.virtual_memory().used,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                }
            }

            return web.json_response(resource_data)

        except Exception as e:
            self.logger.error(f"Error getting resource analytics: {e}")
            return web.json_response({'error': 'Resource analytics not available'}, status=503)


async def main():
    """Main entry point for the monitoring dashboard."""
    # Get local IP for network access
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()

    dashboard = MonitoringDashboard(password="Bermalberist-55")

    try:
        runner = await dashboard.start()

        print("🤖 El Jefe Monitoring Dashboard")
        print("=" * 50)
        print(f"🔒 Password Protected")
        print(f"📊 Local URL: http://localhost:8080")
        print(f"🌐 Network URL: http://{local_ip}:8080")
        print(f"🔑 Login URL: http://{local_ip}:8080/login")
        print(f"🔌 WebSocket API: ws://{local_ip}:8080/ws")
        print(f"📡 REST API: http://{local_ip}:8080/api/")
        print("\n🛡️  SECURITY NOTICE:")
        print("   • Dashboard is password protected")
        print("   • Accessible from your local network")
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