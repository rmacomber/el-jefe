#!/usr/bin/env python3
"""
Monitoring Bridge for El Jefe

Connects El Jefe workflows to the monitoring dashboard for real-time visibility.
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class MonitoringBridge:
    """Bridge between El Jefe workflows and monitoring dashboard."""

    def __init__(self, dashboard_url: str = "http://localhost:8080"):
        self.dashboard_url = dashboard_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.workflow_sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_jobs: Dict[str, Dict[str, Any]] = {}

    async def start(self):
        """Start the monitoring bridge."""
        self.session = aiohttp.ClientSession()
        print("🔗 Monitoring Bridge: Connected to dashboard")

    async def stop(self):
        """Stop the monitoring bridge."""
        if self.session:
            await self.session.close()
            print("🔗 Monitoring Bridge: Disconnected from dashboard")

    async def register_workflow(self, workflow_id: str, goal: str, workspace: str):
        """Register a new workflow session."""
        session_data = {
            "session_id": workflow_id,
            "goal": goal,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "total_steps": 0,
            "completed_steps": 0,
            "current_step": 0,
            "agents_used": [],
            "workspace": workspace,
            "metrics": {}
        }

        self.workflow_sessions[workflow_id] = session_data
        await self._notify_dashboard("workflow_started", session_data)

    async def register_step_start(self, workflow_id: str, step_data: Dict[str, Any]):
        """Register the start of a workflow step."""
        if workflow_id not in self.workflow_sessions:
            return

        job_id = f"{workflow_id}_step_{step_data.get('step', 0)}"
        agent_type = step_data.get("agent_type", "unknown")

        job_data = {
            "job_id": job_id,
            "agent_type": agent_type,
            "task": step_data.get("task", ""),
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "progress": 0.0,
            "current_step": "Initializing...",
            "workspace": self.workflow_sessions[workflow_id]["workspace"],
            "tokens_used": 0,
            "words_generated": 0
        }

        self.agent_jobs[job_id] = job_data

        # Update workflow session
        self.workflow_sessions[workflow_id]["current_step"] = step_data.get("step", 0)
        if agent_type not in self.workflow_sessions[workflow_id]["agents_used"]:
            self.workflow_sessions[workflow_id]["agents_used"].append(agent_type)

        await self._notify_dashboard("agent_started", job_data)
        await self._notify_dashboard("workflow_updated", self.workflow_sessions[workflow_id])

    async def update_job_progress(self, workflow_id: str, step: int, progress: float, current_step: str = ""):
        """Update the progress of a running job."""
        job_id = f"{workflow_id}_step_{step}"

        if job_id in self.agent_jobs:
            self.agent_jobs[job_id]["progress"] = progress
            if current_step:
                self.agent_jobs[job_id]["current_step"] = current_step

            await self._notify_dashboard("agent_updated", self.agent_jobs[job_id])

    async def complete_job(self, workflow_id: str, step: int, result: Dict[str, Any]):
        """Mark a job as completed."""
        job_id = f"{workflow_id}_step_{step}"

        if job_id in self.agent_jobs:
            self.agent_jobs[job_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "progress": 1.0,
                "tokens_used": result.get("tokens_used", 0),
                "words_generated": result.get("words_generated", 0)
            })

            await self._notify_dashboard("agent_completed", self.agent_jobs[job_id])

        # Update workflow session
        if workflow_id in self.workflow_sessions:
            self.workflow_sessions[workflow_id]["completed_steps"] += 1

    async def complete_workflow(self, workflow_id: str, final_results: Dict[str, Any]):
        """Mark a workflow as completed."""
        if workflow_id in self.workflow_sessions:
            self.workflow_sessions[workflow_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "metrics": {
                    "total_agents": len(self.workflow_sessions[workflow_id]["agents_used"]),
                    "total_tokens": sum(job.get("tokens_used", 0) for job in self.agent_jobs.values() if workflow_id in job["job_id"]),
                    "total_words": sum(job.get("words_generated", 0) for job in self.agent_jobs.values() if workflow_id in job["job_id"])
                }
            })

            await self._notify_dashboard("workflow_completed", self.workflow_sessions[workflow_id])

    async def fail_workflow(self, workflow_id: str, error: str):
        """Mark a workflow as failed."""
        if workflow_id in self.workflow_sessions:
            self.workflow_sessions[workflow_id].update({
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error_message": error
            })

            await self._notify_dashboard("workflow_failed", self.workflow_sessions[workflow_id])

    async def _notify_dashboard(self, event_type: str, data: Dict[str, Any]):
        """Send notification to the dashboard."""
        if not self.session:
            return

        try:
            # Simplified approach: Directly call dashboard methods
            # Import the dashboard instance and update it directly
            from monitoring_dashboard import MonitoringDashboard

            # This is a simplified approach - in production you might want a more robust communication
            if hasattr(self, '_dashboard_instance'):
                dashboard = self._dashboard_instance

                if event_type in ["agent_started", "agent_updated", "agent_completed"]:
                    await dashboard.update_agent_job(data)
                elif event_type in ["workflow_started", "workflow_updated", "workflow_completed", "workflow_failed"]:
                    await dashboard.update_workflow_session(data)

        except Exception as e:
            print(f"⚠️  Dashboard notification failed: {e}")


# Global monitoring bridge instance
_monitoring_bridge: Optional[MonitoringBridge] = None


async def get_monitoring_bridge() -> MonitoringBridge:
    """Get or create the global monitoring bridge instance."""
    global _monitoring_bridge
    if _monitoring_bridge is None:
        _monitoring_bridge = MonitoringBridge()
        await _monitoring_bridge.start()
    return _monitoring_bridge


async def cleanup_monitoring_bridge():
    """Cleanup the monitoring bridge."""
    global _monitoring_bridge
    if _monitoring_bridge:
        await _monitoring_bridge.stop()
        _monitoring_bridge = None


# Helper functions for easy integration
async def register_workflow(workflow_id: str, goal: str, workspace: str):
    """Register a new workflow."""
    bridge = await get_monitoring_bridge()
    await bridge.register_workflow(workflow_id, goal, workspace)


async def register_step(workflow_id: str, step_data: Dict[str, Any]):
    """Register a workflow step."""
    bridge = await get_monitoring_bridge()
    await bridge.register_step_start(workflow_id, step_data)


async def update_progress(workflow_id: str, step: int, progress: float, current_step: str = ""):
    """Update workflow step progress."""
    bridge = await get_monitoring_bridge()
    await bridge.update_job_progress(workflow_id, step, progress, current_step)


async def complete_step(workflow_id: str, step: int, result: Dict[str, Any]):
    """Complete a workflow step."""
    bridge = await get_monitoring_bridge()
    await bridge.complete_job(workflow_id, step, result)


async def complete_workflow(workflow_id: str, results: Dict[str, Any]):
    """Complete a workflow."""
    bridge = await get_monitoring_bridge()
    await bridge.complete_workflow(workflow_id, results)