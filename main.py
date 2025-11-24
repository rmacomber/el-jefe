#!/usr/bin/env python3
"""
AI Orchestrator - Main Entry Point

A comprehensive tool for orchestrating complex tasks using specialized AI agents.
Coordinates research, coding, writing, analysis, and design workflows.

Usage:
    python main.py "Your goal or task description"
    python main.py --list
    python main.py --resume <workspace-path>
    python main.py --help
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import Orchestrator
from src.user_interface import UserInterface

# Import chat interface (will be created)
try:
    from src.chat_interface import ChatInterface
except ImportError:
    ChatInterface = None


async def main():
    """Main entry point for the orchestrator CLI."""
    parser = argparse.ArgumentParser(
        description="AI Orchestrator - Coordinate specialized agents for complex tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Research AI trends for my podcast"
  %(prog)s "Build a Python script to analyze sales data"
  %(prog)s "Write documentation for my API"
  %(prog)s --list
  %(prog)s --resume workspaces/week-47/2024-11-23/my-task-143022
        """
    )

    parser.add_argument(
        "goal",
        nargs="?",
        help="The goal or task to accomplish"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List recent workspaces"
    )

    parser.add_argument(
        "--resume", "-r",
        metavar="WORKSPACE",
        help="Resume work in an existing workspace"
    )

    parser.add_argument(
        "--cleanup",
        type=int,
        metavar="DAYS",
        help="Clean up workspaces older than N days"
    )

    parser.add_argument(
        "--non-interactive", "-n",
        action="store_true",
        help="Run without prompting for user input"
    )

    parser.add_argument(
        "--workspace-dir", "-w",
        default="workspaces",
        help="Base directory for workspaces (default: workspaces)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )

    # Special case: no arguments - launch interactive chat mode
    if len(sys.argv) == 1:
        if ChatInterface is not None:
            chat_ui = ChatInterface()
            await chat_ui.start()
            return 0
        else:
            print("❌ Chat interface not available. Please install required dependencies.")
            return 1

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = Orchestrator(
        base_dir=args.workspace_dir,
        interactive=not args.non_interactive
    )

    ui = UserInterface(verbose=args.verbose)

    try:
        # Handle different commands
        if args.list:
            await show_workspaces(orchestrator, ui)
        elif args.resume:
            await resume_workspace(orchestrator, ui, args.resume)
        elif args.cleanup:
            await cleanup_workspaces(orchestrator, ui, args.cleanup)
        elif args.goal:
            await execute_goal(orchestrator, ui, args.goal)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        await ui.show_info("Operation cancelled by user")
        return 1
    except Exception as e:
        await ui.show_error(e, "An unexpected error occurred")
        return 1

    return 0


async def execute_goal(orchestrator: Orchestrator, ui: UserInterface, goal: str):
    """Execute a goal using the orchestrator."""
    await ui.show_info(f"Starting execution of goal: {goal}")

    # Execute the goal
    result = await orchestrator.execute_goal(goal)

    # Show summary
    await ui.show_summary(result.get("summary", {}))

    # Show workspace location
    await ui.show_success(f"All work saved to: {result['workspace']}")


async def show_workspaces(orchestrator: Orchestrator, ui: UserInterface):
    """List recent workspaces."""
    await ui.show_info("Fetching recent workspaces...")

    workspaces = await orchestrator.list_workspaces(limit=20)

    if not workspaces:
        await ui.show_info("No workspaces found")
        return

    print("\nRecent Workspaces:")
    print("-" * 80)

    for i, workspace in enumerate(workspaces, 1):
        name = workspace.get("name", "Unknown")
        path = workspace.get("path", "Unknown")
        status = workspace.get("status", "Unknown")
        created = workspace.get("created_at", "Unknown")[:19]

        print(f"{i:2d}. {name[:40]:<40}")
        print(f"     Status: {status:<10} | Created: {created}")
        print(f"     Path: {path}")
        print()


async def resume_workspace(orchestrator: Orchestrator, ui: UserInterface, workspace_path: str):
    """Resume work in an existing workspace."""
    await ui.show_info(f"Resuming workspace: {workspace_path}")

    success = await orchestrator.resume_workspace(workspace_path)

    if success:
        await ui.show_success(f"Resumed workspace: {workspace_path}")
        await ui.show_info("You can now continue working in this workspace")
    else:
        await ui.show_error(Exception("Failed to resume workspace"), "Check if the path exists")


async def cleanup_workspaces(orchestrator: Orchestrator, ui: UserInterface, days: int):
    """Clean up old workspaces."""
    await ui.show_warning(f"This will delete all workspaces older than {days} days")

    if not args.non_interactive:
        confirmed = await ui.request_approval("Are you sure you want to continue?")
        if not confirmed:
            await ui.show_info("Cleanup cancelled")
            return

    await orchestrator.cleanup_old_workspaces(days)
    await ui.show_success(f"Cleaned up workspaces older than {days} days")


if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("workspaces", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)