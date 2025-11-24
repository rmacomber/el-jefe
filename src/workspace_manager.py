"""
Workspace Manager Module

Handles creation and management of organized workspaces for different tasks.
Implements date-based folder structure with proper isolation and context tracking.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
import aiofiles


class WorkspaceManager:
    """Manages workspace creation, organization, and context tracking."""

    def __init__(self, base_dir: str = "workspaces"):
        """
        Initialize the workspace manager.

        Args:
            base_dir: Base directory for all workspaces
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def get_workspace_path(self, task_name: str) -> Path:
        """
        Generate a workspace path based on current date and time.

        Args:
            task_name: Name of the task (will be sanitized)

        Returns:
            Path object for the workspace
        """
        # Get current week and day
        now = datetime.now()
        week_number = now.isocalendar()[1]
        day_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        # Sanitize task name
        safe_task_name = "".join(c for c in task_name if c.isalnum() or c in ('-', '_')).strip()
        safe_task_name = safe_task_name[:30]  # Limit length

        # Create workspace path
        workspace_path = self.base_dir / f"week-{week_number:02d}" / day_str / f"{safe_task_name}-{time_str}"

        return workspace_path

    async def create_workspace(self, task_name: str, task_description: str) -> Dict[str, Any]:
        """
        Create a new workspace with the required structure and files.

        Args:
            task_name: Name of the task
            task_description: Detailed description of the task

        Returns:
            Dictionary containing workspace information
        """
        workspace_path = self.get_workspace_path(task_name)

        # Create directory structure
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "agent_outputs").mkdir(exist_ok=True)
        (workspace_path / "resources").mkdir(exist_ok=True)

        # Initialize workspace files
        await self._initialize_context_file(workspace_path, task_name, task_description)
        await self._initialize_workflow_history(workspace_path)

        workspace_info = {
            "path": str(workspace_path),
            "name": task_name,
            "description": task_description,
            "created_at": datetime.now().isoformat(),
            "status": "initialized"
        }

        # Save workspace metadata
        await self._save_workspace_metadata(workspace_path, workspace_info)

        return workspace_info

    async def _initialize_context_file(self, workspace_path: Path, task_name: str, task_description: str):
        """Initialize the main context file with task information."""
        context_content = f"""# {task_name}

## Task Description
{task_description}

## Context
This workspace contains all work, agent outputs, and progress for the above task.

## Agents and Roles
<!-- Agent information will be added as they are spawned -->

## Progress Summary
<!-- Progress will be updated as workflow advances -->

## Key Findings
<!-- Important findings and results will be summarized here -->

## Resources
<!-- Links to resources and reference materials -->

## Notes
<!-- Additional notes and observations -->
"""
        context_path = workspace_path / "context-main.md"
        async with aiofiles.open(context_path, 'w') as f:
            await f.write(context_content)

    async def _initialize_workflow_history(self, workspace_path: Path):
        """Initialize the workflow history JSON file."""
        workflow_history = {
            "workspace_created": datetime.now().isoformat(),
            "task_name": workspace_path.name,
            "steps": [],
            "agents_spawned": [],
            "total_cost": 0.0,
            "status": "initialized"
        }

        history_path = workspace_path / "workflow-history.json"
        async with aiofiles.open(history_path, 'w') as f:
            await f.write(json.dumps(workflow_history, indent=2))

    async def _save_workspace_metadata(self, workspace_path: Path, metadata: Dict[str, Any]):
        """Save workspace metadata to a JSON file."""
        metadata_path = workspace_path / "workspace-info.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))

    async def log_workflow_step(self, workspace_path: Path, step: Dict[str, Any]):
        """
        Log a workflow step to the history file.

        Args:
            workspace_path: Path to the workspace
            step: Step information to log
        """
        history_path = workspace_path / "workflow-history.json"

        # Read existing history
        async with aiofiles.open(history_path, 'r') as f:
            history = json.loads(await f.read())

        # Add new step
        step["timestamp"] = datetime.now().isoformat()
        history["steps"].append(step)
        history["last_updated"] = datetime.now().isoformat()

        # Write back
        async with aiofiles.open(history_path, 'w') as f:
            await f.write(json.dumps(history, indent=2))

    async def update_context(self, workspace_path: Path, section: str, content: str):
        """
        Update a specific section in the context file.

        Args:
            workspace_path: Path to the workspace
            section: Section to update
            content: New content for the section
        """
        context_path = workspace_path / "context-main.md"

        # Read existing context
        async with aiofiles.open(context_path, 'r') as f:
            context = await f.read()

        # Simple section replacement (can be made more sophisticated)
        lines = context.split('\n')
        new_lines = []
        in_section = False
        section_found = False

        for line in lines:
            if line.strip() == f"## {section}":
                in_section = True
                section_found = True
                new_lines.append(line)
                new_lines.append(content)
            elif in_section and line.startswith("## "):
                in_section = False
                new_lines.append(line)
            elif not in_section:
                new_lines.append(line)

        # If section wasn't found, add it at the end
        if not section_found:
            new_lines.append(f"\n## {section}\n{content}")

        # Write back
        async with aiofiles.open(context_path, 'w') as f:
            await f.write('\n'.join(new_lines))

    async def get_workspace_summary(self, workspace_path: Path) -> Dict[str, Any]:
        """
        Get a summary of the workspace including all work done.

        Args:
            workspace_path: Path to the workspace

        Returns:
            Summary dictionary
        """
        # Read workflow history
        history_path = workspace_path / "workflow-history.json"
        async with aiofiles.open(history_path, 'r') as f:
            history = json.loads(await f.read())

        # Read context
        context_path = workspace_path / "context-main.md"
        async with aiofiles.open(context_path, 'r') as f:
            context = await f.read()

        # List output files
        output_files = []
        agent_outputs_dir = workspace_path / "agent_outputs"
        if agent_outputs_dir.exists():
            for file_path in agent_outputs_dir.glob("*"):
                if file_path.is_file():
                    output_files.append(str(file_path.relative_to(workspace_path)))

        summary = {
            "workspace": str(workspace_path),
            "created_at": history.get("workspace_created"),
            "last_updated": history.get("last_updated"),
            "total_steps": len(history.get("steps", [])),
            "agents_spawned": history.get("agents_spawned", []),
            "output_files": output_files,
            "status": history.get("status"),
            "context_preview": context[:500] + "..." if len(context) > 500 else context
        }

        return summary

    async def list_workspaces(self, limit: int = 10) -> list:
        """
        List recent workspaces.

        Args:
            limit: Maximum number of workspaces to return

        Returns:
            List of workspace information
        """
        workspaces = []

        for week_dir in sorted(self.base_dir.glob("week-*"), reverse=True):
            for day_dir in sorted(week_dir.glob("*"), reverse=True):
                for workspace_dir in sorted(day_dir.glob("*"), reverse=True):
                    if len(workspaces) >= limit:
                        break

                    # Read workspace info if it exists
                    info_path = workspace_dir / "workspace-info.json"
                    if info_path.exists():
                        async with aiofiles.open(info_path, 'r') as f:
                            info = json.loads(await f.read())
                            workspaces.append(info)
                    else:
                        # Fallback: basic info from directory name
                        workspaces.append({
                            "path": str(workspace_dir),
                            "name": workspace_dir.name,
                            "status": "unknown"
                        })

                if len(workspaces) >= limit:
                    break

            if len(workspaces) >= limit:
                break

        return workspaces