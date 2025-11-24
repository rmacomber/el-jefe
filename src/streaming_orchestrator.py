"""
Streaming Orchestrator with Real-Time Monitoring

Enhanced orchestrator that provides real-time workflow streaming,
advanced monitoring integration, and dynamic workflow modification.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncIterator
from pathlib import Path
import uuid

from .enhanced_agent_manager import StreamingAgentManager, StreamingAgentOptions
from .agent_manager import AgentType, AgentConfig
from .monitoring import ProgressMonitor, AgentStatus
from .workspace_manager import WorkspaceManager
from .task_planner import TaskPlanner


class StreamingOrchestrator:
    """
    Enhanced orchestrator with real-time streaming capabilities
    and integrated monitoring.
    """

    def __init__(
        self,
        base_dir: str = "workspaces",
        enable_monitoring: bool = True,
        enable_streaming: bool = True
    ):
        """
        Initialize the streaming orchestrator.

        Args:
            base_dir: Base directory for workspaces
            enable_monitoring: Enable real-time progress monitoring
            enable_streaming: Enable streaming output capabilities
        """
        self.workspace_manager = WorkspaceManager(base_dir)
        self.enable_monitoring = enable_monitoring
        self.enable_streaming = enable_streaming
        self.task_planner = TaskPlanner()

        # Initialize monitoring system
        self.monitor = ProgressMonitor() if enable_monitoring else None

        # Active workflows tracking
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.active_sessions: Dict[str, StreamingAgentManager] = {}

        # Start monitoring system
        if self.monitor:
            self.monitor.start_monitoring()

    async def execute_goal_streaming(
        self,
        goal: str,
        session_id: Optional[str] = None,
        enable_parallel: bool = False
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a goal with real-time streaming output.

        Args:
            goal: High-level goal description
            session_id: Optional session ID for tracking
            enable_parallel: Enable parallel agent execution when possible

        Yields:
            Real-time updates including:
            - Workflow start/completion events
            - Step start/completion events
            - Agent text chunks
            - Tool usage events
            - Progress updates
            - Metrics and performance data
        """
        # Create session ID if not provided
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

        # Create workspace
        task_name = goal.lower().replace(" ", "-")[:20]
        workspace_info = await self.workspace_manager.create_workspace(
            task_name=task_name,
            task_description=goal
        )
        workspace_path = Path(workspace_info["path"])

        # Initialize monitoring callback
        async def monitoring_callback(agent_status: AgentStatus):
            """Handle agent status updates from monitoring."""
            if self.monitor:
                # Update monitoring system
                self.monitor._notify_progress_callbacks(agent_status)

        # Initialize agent manager
        agent_manager = StreamingAgentManager(
            workspace_path,
            monitoring_callback=monitoring_callback if self.enable_monitoring else None
        )

        # Store active session
        self.active_sessions[session_id] = agent_manager

        # Create monitoring session
        if self.monitor:
            monitor_session = self.monitor.create_session(session_id, str(workspace_path))

        # Workflow state
        workflow_state = {
            "session_id": session_id,
            "goal": goal,
            "workspace": str(workspace_path),
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "current_step": 0,
            "status": "running",
            "enable_parallel": enable_parallel
        }

        # Store active workflow
        self.active_workflows[session_id] = workflow_state

        # Yield workflow start event
        yield {
            "type": "workflow_started",
            "session_id": session_id,
            "goal": goal,
            "workspace": str(workspace_path),
            "enable_parallel": enable_parallel,
            "timestamp": datetime.now().isoformat(),
            "monitoring_enabled": self.enable_monitoring,
            "streaming_enabled": self.enable_streaming
        }

        try:
            # Determine workflow steps
            task_plan = await self.task_planner.create_task_plan(goal)
            steps = task_plan["steps"]
            workflow_state["steps"] = steps

            # Yield step planning completed event
            yield {
                "type": "workflow_planned",
                "session_id": session_id,
                "total_steps": len(steps),
                "steps": [
                    {
                        "step": i + 1,
                        "description": step["description"],
                        "agent_type": step["agent_type"],
                        "estimated_duration": step.get("estimated_duration", "unknown")
                    }
                    for i, step in enumerate(steps)
                ],
                "timestamp": datetime.now().isoformat()
            }

            # Execute steps (with parallelization if enabled)
            if enable_parallel and self._can_parallelize(steps):
                async for update in self._execute_parallel_workflow(
                    session_id, steps, agent_manager, workspace_path
                ):
                    yield update
            else:
                async for update in self._execute_sequential_workflow(
                    session_id, steps, agent_manager, workspace_path
                ):
                    yield update

            # Generate workflow completion summary
            workflow_metrics = agent_manager.get_workflow_metrics()

            # Update workflow state
            workflow_state.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "total_steps": len(steps),
                "metrics": workflow_metrics
            })

            # Yield workflow completion event
            yield {
                "type": "workflow_completed",
                "session_id": session_id,
                "goal": goal,
                "workspace": str(workspace_path),
                "total_steps": len(steps),
                "metrics": workflow_metrics,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Handle workflow error
            workflow_state.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })

            yield {
                "type": "workflow_error",
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

        finally:
            # Cleanup
            if session_id in self.active_sessions:
                await self.active_sessions[session_id].cleanup()
                del self.active_sessions[session_id]

    async def _execute_sequential_workflow(
        self,
        session_id: str,
        steps: List[Dict[str, Any]],
        agent_manager: StreamingAgentManager,
        workspace_path: Path
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute workflow steps sequentially."""
        for i, step in enumerate(steps):
            workflow_state = self.active_workflows[session_id]
            workflow_state["current_step"] = i

            # Yield step start event
            yield {
                "type": "step_started",
                "session_id": session_id,
                "step": i + 1,
                "total_steps": len(steps),
                "description": step["description"],
                "agent_type": step["agent_type"],
                "timestamp": datetime.now().isoformat()
            }

            # Configure agent options
            config = AgentConfig.AGENT_CONFIGS[AgentType(step["agent_type"])]
            options = StreamingAgentOptions(
                system_prompt=config["system_prompt"],
                allowed_tools=config["allowed_tools"],
                max_turns=config["max_turns"],
                session_id=session_id,
                on_progress=lambda aid, txt: self._on_agent_progress(session_id, aid, txt)
            )

            # Execute agent with streaming
            agent_outputs = []
            async for update in agent_manager.spawn_streaming_agent(
                agent_type=AgentType(step["agent_type"]),
                task_description=step["task"],
                options=options,
                context_files=step.get("context_files", []),
                output_file=step.get("output_file")
            ):
                # Add session info to all updates
                update["session_id"] = session_id
                update["step"] = i + 1

                # Store agent outputs
                if update["type"] == "text_chunk":
                    agent_outputs.append(update["content"])

                # Yield update
                yield update

            # Yield step completion event
            step_result = {
                "step": i + 1,
                "agent_type": step["agent_type"],
                "output": "".join(agent_outputs),
                "completed_at": datetime.now().isoformat()
            }

            yield {
                "type": "step_completed",
                "session_id": session_id,
                "step": i + 1,
                "result": step_result,
                "timestamp": datetime.now().isoformat()
            }

    async def _execute_parallel_workflow(
        self,
        session_id: str,
        steps: List[Dict[str, Any]],
        agent_manager: StreamingAgentManager,
        workspace_path: Path
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute workflow steps with parallelization where possible."""
        # Group steps that can run in parallel
        parallel_groups = self._group_parallel_steps(steps)

        for group_idx, group in enumerate(parallel_groups):
            if len(group) == 1:
                # Single step - execute sequentially
                async for update in self._execute_sequential_workflow(
                    session_id, group, agent_manager, workspace_path
                ):
                    yield update
            else:
                # Multiple steps - execute in parallel
                yield {
                    "type": "parallel_group_started",
                    "session_id": session_id,
                    "group": group_idx + 1,
                    "total_groups": len(parallel_groups),
                    "agents": [step["agent_type"] for step in group],
                    "timestamp": datetime.now().isoformat()
                }

                # Configure agent options for parallel execution
                agent_configs = []
                for step in group:
                    config = AgentConfig.AGENT_CONFIGS[AgentType(step["agent_type"])]
                    options = StreamingAgentOptions(
                        system_prompt=config["system_prompt"],
                        allowed_tools=config["allowed_tools"],
                        max_turns=config["max_turns"],
                        session_id=session_id
                    )

                    agent_configs.append({
                        "agent_type": AgentType(step["agent_type"]),
                        "task_description": step["task"],
                        "options": options,
                        "context_files": step.get("context_files", []),
                        "output_file": step.get("output_file"),
                        "batch_id": f"group_{group_idx}"
                    })

                # Execute agents in parallel
                async for update in agent_manager.spawn_parallel_agents(agent_configs, session_id):
                    update["session_id"] = session_id
                    update["parallel_group"] = group_idx + 1
                    yield update

                yield {
                    "type": "parallel_group_completed",
                    "session_id": session_id,
                    "group": group_idx + 1,
                    "timestamp": datetime.now().isoformat()
                }

    async def interrupt_workflow(self, session_id: str, reason: str = "User requested interruption") -> bool:
        """Interrupt a running workflow."""
        if session_id not in self.active_sessions:
            return False

        agent_manager = self.active_sessions[session_id]
        workflow_state = self.active_workflows[session_id]

        # Cancel all active agents
        cancelled_agents = []
        for agent_id, task in agent_manager.active_streams.items():
            if not task.done():
                task.cancel()
                cancelled_agents.append(agent_id)

        # Update workflow state
        workflow_state.update({
            "status": "interrupted",
            "interrupted_at": datetime.now().isoformat(),
            "interruption_reason": reason,
            "cancelled_agents": cancelled_agents
        })

        return len(cancelled_agents) > 0

    async def pause_workflow(self, session_id: str) -> bool:
        """Pause a running workflow (experimental)."""
        # This would require more complex implementation with SDK support
        # For now, return not implemented
        return False

    async def resume_workflow(self, session_id: str) -> bool:
        """Resume a paused workflow (experimental)."""
        # This would require more complex implementation with SDK support
        # For now, return not implemented
        return False

    async def modify_workflow(
        self,
        session_id: str,
        modification_type: str,
        modification_data: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Dynamically modify a running workflow.

        Args:
            session_id: Session ID of the workflow
            modification_type: Type of modification ("add_step", "remove_step", "modify_step")
            modification_data: Data for the modification

        Yields:
            Modification update events
        """
        if session_id not in self.active_workflows:
            yield {
                "type": "modification_failed",
                "session_id": session_id,
                "error": "Session not found",
                "timestamp": datetime.now().isoformat()
            }
            return

        workflow_state = self.active_workflows[session_id]

        # Only allow modifications before workflow completes
        if workflow_state.get("status") == "completed":
            yield {
                "type": "modification_failed",
                "session_id": session_id,
                "error": "Cannot modify completed workflow",
                "timestamp": datetime.now().isoformat()
            }
            return

        modification_success = False

        # Apply modification based on type
        if modification_type == "add_step":
            # Add a new step to the workflow
            new_step = modification_data.get("step")
            if new_step and "steps" in workflow_state:
                insert_position = modification_data.get("position", len(workflow_state["steps"]))
                workflow_state["steps"].insert(insert_position, new_step)
                modification_success = True

                yield {
                    "type": "workflow_modified",
                    "session_id": session_id,
                    "modification": "step_added",
                    "step": new_step,
                    "position": insert_position,
                    "timestamp": datetime.now().isoformat()
                }

        elif modification_type == "remove_step":
            # Remove a step from the workflow
            step_index = modification_data.get("step_index")
            if step_index is not None and 0 <= step_index < len(workflow_state.get("steps", [])):
                removed_step = workflow_state["steps"].pop(step_index)
                modification_success = True

                yield {
                    "type": "workflow_modified",
                    "session_id": session_id,
                    "modification": "step_removed",
                    "removed_step": removed_step,
                    "step_index": step_index,
                    "timestamp": datetime.now().isoformat()
                }

        elif modification_type == "modify_step":
            # Modify an existing step
            step_index = modification_data.get("step_index")
            new_step_data = modification_data.get("step_data")

            if (step_index is not None and
                0 <= step_index < len(workflow_state.get("steps", [])) and
                new_step_data):

                workflow_state["steps"][step_index].update(new_step_data)
                modification_success = True

                yield {
                    "type": "workflow_modified",
                    "session_id": session_id,
                    "modification": "step_modified",
                    "step_index": step_index,
                    "new_data": new_step_data,
                    "timestamp": datetime.now().isoformat()
                }

        # If no modification was successful, yield a failure event
        if not modification_success:
            yield {
                "type": "modification_failed",
                "session_id": session_id,
                "error": f"Failed to apply modification: {modification_type}",
                "timestamp": datetime.now().isoformat()
            }

    def get_workflow_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow."""
        if session_id not in self.active_workflows:
            return None

        workflow_state = self.active_workflows[session_id].copy()

        # Add current metrics if agent manager is available
        if session_id in self.active_sessions:
            agent_manager = self.active_sessions[session_id]
            workflow_state["metrics"] = agent_manager.get_workflow_metrics()

        # Add monitoring data if available
        if self.monitor:
            monitor_session = self.monitor.get_session(session_id)
            if monitor_session:
                workflow_state["monitoring"] = {
                    "active_agents": len(monitor_session.active_agents),
                    "session_status": monitor_session.status
                }

        return workflow_state

    def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active workflows."""
        return {
            session_id: self.get_workflow_status(session_id)
            for session_id in self.active_workflows.keys()
        }

    def _can_parallelize(self, steps: List[Dict[str, Any]]) -> bool:
        """Determine if workflow steps can be parallelized."""
        # Simple heuristic: if multiple agents of different types are needed,
        # and they don't depend on each other's output, we can parallelize
        agent_types = [step.get("agent_type") for step in steps]

        # Check for dependency indicators in context files
        has_dependencies = any(
            "context_files" in step and step["context_files"]
            for step in steps
        )

        # Can parallelize if we have different agent types and no clear dependencies
        return len(set(agent_types)) > 1 and not has_dependencies

    def _group_parallel_steps(self, steps: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group steps that can be executed in parallel."""
        # For now, use a simple approach: group by agent type dependencies
        # This could be made much more sophisticated
        parallel_groups = []
        current_group = []
        used_agent_types = set()

        for step in steps:
            agent_type = step.get("agent_type")

            # Check if this agent type has been used in current group
            if agent_type not in used_agent_types:
                current_group.append(step)
                used_agent_types.add(agent_type)
            else:
                # Start new group
                if current_group:
                    parallel_groups.append(current_group)
                current_group = [step]
                used_agent_types = {agent_type}

        # Add last group
        if current_group:
            parallel_groups.append(current_group)

        return parallel_groups

    async def _on_agent_progress(self, session_id: str, agent_id: str, text: str):
        """Handle agent progress updates."""
        # This could be used to trigger events, update UI, etc.
        pass

    async def cleanup(self):
        """Clean up all resources and active sessions."""
        # Cancel all active workflows
        for session_id in list(self.active_sessions.keys()):
            await self.interrupt_workflow(session_id, "System shutdown")

        # Stop monitoring
        if self.monitor:
            self.monitor.stop_monitoring()

        # Clear active sessions
        self.active_sessions.clear()
        self.active_workflows.clear()