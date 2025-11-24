#!/usr/bin/env python3
"""
Test script for the AI Orchestrator SDK

Run this script to verify that the orchestrator is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_workspace_manager():
    """Test the workspace manager."""
    print("🧪 Testing Workspace Manager...")

    from src.workspace_manager import WorkspaceManager

    # Create a test workspace manager
    wm = WorkspaceManager("test-workspaces")

    # Create a test workspace
    workspace_info = await wm.create_workspace(
        "test-task",
        "This is a test task to verify the workspace manager is working"
    )

    print(f"✅ Created workspace: {workspace_info['path']}")

    # Test logging
    await wm.log_workflow_step(
        Path(workspace_info["path"]),
        {
            "step_type": "test",
            "description": "Test step",
            "status": "completed"
        }
    )

    print("✅ Successfully logged workflow step")

    # Test context update
    await wm.update_context(
        Path(workspace_info["path"]),
        "Test Section",
        "This is test content added to verify context updates work."
    )

    print("✅ Successfully updated context")

    return True

async def test_task_planner():
    """Test the task planner."""
    print("\n🧪 Testing Task Planner...")

    from src.task_planner import TaskPlanner

    # Create a test task planner
    planner = TaskPlanner()

    # Test different task types
    test_goals = [
        "Research AI trends for my podcast",
        "Build a Python script to analyze data",
        "Write documentation for my API"
    ]

    for goal in test_goals:
        plan = await planner.create_task_plan(goal)
        print(f"✅ Created plan for: {goal}")
        print(f"   Steps: {plan['estimated_steps']}")

    return True

async def test_agent_manager():
    """Test the agent manager."""
    print("\n🧪 Testing Agent Manager...")

    from src.agent_manager import AgentManager, AgentType
    from src.workspace_manager import WorkspaceManager

    # Create workspace and agent manager
    wm = WorkspaceManager("test-workspaces")
    workspace_info = await wm.create_workspace("agent-test", "Test agent spawning")
    workspace_path = Path(workspace_info["path"])

    am = AgentManager(workspace_path)

    # Test agent spawning (mock)
    print(f"✅ Agent manager initialized for workspace: {workspace_path}")

    # List agent types
    from src.agent_manager import AgentConfig
    print(f"✅ Available agent types: {list(AgentConfig.AGENT_CONFIGS.keys())}")

    return True

async def test_orchestrator():
    """Test the main orchestrator."""
    print("\n🧪 Testing Orchestrator...")

    from src.orchestrator import Orchestrator

    # Create orchestrator
    orchestrator = Orchestrator(
        base_dir="test-workspaces",
        interactive=False  # Non-interactive for testing
    )

    print("✅ Orchestrator initialized successfully")

    # Test workspace listing
    workspaces = await orchestrator.list_workspaces(limit=5)
    print(f"✅ Found {len(workspaces)} workspaces")

    return True

async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting AI Orchestrator SDK Tests\n")
    print("=" * 50)

    tests = [
        ("Workspace Manager", test_workspace_manager),
        ("Task Planner", test_task_planner),
        ("Agent Manager", test_agent_manager),
        ("Orchestrator", test_orchestrator)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, "✅ PASSED", None))
        except Exception as e:
            results.append((test_name, "❌ FAILED", str(e)))

    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, status, error in results:
        print(f"{status} {test_name}")
        if error:
            print(f"    Error: {error}")

        if "PASSED" in status:
            passed += 1
        else:
            failed += 1

    print(f"\nSummary: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All tests passed! The AI Orchestrator SDK is ready to use.")
        print("\nNext steps:")
        print("1. Set up your Claude API key: export CLAUDE_API_KEY='your-key-here'")
        print("2. Run the main CLI: python main.py --help")
        print("3. Try an example: python examples/podcast_research.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)