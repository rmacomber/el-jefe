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
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import Orchestrator
from src.user_interface import UserInterface

# Import scheduler
try:
    from src.scheduler import WorkflowScheduler
except ImportError:
    WorkflowScheduler = None

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

    # Scheduler commands
    parser.add_argument(
        "--schedule-list",
        action="store_true",
        help="List scheduled workflows"
    )

    parser.add_argument(
        "--schedule-daemon",
        action="store_true",
        help="Start scheduler daemon for running scheduled workflows"
    )

    parser.add_argument(
        "--schedule-add",
        nargs=4,
        metavar=("NAME", "DESCRIPTION", "GOAL", "SCHEDULE_TYPE"),
        help="Add a scheduled workflow: --schedule-add 'name' 'description' 'goal' 'daily'"
    )

    # Dashboard commands
    parser.add_argument(
        "--dashboard", "-d",
        action="store_true",
        help="Start the monitoring dashboard"
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
            await cleanup_workspaces(orchestrator, ui, args.cleanup, args.non_interactive)
        elif args.schedule_list:
            await show_scheduled_workflows(args.workspace_dir)
        elif args.schedule_daemon:
            await start_scheduler_daemon(args.workspace_dir)
        elif args.schedule_add:
            await add_scheduled_workflow(args.workspace_dir, *args.schedule_add)
        elif args.dashboard:
            await start_dashboard()
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


async def cleanup_workspaces(orchestrator: Orchestrator, ui: UserInterface, days: int, non_interactive: bool = False):
    """Clean up old workspaces."""
    await ui.show_warning(f"This will delete all workspaces older than {days} days")

    if not non_interactive:
        confirmed = await ui.request_approval("Are you sure you want to continue?")
        if not confirmed:
            await ui.show_info("Cleanup cancelled")
            return

    await orchestrator.cleanup_old_workspaces(days)
    await ui.show_success(f"Cleaned up workspaces older than {days} days")


async def show_scheduled_workflows(workspace_dir: str):
    """Show scheduled workflows."""
    if WorkflowScheduler is None:
        print("❌ Scheduler not available. Please install required dependencies.")
        return 1

    from pathlib import Path
    workspace_path = Path(workspace_dir) / "scheduler"
    workspace_path.mkdir(parents=True, exist_ok=True)

    scheduler = WorkflowScheduler(workspace_path)
    await scheduler.load_scheduled_workflows()

    workflows = await scheduler.list_scheduled_workflows()

    if not workflows:
        print("📋 No scheduled workflows found.")
        return 0

    print("\n📅 Scheduled Workflows")
    print("=" * 80)

    for workflow in sorted(workflows, key=lambda w: w.next_run or datetime.max):
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
            "cancelled": "🛑"
        }.get(workflow.status.value, "❓")

        print(f"\n{status_icon} {workflow.name}")
        print(f"   ID: {workflow.id}")
        print(f"   Description: {workflow.description}")
        print(f"   Status: {workflow.status.value}")
        print(f"   Schedule: {workflow.schedule_type.value}")
        print(f"   Last Run: {workflow.last_run.strftime('%Y-%m-%d %H:%M:%S') if workflow.last_run else 'Never'}")
        print(f"   Next Run: {workflow.next_run.strftime('%Y-%m-%d %H:%M:%S') if workflow.next_run else 'Never'}")
        print(f"   Run Count: {workflow.run_count}")

    return 0


async def start_scheduler_daemon(workspace_dir: str):
    """Start scheduler daemon."""
    if WorkflowScheduler is None:
        print("❌ Scheduler not available. Please install required dependencies.")
        return 1

    from pathlib import Path
    workspace_path = Path(workspace_dir) / "scheduler"
    workspace_path.mkdir(parents=True, exist_ok=True)

    scheduler = WorkflowScheduler(workspace_path)
    await scheduler.load_scheduled_workflows()

    print("🚀 Starting El Jefe Workflow Scheduler Daemon...")
    print("Press Ctrl+C to stop")

    def orchestrator_factory():
        return Orchestrator(workspace_dir)

    try:
        await scheduler.start_scheduler(orchestrator_factory)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping scheduler daemon...")
    finally:
        await scheduler.shutdown()

    return 0


async def add_scheduled_workflow(workspace_dir: str, name: str, description: str, goal: str, schedule_type: str):
    """Add a new scheduled workflow."""
    if WorkflowScheduler is None:
        print("❌ Scheduler not available. Please install required dependencies.")
        return 1

    from src.scheduler import ScheduleType
    from pathlib import Path

    try:
        schedule_enum = ScheduleType(schedule_type)
    except ValueError:
        print(f"❌ Invalid schedule type: {schedule_type}")
        print(f"Valid types: {[t.value for t in ScheduleType]}")
        return 1

    workspace_path = Path(workspace_dir) / "scheduler"
    workspace_path.mkdir(parents=True, exist_ok=True)

    scheduler = WorkflowScheduler(workspace_path)
    await scheduler.load_scheduled_workflows()

    # Basic schedule configuration
    if schedule_enum == ScheduleType.DAILY:
        schedule_config = {"hour": 9, "minute": 0}
    elif schedule_enum == ScheduleType.WEEKLY:
        schedule_config = {"day_of_week": 0, "hour": 9, "minute": 0}
    elif schedule_enum == ScheduleType.INTERVAL:
        schedule_config = {"interval_value": 1, "interval_unit": "hours"}
    else:
        schedule_config = {}

    try:
        workflow_id = await scheduler.schedule_workflow(
            name=name,
            description=description,
            goal=goal,
            schedule_type=schedule_enum,
            schedule_config=schedule_config,
            metadata={'created_by': 'main_cli'}
        )

        print(f"✅ Scheduled workflow '{name}' with ID: {workflow_id}")

        # Show next run time
        workflow = await scheduler.get_workflow(workflow_id)
        if workflow.next_run:
            print(f"📅 Next run: {workflow.next_run.strftime('%Y-%m-%d %H:%M:%S')}")

        return 0

    except Exception as e:
        print(f"❌ Error scheduling workflow: {e}")
        return 1


async def start_dashboard():
    """Start the monitoring dashboard."""
    try:
        # Import here to avoid circular imports
        from monitoring_dashboard import MonitoringDashboard

        print("🚀 Starting El Jefe Monitoring Dashboard...")
        print("=" * 50)

        dashboard = MonitoringDashboard()
        runner = await dashboard.start()

        print("📊 Dashboard started successfully!")
        print("🌐 Web Interface: http://localhost:8080")
        print("📡 WebSocket API: ws://localhost:8080/ws")
        print("🔌 REST API: http://localhost:8080/api/")
        print("\n💡 Keep this terminal open to maintain the dashboard")
        print("💻 Open http://localhost:8080 in your browser to view")
        print("⏹️ Press Ctrl+C to stop the dashboard")

        try:
            # Keep the dashboard running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping monitoring dashboard...")
            await dashboard.stop()
            await runner.cleanup()
            print("✅ Dashboard stopped successfully")

        return 0

    except ImportError:
        print("❌ Dashboard dependencies not found")
        print("💡 Install with: pip install websockets aiohttp-cors")
        return 1
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return 1


if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("workspaces", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)