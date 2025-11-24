"""
Workflow Scheduler Module

Handles scheduling and execution of recurring and one-time workflows.
Integrates with the orchestrator to run automated tasks at specified intervals.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import aiofiles
from dataclasses import dataclass, asdict
import uuid


class ScheduleType(Enum):
    """Types of scheduling."""
    ONCE = "once"                    # Run once at specific time
    DAILY = "daily"                  # Run every day at specific time
    WEEKLY = "weekly"                # Run weekly on specific day/time
    MONTHLY = "monthly"              # Run monthly on specific day/time
    INTERVAL = "interval"            # Run every N minutes/hours/days
    CRON = "cron"                    # Cron expression


class ScheduleStatus(Enum):
    """Status of scheduled workflows."""
    PENDING = "pending"              # Waiting to run
    RUNNING = "running"              # Currently executing
    COMPLETED = "completed"          # Finished successfully
    FAILED = "failed"                # Failed to execute
    PAUSED = "paused"                # Temporarily stopped
    CANCELLED = "cancelled"          # Permanently stopped


@dataclass
class ScheduledWorkflow:
    """Represents a scheduled workflow."""
    id: str
    name: str
    description: str
    goal: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    status: ScheduleStatus = ScheduleStatus.PENDING
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    workspace_template: Optional[str] = None
    agent_types: List[str] = None
    notifications: Dict[str, bool] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.agent_types is None:
            self.agent_types = []
        if self.notifications is None:
            self.notifications = {"email": False, "desktop": False}
        if self.metadata is None:
            self.metadata = {}


class WorkflowScheduler:
    """Manages scheduled workflow execution."""

    def __init__(self, workspace_path: Path):
        """
        Initialize the scheduler.

        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = workspace_path
        self.scheduled_workflows: Dict[str, ScheduledWorkflow] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduler_file = workspace_path / "scheduled_workflows.json"
        self.logger = logging.getLogger(__name__)
        self._shutdown = False

        # Create scheduler directory
        self.scheduler_dir = workspace_path / "scheduler"
        self.scheduler_dir.mkdir(exist_ok=True)

    async def load_scheduled_workflows(self):
        """Load scheduled workflows from file."""
        try:
            if self.scheduler_file.exists():
                async with aiofiles.open(self.scheduler_file, 'r') as f:
                    data = json.loads(await f.read())

                for workflow_data in data.get('workflows', []):
                    workflow = self._deserialize_workflow(workflow_data)
                    self.scheduled_workflows[workflow.id] = workflow

                self.logger.info(f"Loaded {len(self.scheduled_workflows)} scheduled workflows")
        except Exception as e:
            self.logger.error(f"Error loading scheduled workflows: {e}")

    async def save_scheduled_workflows(self):
        """Save scheduled workflows to file."""
        try:
            data = {
                'workflows': [
                    self._serialize_workflow(workflow)
                    for workflow in self.scheduled_workflows.values()
                ],
                'last_saved': datetime.now().isoformat()
            }

            async with aiofiles.open(self.scheduler_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))

        except Exception as e:
            self.logger.error(f"Error saving scheduled workflows: {e}")

    def _serialize_workflow(self, workflow: ScheduledWorkflow) -> Dict:
        """Serialize workflow to dictionary for JSON storage."""
        data = asdict(workflow)
        # Convert datetime objects to strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, (ScheduleType, ScheduleStatus)):
                data[key] = value.value
        return data

    def _deserialize_workflow(self, data: Dict) -> ScheduledWorkflow:
        """Deserialize workflow from dictionary."""
        # Convert string enums back to enum objects
        if isinstance(data.get('schedule_type'), str):
            data['schedule_type'] = ScheduleType(data['schedule_type'])
        if isinstance(data.get('status'), str):
            data['status'] = ScheduleStatus(data['status'])

        # Convert datetime strings back to datetime objects
        for key in ['created_at', 'last_run', 'next_run']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key])

        return ScheduledWorkflow(**data)

    async def schedule_workflow(
        self,
        name: str,
        description: str,
        goal: str,
        schedule_type: ScheduleType,
        schedule_config: Dict[str, Any],
        max_runs: Optional[int] = None,
        workspace_template: Optional[str] = None,
        agent_types: Optional[List[str]] = None,
        notifications: Optional[Dict[str, bool]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a new workflow.

        Args:
            name: Name of the workflow
            description: Description of what the workflow does
            goal: The goal/task description for the orchestrator
            schedule_type: Type of scheduling (daily, weekly, etc.)
            schedule_config: Configuration for the schedule
            max_runs: Maximum number of times to run (None for infinite)
            workspace_template: Template for workspace naming
            agent_types: List of agent types to use
            notifications: Notification preferences
            metadata: Additional metadata

        Returns:
            ID of the scheduled workflow
        """
        workflow_id = str(uuid.uuid4())

        # Create scheduled workflow
        workflow = ScheduledWorkflow(
            id=workflow_id,
            name=name,
            description=description,
            goal=goal,
            schedule_type=schedule_type,
            schedule_config=schedule_config,
            max_runs=max_runs,
            workspace_template=workspace_template,
            agent_types=agent_types or [],
            notifications=notifications or {},
            metadata=metadata or {}
        )

        # Calculate next run time
        workflow.next_run = self._calculate_next_run(workflow)

        # Store workflow
        self.scheduled_workflows[workflow_id] = workflow

        # Save to file
        await self.save_scheduled_workflows()

        self.logger.info(f"Scheduled workflow '{name}' with ID {workflow_id}")
        return workflow_id

    def _calculate_next_run(self, workflow: ScheduledWorkflow) -> Optional[datetime]:
        """Calculate the next run time for a workflow."""
        now = datetime.now()
        config = workflow.schedule_config

        if workflow.schedule_type == ScheduleType.ONCE:
            # Run once at specific time
            if 'run_at' in config:
                run_time = datetime.fromisoformat(config['run_at'])
                return run_time if run_time > now else None

        elif workflow.schedule_type == ScheduleType.DAILY:
            # Run daily at specific time
            hour = config.get('hour', 9)
            minute = config.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif workflow.schedule_type == ScheduleType.WEEKLY:
            # Run weekly on specific day
            day_of_week = config.get('day_of_week', 0)  # 0 = Monday
            hour = config.get('hour', 9)
            minute = config.get('minute', 0)

            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7

            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            next_run += timedelta(days=days_ahead)
            return next_run

        elif workflow.schedule_type == ScheduleType.INTERVAL:
            # Run every N minutes/hours/days
            interval_value = config.get('interval_value', 1)
            interval_unit = config.get('interval_unit', 'hours')

            if workflow.last_run:
                next_run = workflow.last_run
            else:
                next_run = now

            if interval_unit == 'minutes':
                next_run += timedelta(minutes=interval_value)
            elif interval_unit == 'hours':
                next_run += timedelta(hours=interval_value)
            elif interval_unit == 'days':
                next_run += timedelta(days=interval_value)
            else:
                raise ValueError(f"Invalid interval unit: {interval_unit}")

            return next_run

        return None

    async def start_scheduler(self, orchestrator_factory: Callable):
        """
        Start the scheduler loop.

        Args:
            orchestrator_factory: Function to create orchestrator instances
        """
        self.logger.info("Starting workflow scheduler")
        self._shutdown = False

        while not self._shutdown:
            try:
                await self._check_and_run_workflows(orchestrator_factory)
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)

    async def _check_and_run_workflows(self, orchestrator_factory: Callable):
        """Check for workflows that need to run and execute them."""
        now = datetime.now()

        for workflow_id, workflow in self.scheduled_workflows.items():
            if (workflow.status == ScheduleStatus.PENDING and
                workflow.next_run and
                workflow.next_run <= now):

                # Check if we've reached max runs
                if workflow.max_runs and workflow.run_count >= workflow.max_runs:
                    workflow.status = ScheduleStatus.COMPLETED
                    continue

                # Run the workflow
                await self._run_workflow(workflow, orchestrator_factory)

    async def _run_workflow(self, workflow: ScheduledWorkflow, orchestrator_factory: Callable):
        """Execute a scheduled workflow."""
        workflow.status = ScheduleStatus.RUNNING
        workflow.last_run = datetime.now()
        workflow.run_count += 1

        self.logger.info(f"Running scheduled workflow: {workflow.name}")

        try:
            # Create orchestrator instance
            orchestrator = orchestrator_factory()

            # Generate workspace name if template provided
            goal = workflow.goal
            if workflow.workspace_template:
                timestamp = workflow.last_run.strftime("%Y%m%d-%H%M%S")
                workspace_name = workflow.workspace_template.format(
                    name=workflow.name.replace(' ', '-').lower(),
                    timestamp=timestamp,
                    date=workflow.last_run.strftime("%Y-%m-%d")
                )
                # We'll need to modify the orchestrator to accept workspace name
                # For now, just use the goal
                goal = f"{workflow.goal} (Workspace: {workspace_name})"

            # Run the orchestrator
            async for update in orchestrator.execute_goal(goal):
                # Log progress
                if update.get('type') == 'step_progress':
                    self.logger.debug(f"Workflow {workflow.name}: {update.get('message', '')}")

                elif update.get('type') == 'error':
                    self.logger.error(f"Workflow {workflow.name} error: {update.get('error', '')}")

            # Mark as completed if one-time workflow
            if workflow.schedule_type == ScheduleType.ONCE:
                workflow.status = ScheduleStatus.COMPLETED
            else:
                workflow.status = ScheduleStatus.PENDING
                # Calculate next run time
                workflow.next_run = self._calculate_next_run(workflow)

        except Exception as e:
            self.logger.error(f"Error running workflow {workflow.name}: {e}")
            workflow.status = ScheduleStatus.FAILED

        # Save updated workflow
        await self.save_scheduled_workflows()

    async def list_scheduled_workflows(self) -> List[ScheduledWorkflow]:
        """List all scheduled workflows."""
        return list(self.scheduled_workflows.values())

    async def get_workflow(self, workflow_id: str) -> Optional[ScheduledWorkflow]:
        """Get a specific workflow by ID."""
        return self.scheduled_workflows.get(workflow_id)

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow."""
        if workflow_id in self.scheduled_workflows:
            self.scheduled_workflows[workflow_id].status = ScheduleStatus.PAUSED
            await self.save_scheduled_workflows()
            return True
        return False

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        if workflow_id in self.scheduled_workflows:
            workflow = self.scheduled_workflows[workflow_id]
            if workflow.status == ScheduleStatus.PAUSED:
                workflow.status = ScheduleStatus.PENDING
                workflow.next_run = self._calculate_next_run(workflow)
                await self.save_scheduled_workflows()
                return True
        return False

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow."""
        if workflow_id in self.scheduled_workflows:
            self.scheduled_workflows[workflow_id].status = ScheduleStatus.CANCELLED
            await self.save_scheduled_workflows()
            return True
        return False

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow completely."""
        if workflow_id in self.scheduled_workflows:
            del self.scheduled_workflows[workflow_id]
            await self.save_scheduled_workflows()
            return True
        return False

    def get_upcoming_runs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming workflow runs in the next N hours."""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        upcoming = []

        for workflow in self.scheduled_workflows.values():
            if (workflow.status == ScheduleStatus.PENDING and
                workflow.next_run and
                workflow.next_run <= cutoff):

                upcoming.append({
                    'workflow_id': workflow.id,
                    'name': workflow.name,
                    'next_run': workflow.next_run,
                    'description': workflow.description
                })

        return sorted(upcoming, key=lambda x: x['next_run'])

    async def shutdown(self):
        """Shutdown the scheduler."""
        self.logger.info("Shutting down workflow scheduler")
        self._shutdown = True

        # Wait for running tasks to complete
        for task_id, task in self.running_tasks.items():
            if not task.done():
                try:
                    await asyncio.wait_for(task, timeout=30)
                except asyncio.TimeoutError:
                    self.logger.warning(f"Task {task_id} did not complete gracefully")
                    task.cancel()

        await self.save_scheduled_workflows()