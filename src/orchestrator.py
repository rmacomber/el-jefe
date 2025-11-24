"""
Main Orchestrator Module

Coordinates the entire workflow, breaking down tasks, spawning agents,
and managing the complete execution pipeline.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
import aiofiles

from .workspace_manager import WorkspaceManager
from .agent_manager import AgentManager, AgentType
from .task_planner import TaskPlanner
from .user_interface import UserInterface

# Import shared monitoring state for dashboard integration
try:
    from .shared_monitoring_state import add_agent_job, add_workflow_session, get_shared_monitoring_state
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class Orchestrator:
    """
    Main orchestrator that coordinates agents and manages workflows.
    """

    def __init__(self, base_dir: str = "workspaces", interactive: bool = True):
        """
        Initialize the orchestrator.

        Args:
            base_dir: Base directory for workspaces
            interactive: Whether to prompt for user confirmation
        """
        self.workspace_manager = WorkspaceManager(base_dir)
        self.interactive = interactive
        self.user_interface = UserInterface() if interactive else None
        self.task_planner = TaskPlanner()

        # Runtime state
        self.current_workspace: Optional[Path] = None
        self.agent_manager: Optional[AgentManager] = None
        self.workflow_state: Dict[str, Any] = {}

    async def execute_goal(self, goal: str) -> Dict[str, Any]:
        """
        Execute a complete goal from start to finish.

        Args:
            goal: High-level goal description

        Returns:
            Dictionary containing execution results and summary
        """
        results = []
        summary = None

        try:
            # Step 1: Parse and validate the goal
            print(f"\n🎯 Goal: {goal}")

            # Step 2: Create workspace
            task_name = self._extract_task_name(goal)
            workspace_info = await self.workspace_manager.create_workspace(
                task_name=task_name,
                task_description=goal
            )
            self.current_workspace = Path(workspace_info["path"])
            self.agent_manager = AgentManager(self.current_workspace)

            print(f"📁 Created workspace: {self.current_workspace}")

            # Step 3: Plan the task breakdown
            task_plan = await self.task_planner.create_task_plan(goal)
            print(f"📋 Planned {len(task_plan['steps'])} workflow steps")

            # Initialize workflow state
            self.workflow_state = {
                "goal": goal,
                "task_plan": task_plan,
                "workspace": workspace_info,
                "execution_start": datetime.now().isoformat(),
                "steps_completed": [],
                "current_step": 0,
                "status": "running"
            }

            # Register workflow with monitoring dashboard
            if MONITORING_AVAILABLE:
                workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                session_data = {
                    "session_id": workflow_id,
                    "goal": goal,
                    "status": "running",
                    "started_at": datetime.now().isoformat(),
                    "total_steps": len(task_plan['steps']),
                    "completed_steps": 0,
                    "current_step": 0,
                    "agents_used": [],
                    "workspace": str(self.current_workspace),
                    "metrics": {}
                }
                add_workflow_session(session_data)
                self.workflow_state["monitoring_id"] = workflow_id

            # Step 4: Execute workflow steps
            for i, step in enumerate(task_plan["steps"]):
                self.workflow_state["current_step"] = i

                print(f"\n⚡ Step {i+1}/{len(task_plan['steps'])}: {step['description']}")

                # Check for user approval if needed
                if self.interactive and step.get("requires_approval", False):
                    approved = await self._request_approval(step)
                    if not approved:
                        print("❌ Step cancelled by user")
                        continue

                # Register step with monitoring dashboard
                if MONITORING_AVAILABLE and "monitoring_id" in self.workflow_state:
                    job_id = f"{self.workflow_state['monitoring_id']}_step_{i+1}"
                    job_data = {
                        "job_id": job_id,
                        "agent_type": step["agent_type"],
                        "task": step["task"],
                        "status": "running",
                        "started_at": datetime.now().isoformat(),
                        "progress": 0.0,
                        "current_step": "Starting...",
                        "workspace": str(self.current_workspace),
                        "tokens_used": 0,
                        "words_generated": 0
                    }
                    add_agent_job(job_data)

                # Execute the step
                step_result = await self._execute_workflow_step(step)
                results.append(step_result)
                self.workflow_state["steps_completed"].append(step_result)

                # Update monitoring dashboard with step completion
                if MONITORING_AVAILABLE and "monitoring_id" in self.workflow_state:
                    completion_data = {
                        "job_id": job_id,
                        "status": "completed" if step_result.get("status") == "completed" else "failed",
                        "completed_at": datetime.now().isoformat(),
                        "progress": 1.0,
                        "tokens_used": step_result.get("tokens_used", 0),
                        "words_generated": step_result.get("words_generated", 0)
                    }
                    add_agent_job(completion_data)

                # Update workspace context
                await self._update_workspace_context(step_result)

            # Step 5: Mark execution end time and generate final summary
            self.workflow_state["execution_end"] = datetime.now().isoformat()
            summary = await self._generate_final_summary(results)

            # Update final state
            self.workflow_state.update({
                "status": "completed",
                "total_steps": len(results),
                "summary": summary
            })

            # Notify monitoring dashboard of workflow completion
            if MONITORING_AVAILABLE and "monitoring_id" in self.workflow_state:
                completion_data = {
                    "session_id": self.workflow_state["monitoring_id"],
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "total_steps": len(results),
                    "completed_steps": len(results),
                    "current_step": len(results),
                    "workspace": str(self.current_workspace),
                    "metrics": {
                        "total_agents": len(set(step.get("agent_type", "unknown") for step in task_plan["steps"])),
                        "summary": summary
                    }
                }
                add_workflow_session(completion_data)

            print(f"\n✅ Goal completed! Workspace: {self.current_workspace}")
            print(f"📊 Executed {len(results)} steps")

        except Exception as e:
            # Ensure execution_end is set even on error
            if "execution_end" not in self.workflow_state:
                self.workflow_state["execution_end"] = datetime.now().isoformat()

            # Update error state
            self.workflow_state.update({
                "status": "failed",
                "error": str(e),
                "total_steps": len(results)
            })

            # Notify monitoring dashboard of workflow failure
            if MONITORING_AVAILABLE and "monitoring_id" in self.workflow_state:
                failure_data = {
                    "session_id": self.workflow_state["monitoring_id"],
                    "status": "failed",
                    "completed_at": datetime.now().isoformat(),
                    "total_steps": len(results),
                    "completed_steps": len(results),
                    "current_step": self.workflow_state.get("current_step", 0),
                    "workspace": str(self.current_workspace) if self.current_workspace else "",
                    "metrics": {
                        "error": str(e),
                        "summary": "Workflow failed due to an error"
                    }
                }
                add_workflow_session(failure_data)

            print(f"\n❌ Error during execution: {e}")
            raise

        finally:
            # Always save final workflow state and clean up
            if self.workflow_state:
                await self._save_workflow_state()

        return {
            "goal": goal,
            "workspace": str(self.current_workspace) if self.current_workspace else "unknown",
            "results": results,
            "summary": summary or {},
            "workflow_state": self.workflow_state
        }

    def _extract_task_name(self, goal: str) -> str:
        """
        Extract a concise task name from the goal description.

        Args:
            goal: Full goal description

        Returns:
            Concise task name
        """
        # Take first 5 words and clean up
        words = goal.strip().split()[:5]
        task_name = "-".join(words).lower()
        # Remove special characters
        task_name = re.sub(r'[^a-z0-9\-]', '', task_name)
        return task_name or "task"

    async def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        Args:
            step: Step configuration dictionary

        Returns:
            Step execution result
        """
        step_result = {
            "step_id": step.get("id", "unknown"),
            "description": step["description"],
            "agent_type": step["agent_type"],
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }

        try:
            # Determine context files for this step
            context_files = step.get("context_files", [])

            # Add outputs from previous steps as context
            for completed_step in self.workflow_state["steps_completed"]:
                if completed_step.get("output_file"):
                    context_files.append(completed_step["output_file"])

            # Spawn the agent
            agent_result = await self.agent_manager.spawn_agent(
                agent_type=AgentType(step["agent_type"]),
                task_description=step["task"],
                context_files=context_files,
                output_file=step.get("output_file"),
                custom_instructions=step.get("custom_instructions")
            )

            # Update step result with agent result
            step_result.update({
                "status": "completed" if agent_result["status"] == "completed" else "failed",
                "completed_at": datetime.now().isoformat(),
                "agent_result": agent_result,
                "output_file": agent_result.get("output_file")
            })

            print(f"  ✓ {step['description']} - {agent_result['status']}")

            return step_result

        except Exception as e:
            step_result.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            print(f"  ✗ {step['description']} - Error: {e}")
            return step_result

    async def _request_approval(self, step: Dict[str, Any]) -> bool:
        """
        Request user approval for a step.

        Args:
            step: Step configuration

        Returns:
            True if approved, False otherwise
        """
        if not self.user_interface:
            return True

        return await self.user_interface.request_approval(
            f"Execute step: {step['description']}?\n"
            f"Agent: {step['agent_type']}\n"
            f"Task: {step['task']}"
        )

    async def _update_workspace_context(self, step_result: Dict[str, Any]):
        """
        Update the workspace context with step results.

        Args:
            step_result: Result from the completed step
        """
        # Add to agents section
        if step_result["status"] == "completed":
            agent_info = f"- {step_result['agent_type']} agent: {step_result['description']} (✓)"
            await self.workspace_manager.update_context(
                self.current_workspace,
                "Agents and Roles",
                agent_info
            )

        # Add to progress summary
        progress_info = f"- {step_result['description']}: {step_result['status']}"
        await self.workspace_manager.update_context(
            self.current_workspace,
            "Progress Summary",
            progress_info
        )

    async def _generate_final_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a final summary of all work done.

        Args:
            results: List of all step results

        Returns:
            Summary dictionary
        """
        # Get workspace summary
        workspace_summary = await self.workspace_manager.get_workspace_summary(
            self.current_workspace
        )

        # Compile execution statistics
        completed_steps = sum(1 for r in results if r["status"] == "completed")
        failed_steps = sum(1 for r in results if r["status"] == "failed")
        agents_used = list(set(r["agent_type"] for r in results))

        # Calculate execution time properly
        start_time = datetime.fromisoformat(self.workflow_state["execution_start"])

        # Use current time as fallback if execution_end is not set
        if "execution_end" in self.workflow_state:
            end_time = datetime.fromisoformat(self.workflow_state["execution_end"])
        else:
            end_time = datetime.now()
            self.workflow_state["execution_end"] = end_time.isoformat()

        execution_duration = end_time - start_time

        summary = {
            "goal": self.workflow_state["goal"],
            "execution_time": str(execution_duration),
            "total_steps": len(results),
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "success_rate": f"{(completed_steps / len(results) * 100):.1f}%",
            "agents_used": agents_used,
            "workspace_summary": workspace_summary,
            "output_files": [r.get("output_file") for r in results if r.get("output_file")]
        }

        # Write summary to workspace
        summary_path = self.current_workspace / "execution-summary.md"
        summary_content = f"""# Execution Summary

## Goal
{summary['goal']}

## Results
- **Total Steps**: {summary['total_steps']}
- **Completed**: {summary['completed_steps']}
- **Failed**: {summary['failed_steps']}
- **Success Rate**: {summary['success_rate']}

## Agents Used
{chr(10).join(f"- {agent}" for agent in summary['agents_used'])}

## Output Files
{chr(10).join(f"- {file}" for file in summary['output_files'] if file)}

## Workspace Location
{self.current_workspace}

## Next Steps
Review the generated files and context-main.md for complete results.
"""
        async with aiofiles.open(summary_path, 'w') as f:
            await f.write(summary_content)

        return summary

    async def _save_workflow_state(self):
        """Save the complete workflow state to file."""
        state_path = self.current_workspace / "workflow-state.json"
        async with aiofiles.open(state_path, 'w') as f:
            await f.write(json.dumps(self.workflow_state, indent=2))

    async def list_workspaces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent workspaces.

        Args:
            limit: Maximum number of workspaces to return

        Returns:
            List of workspace information
        """
        return await self.workspace_manager.list_workspaces(limit)

    async def resume_workspace(self, workspace_path: str) -> bool:
        """
        Resume work in an existing workspace.

        Args:
            workspace_path: Path to the workspace to resume

        Returns:
            True if successfully resumed, False otherwise
        """
        workspace = Path(workspace_path)
        if not workspace.exists():
            print(f"❌ Workspace not found: {workspace_path}")
            return False

        # Load workflow state
        state_path = workspace / "workflow-state.json"
        if state_path.exists():
            async with aiofiles.open(state_path, 'r') as f:
                self.workflow_state = json.loads(await f.read())

        self.current_workspace = workspace
        self.agent_manager = AgentManager(workspace)

        print(f"📂 Resumed workspace: {workspace}")
        return True

    async def cleanup_old_workspaces(self, days: int = 30):
        """
        Clean up workspaces older than specified days.

        Args:
            days: Age threshold in days
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        cleaned = 0

        for workspace_info in await self.workspace_manager.list_workspaces(100):
            workspace_path = Path(workspace_info["path"])
            if workspace_path.exists():
                # Check creation time
                created_at = datetime.fromisoformat(
                    workspace_info.get("created_at", "1970-01-01")
                ).timestamp()

                if created_at < cutoff_date:
                    import shutil
                    shutil.rmtree(workspace_path)
                    cleaned += 1

        print(f"🧹 Cleaned up {cleaned} old workspaces")