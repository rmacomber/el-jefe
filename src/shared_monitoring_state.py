#!/usr/bin/env python3
"""
Shared Monitoring State

Simple shared state for monitoring El Jefe workflows.
Accessible by both the orchestrator and dashboard.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


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
    agents_used: List[str] = field(default_factory=list)
    workspace: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


class SharedMonitoringState:
    """Shared monitoring state that can be accessed by multiple components."""

    def __init__(self):
        self.agent_jobs: Dict[str, AgentJob] = {}
        self.workflow_sessions: Dict[str, WorkflowSession] = {}
        self._state_file = Path("monitoring_state.json")

    def add_agent_job(self, job_data: Dict[str, Any]):
        """Add or update an agent job."""
        job_id = job_data["job_id"]

        if job_id in self.agent_jobs:
            # Update existing job
            for key, value in job_data.items():
                if hasattr(self.agent_jobs[job_id], key):
                    setattr(self.agent_jobs[job_id], key, value)
        else:
            # Create new job
            self.agent_jobs[job_id] = AgentJob(**job_data)

        self._save_state()

    def add_workflow_session(self, session_data: Dict[str, Any]):
        """Add or update a workflow session."""
        session_id = session_data["session_id"]

        if session_id in self.workflow_sessions:
            # Update existing session
            for key, value in session_data.items():
                if hasattr(self.workflow_sessions[session_id], key):
                    setattr(self.workflow_sessions[session_id], key, value)
        else:
            # Create new session
            self.workflow_sessions[session_id] = WorkflowSession(**session_data)

        self._save_state()

    def get_agent_jobs(self) -> Dict[str, AgentJob]:
        """Get all agent jobs."""
        return self.agent_jobs.copy()

    def get_workflow_sessions(self) -> Dict[str, WorkflowSession]:
        """Get all workflow sessions."""
        return self.workflow_sessions.copy()

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "system": {
                "status": "running",
                "uptime": "active",
                "active_agents": len([j for j in self.agent_jobs.values() if j.status == "running"]),
                "active_workflows": len([w for w in self.workflow_sessions.values() if w.status == "running"]),
                "connected_clients": 0  # This would be managed by the dashboard
            },
            "agents": {job_id: self._dataclass_to_dict(job) for job_id, job in self.agent_jobs.items()},
            "workflows": {session_id: self._dataclass_to_dict(session) for session_id, session in self.workflow_sessions.items()}
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        return {
            "total_jobs": len(self.agent_jobs),
            "completed_jobs": len([j for j in self.agent_jobs.values() if j.status == "completed"]),
            "failed_jobs": len([j for j in self.agent_jobs.values() if j.status == "failed"]),
            "running_jobs": len([j for j in self.agent_jobs.values() if j.status == "running"]),
            "total_workflows": len(self.workflow_sessions),
            "completed_workflows": len([w for w in self.workflow_sessions.values() if w.status == "completed"]),
            "total_tokens": sum(job.tokens_used for job in self.agent_jobs.values()),
            "total_words": sum(job.words_generated for job in self.agent_jobs.values()),
            "average_completion_time": 0.0  # Would need time tracking
        }

    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert a dataclass to a dictionary."""
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj

    def _save_state(self):
        """Save the current state to a file."""
        try:
            state_data = {
                "agent_jobs": {job_id: self._dataclass_to_dict(job) for job_id, job in self.agent_jobs.items()},
                "workflow_sessions": {session_id: self._dataclass_to_dict(session) for session_id, session in self.workflow_sessions.items()},
                "last_updated": datetime.now().isoformat()
            }

            with open(self._state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save monitoring state: {e}")

    def _load_state(self):
        """Load state from a file."""
        try:
            if self._state_file.exists():
                with open(self._state_file, 'r') as f:
                    state_data = json.load(f)

                # Restore agent jobs
                for job_id, job_data in state_data.get("agent_jobs", {}).items():
                    self.agent_jobs[job_id] = AgentJob(**job_data)

                # Restore workflow sessions
                for session_id, session_data in state_data.get("workflow_sessions", {}).items():
                    self.workflow_sessions[session_id] = WorkflowSession(**session_data)

                print(f"✅ Loaded {len(self.workflow_sessions)} workflows and {len(self.agent_jobs)} agent jobs from state file")
            else:
                print(f"ℹ️  No monitoring state file found at {self._state_file}")

        except Exception as e:
            print(f"⚠️  Failed to load monitoring state: {e}")
            import traceback
            traceback.print_exc()


# Global shared monitoring state instance
_shared_state: Optional[SharedMonitoringState] = None


def get_shared_monitoring_state() -> SharedMonitoringState:
    """Get the global shared monitoring state instance."""
    global _shared_state
    if _shared_state is None:
        _shared_state = SharedMonitoringState()
        _shared_state._load_state()
        print(f"🔗 Shared Monitoring State: Loaded {len(_shared_state.workflow_sessions)} workflows and {len(_shared_state.agent_jobs)} agent jobs")
    return _shared_state


# Simple wrapper functions for easy access
def add_agent_job(job_data: Dict[str, Any]):
    """Add an agent job to the shared monitoring state."""
    state = get_shared_monitoring_state()
    state.add_agent_job(job_data)


def add_workflow_session(session_data: Dict[str, Any]):
    """Add a workflow session to the shared monitoring state."""
    state = get_shared_monitoring_state()
    state.add_workflow_session(session_data)


def get_system_status() -> Dict[str, Any]:
    """Get current system status from shared monitoring state."""
    state = get_shared_monitoring_state()
    return state.get_system_status()