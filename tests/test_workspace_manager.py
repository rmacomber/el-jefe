"""
Tests for Workspace Manager

Test the workspace creation, management, and file operations.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
import json

from src.workspace_manager import WorkspaceManager


class TestWorkspaceManager(unittest.TestCase):
    """Test cases for WorkspaceManager class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.workspace_manager = WorkspaceManager(self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    async def test_create_workspace(self):
        """Test workspace creation."""
        task_name = "test-task"
        task_description = "A test task for unit testing"

        # Create workspace
        workspace_info = await self.workspace_manager.create_workspace(
            task_name, task_description
        )

        # Verify workspace info
        self.assertEqual(workspace_info["name"], task_name)
        self.assertEqual(workspace_info["description"], task_description)
        self.assertEqual(workspace_info["status"], "initialized")
        self.assertIn("test-task", workspace_info["path"])

        # Verify directory structure
        workspace_path = Path(workspace_info["path"])
        self.assertTrue(workspace_path.exists())
        self.assertTrue((workspace_path / "context-main.md").exists())
        self.assertTrue((workspace_path / "workflow-history.json").exists())
        self.assertTrue((workspace_path / "agent_outputs").exists())
        self.assertTrue((workspace_path / "resources").exists())

    async def test_log_workflow_step(self):
        """Test logging workflow steps."""
        # Create workspace first
        workspace_info = await self.workspace_manager.create_workspace(
            "log-test", "Test logging"
        )
        workspace_path = Path(workspace_info["path"])

        # Log a step
        step = {
            "step_type": "test",
            "description": "Test step",
            "status": "completed"
        }
        await self.workspace_manager.log_workflow_step(workspace_path, step)

        # Verify step was logged
        history_path = workspace_path / "workflow-history.json"
        with open(history_path, 'r') as f:
            history = json.load(f)

        self.assertEqual(len(history["steps"]), 1)
        self.assertEqual(history["steps"][0]["step_type"], "test")
        self.assertEqual(history["steps"][0]["status"], "completed")
        self.assertIn("timestamp", history["steps"][0])

    async def test_update_context(self):
        """Test updating workspace context."""
        # Create workspace
        workspace_info = await self.workspace_manager.create_workspace(
            "context-test", "Test context updates"
        )
        workspace_path = Path(workspace_info["path"])

        # Update context
        await self.workspace_manager.update_context(
            workspace_path,
            "Test Section",
            "This is test content for the context."
        )

        # Verify context was updated
        context_path = workspace_path / "context-main.md"
        with open(context_path, 'r') as f:
            context = f.read()

        self.assertIn("## Test Section", context)
        self.assertIn("This is test content", context)

    async def test_workspace_summary(self):
        """Test generating workspace summary."""
        # Create and populate workspace
        workspace_info = await self.workspace_manager.create_workspace(
            "summary-test", "Test summary generation"
        )
        workspace_path = Path(workspace_info["path"])

        # Add some data
        step = {
            "step_type": "test",
            "description": "Test step for summary",
            "status": "completed"
        }
        await self.workspace_manager.log_workflow_step(workspace_path, step)

        # Get summary
        summary = await self.workspace_manager.get_workspace_summary(workspace_path)

        # Verify summary
        self.assertEqual(summary["workspace"], str(workspace_path))
        self.assertEqual(summary["total_steps"], 1)
        self.assertIn("context_preview", summary)

    async def test_list_workspaces(self):
        """Test listing workspaces."""
        # Create multiple workspaces
        for i in range(3):
            await self.workspace_manager.create_workspace(
                f"test-workspace-{i}",
                f"Test workspace number {i}"
            )

        # List workspaces
        workspaces = await self.workspace_manager.list_workspaces(limit=10)

        # Should have at least 3 workspaces
        self.assertGreaterEqual(len(workspaces), 3)

        # Verify structure
        for workspace in workspaces:
            self.assertIn("name", workspace)
            self.assertIn("path", workspace)

    def test_get_workspace_path(self):
        """Test workspace path generation."""
        # Test normal task name
        path = self.workspace_manager.get_workspace_path("test-task")
        self.assertIn("test-task", str(path))
        self.assertIn("week-", str(path))

        # Test task name with special characters
        path = self.workspace_manager.get_workspace_path("Task@#$%^&*()")
        # Should be sanitized
        self.assertNotIn("@", str(path))
        self.assertNotIn("#", str(path))


if __name__ == "__main__":
    # Run async tests
    def run_async_test(test_func):
        """Run an async test function."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_func())
        finally:
            loop.close()

    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(TestWorkspaceManager("test_create_workspace"))
    suite.addTest(TestWorkspaceManager("test_log_workflow_step"))
    suite.addTest(TestWorkspaceManager("test_update_context"))
    suite.addTest(TestWorkspaceManager("test_workspace_summary"))
    suite.addTest(TestWorkspaceManager("test_list_workspaces"))
    suite.addTest(TestWorkspaceManager("test_get_workspace_path"))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)