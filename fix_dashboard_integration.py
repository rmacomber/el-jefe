#!/usr/bin/env python3
"""
Fix Dashboard Integration

Simple script to fix the El Jefe dashboard integration issue.
Updates the shared monitoring state to work with the current dashboard.
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any

class DashboardUpdater:
    """Simple updater for the monitoring dashboard."""

    def __init__(self, dashboard_url: str = "http://localhost:8080"):
        self.dashboard_url = dashboard_url
        self.session = None

    async def start(self):
        """Start the dashboard updater."""
        self.session = aiohttp.ClientSession()

    async def stop(self):
        """Stop the dashboard updater."""
        if self.session:
            await self.session.close()

    async def update_dashboard(self, data: Dict[str, Any]):
        """Update the dashboard with workflow data."""
        if not self.session:
            return

        try:
            # Create a simple monitoring state file that the dashboard can read
            monitoring_state = {
                "agent_jobs": data.get("agent_jobs", {}),
                "workflow_sessions": data.get("workflow_sessions", {}),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }

            # Save to monitoring state file
            with open("monitoring_state.json", "w") as f:
                json.dump(monitoring_state, f, indent=2)

            print(f"📊 Updated dashboard with {len(data.get('workflow_sessions', {}))} workflows")

        except Exception as e:
            print(f"❌ Failed to update dashboard: {e}")


async def test_dashboard_update():
    """Test updating the dashboard with sample data."""
    updater = DashboardUpdater()
    await updater.start()

    # Create sample workflow data
    test_data = {
        "workflow_sessions": {
            "workflow_2025_11_24_research": {
                "session_id": "workflow_2025_11_24_research",
                "goal": "Research Python frameworks like Django and Flask",
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "total_steps": 3,
                "completed_steps": 1,
                "current_step": 1,
                "agents_used": ["researcher"],
                "workspace": "workspaces/test",
                "metrics": {}
            }
        },
        "agent_jobs": {
            "workflow_2025_11_24_research_step_1": {
                "job_id": "workflow_2025_11_24_research_step_1",
                "agent_type": "researcher",
                "task": "Research information about Python web frameworks",
                "status": "completed",
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "progress": 1.0,
                "current_step": "Research completed",
                "workspace": "workspaces/test",
                "tokens_used": 1500,
                "words_generated": 750
            }
        }
    }

    await updater.update_dashboard(test_data)
    await updater.stop()

    print("✅ Test update completed. Check the dashboard!")


if __name__ == "__main__":
    asyncio.run(test_dashboard_update())