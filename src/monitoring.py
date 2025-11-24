"""
Real-time Agent Progress Monitoring System

Provides live monitoring and interruptible execution capabilities for agent workflows.
Supports background monitoring tasks, progress streaming, and dynamic workflow modification.
"""

import asyncio
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import time

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


@dataclass
class AgentStatus:
    """Real-time status of an active agent."""
    agent_id: str
    agent_type: str
    task: str
    status: str  # 'starting', 'running', 'paused', 'completed', 'failed', 'interrupted'
    progress: float  # 0.0 to 1.0
    current_step: str
    total_steps: int
    current_step_index: int
    started_at: datetime
    last_activity: datetime
    workspace_path: str
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    session_id: Optional[str] = None


@dataclass
class WorkflowSession:
    """Represents a monitoring session for agent workflows."""
    session_id: str
    created_at: datetime
    active_agents: Dict[str, AgentStatus]
    conversation_context: Dict[str, Any]
    workspace_path: str
    status: str  # 'active', 'paused', 'completed', 'failed'
    metadata: Dict[str, Any]


class ProgressMonitor:
    """Real-time progress monitoring system for agent workflows."""

    def __init__(self):
        self.active_sessions: Dict[str, WorkflowSession] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.progress_callbacks: List[Callable[[AgentStatus], None]] = []
        self.session_file = Path("monitoring_state.json")
        self.running = False

        # Load existing sessions if file exists
        self._load_sessions()

    def start_monitoring(self):
        """Start the background monitoring system."""
        self.running = True
        asyncio.create_task(self._monitoring_loop())

    def stop_monitoring(self):
        """Stop the background monitoring system."""
        self.running = False

    def add_progress_callback(self, callback: Callable[[AgentStatus], None]):
        """Add a callback for progress updates."""
        self.progress_callbacks.append(callback)

    def create_session(self, session_id: str, workspace_path: str) -> WorkflowSession:
        """Create a new monitoring session."""
        session = WorkflowSession(
            session_id=session_id,
            created_at=datetime.now(),
            active_agents={},
            conversation_context={},
            workspace_path=workspace_path,
            status='active',
            metadata={}
        )
        self.active_sessions[session_id] = session
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[WorkflowSession]:
        """Get a monitoring session by ID."""
        return self.active_sessions.get(session_id)

    async def start_agent_monitoring(
        self,
        session_id: str,
        agent_type: str,
        task: str,
        options: ClaudeAgentOptions,
        total_steps: int = 5
    ) -> str:
        """Start monitoring a new agent execution."""

        agent_id = f"{agent_type}_{datetime.now().strftime('%H%M%S')}"

        # Create agent status
        agent_status = AgentStatus(
            agent_id=agent_id,
            agent_type=agent_type,
            task=task,
            status='starting',
            progress=0.0,
            current_step="",
            total_steps=total_steps,
            current_step_index=0,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            workspace_path=self.active_sessions[session_id].workspace_path,
            messages=[],
            metadata={},
            session_id=session_id
        )

        # Add to session
        self.active_sessions[session_id].active_agents[agent_id] = agent_status

        # Notify progress callbacks
        for callback in self.progress_callbacks:
            try:
                callback(agent_status)
            except Exception as e:
                print(f"Error in progress callback: {e}")

        # Save state
        self._save_sessions()

        # Start monitoring task
        monitor_task = asyncio.create_task(
            self._monitor_agent_execution(agent_id, options)
        )
        self.monitoring_tasks[agent_id] = monitor_task

        return agent_id

    async def _monitor_agent_execution(self, agent_id: str, options: ClaudeAgentOptions):
        """Monitor the execution of a specific agent."""
        try:
            # This would integrate with the actual Claude Agent SDK
            # For now, we'll simulate monitoring

            # Update status to running
            agent_status = self._get_agent_status(agent_id)
            if agent_status:
                agent_status.status = 'running'
                agent_status.current_step = f"Executing {agent_status.task}"
                self._notify_progress_callbacks(agent_status)

            # Simulate progress updates
            for step in range(agent_status.total_steps):
                if not self.running:
                    break

                if agent_status.status == 'paused':
                    await asyncio.sleep(1)  # Wait if paused
                    continue

                # Update progress
                agent_status.current_step_index = step
                agent_status.progress = (step + 1) / agent_status.total_steps
                agent_status.current_step = f"Step {step + 1}/{agent_status.total_steps}: {agent_status.task}"
                agent_status.last_activity = datetime.now()

                # Notify callbacks
                self._notify_progress_callbacks(agent_status)

                # Simulate work
                await asyncio.sleep(2)

                # Save state periodically
                if step % 2 == 0:  # Every other step
                    self._save_sessions()

            # Complete execution
            if agent_status.status != 'interrupted':
                agent_status.status = 'completed'
                agent_status.progress = 1.0
                agent_status.current_step = "Completed"
                agent_status.last_activity = datetime.now()

            self._notify_progress_callbacks(agent_status)
            self._save_sessions()

        except Exception as e:
            print(f"Error monitoring agent {agent_id}: {e}")
            agent_status = self._get_agent_status(agent_id)
            if agent_status:
                agent_status.status = 'failed'
                agent_status.last_activity = datetime.now()
                self._notify_progress_callbacks(agent_status)
                self._save_sessions()

        finally:
            # Clean up monitoring task
            if agent_id in self.monitoring_tasks:
                del self.monitoring_tasks[agent_id]

    async def interrupt_agent(self, agent_id: str, reason: str = "User requested interruption") -> bool:
        """Interrupt a running agent."""
        agent_status = self._get_agent_status(agent_id)

        if not agent_status or agent_id not in self.monitoring_tasks:
            return False

        if agent_status.status in ['running']:
            agent_status.status = 'interrupted'
            agent_status.metadata['interruption_reason'] = reason
            agent_status.last_activity = datetime.now()

            self._notify_progress_callbacks(agent_status)
            self._save_sessions()

            # Cancel monitoring task
            if agent_id in self.monitoring_tasks:
                self.monitoring_tasks[agent_id].cancel()
                del self.monitoring_tasks[agent_id]

            return True

        return False

    async def pause_agent(self, agent_id: str) -> bool:
        """Pause a running agent."""
        agent_status = self._get_agent_status(agent_id)

        if not agent_status:
            return False

        if agent_status.status in ['running']:
            agent_status.status = 'paused'
            agent_status.last_activity = datetime.now()
            self._notify_progress_callbacks(agent_status)
            self._save_sessions()
            return True

        return False

    async def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent."""
        agent_status = self._get_agent_status(agent_id)

        if not agent_status:
            return False

        if agent_status.status == 'paused':
            agent_status.status = 'running'
            agent_status.last_activity = datetime.now()
            self._notify_progress_callbacks(agent_status)
            self._save_sessions()

            # Restart monitoring if task was cancelled
            if agent_id not in self.monitoring_tasks:
                options = ClaudeAgentOptions()  # Would be passed from caller
                monitor_task = asyncio.create_task(
                    self._monitor_agent_execution(agent_id, options)
                )
                self.monitoring_tasks[agent_id] = monitor_task

            return True

        return False

    def get_all_agent_status(self) -> Dict[str, AgentStatus]:
        """Get status of all active agents."""
        all_agents = {}
        for session in self.active_sessions.values():
            for agent_id, agent_status in session.active_agents.items():
                all_agents[agent_id] = agent_status
        return all_agents

    def _get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get agent status by ID."""
        for session in self.active_sessions.values():
            if agent_id in session.active_agents:
                return session.active_agents[agent_id]
        return None

    def _notify_progress_callbacks(self, agent_status: AgentStatus):
        """Notify all progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(agent_status)
            except Exception as e:
                print(f"Error in progress callback: {e}")

    async def _monitoring_loop(self):
        """Background monitoring loop for system health."""
        while self.running:
            try:
                # Check for stale sessions (no activity for 1 hour)
                current_time = datetime.now()
                stale_sessions = []

                for session_id, session in self.active_sessions.items():
                    stale_time = current_time - session.created_at

                    if stale_time > timedelta(hours=1):
                        stale_sessions.append(session_id)

                # Clean up stale sessions
                for session_id in stale_sessions:
                    del self.active_sessions[session_id]

                # Save state periodically
                self._save_sessions()

                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)

    def _save_sessions(self):
        """Save monitoring state to file."""
        try:
            state = {
                'sessions': {sid: asdict(session) for sid, session in self.active_sessions.items()},
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }

            with open(self.session_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving sessions: {e}")

    def _load_sessions(self):
        """Load monitoring state from file."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    state = json.load(f)

                if 'sessions' in state:
                    for session_id, session_data in state['sessions'].items():
                        # Convert dictionaries back to dataclasses
                        session = WorkflowSession(
                            session_id=session_data['session_id'],
                            created_at=datetime.fromisoformat(session_data['created_at']),
                            active_agents={
                                agent_id: AgentStatus(**agent_data)
                                for agent_id, agent_data in session_data['active_agents'].items()
                            },
                            conversation_context=session_data['conversation_context'],
                            workspace_path=session_data['workspace_path'],
                            status=session_data['status'],
                            metadata=session_data['metadata']
                        )

                        # Convert timestamps
                        for agent in session.active_agents.values():
                            agent.started_at = datetime.fromisoformat(agent.started_at)
                            agent.last_activity = datetime.fromisoformat(agent.last_activity)

                        self.active_sessions[session_id] = session

        except Exception as e:
            print(f"Error loading sessions: {e}")
            self.active_sessions = {}  # Start with empty state