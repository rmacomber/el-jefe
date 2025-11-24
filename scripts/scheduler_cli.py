#!/usr/bin/env python3
"""
Scheduler CLI Tool

Command-line interface for managing scheduled workflows and repeatable tasks.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

from scheduler import WorkflowScheduler, ScheduleType, ScheduleStatus
from orchestrator import Orchestrator


class SchedulerCLI:
    """Command-line interface for workflow scheduler."""

    def __init__(self, workspace_path: Path = None):
        if workspace_path is None:
            workspace_path = Path("workspaces/scheduler")
        workspace_path.mkdir(parents=True, exist_ok=True)

        self.workspace_path = workspace_path
        self.scheduler = WorkflowScheduler(workspace_path)

    async def initialize(self):
        """Initialize the scheduler."""
        await self.scheduler.load_scheduled_workflows()

    def format_datetime(self, dt: datetime) -> str:
        """Format datetime for display."""
        if dt is None:
            return "Never"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def format_duration(self, dt: datetime) -> str:
        """Format datetime as duration from now."""
        if dt is None:
            return "Never"
        now = datetime.now()
        diff = dt - now
        if diff.total_seconds() < 0:
            return "Overdue"
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")

        return "In " + " ".join(parts) if parts else "Now"

    async def list_workflows(self, status_filter: str = None):
        """List all scheduled workflows."""
        workflows = await self.scheduler.list_scheduled_workflows()

        if status_filter:
            try:
                status_enum = ScheduleStatus(status_filter)
                workflows = [w for w in workflows if w.status == status_enum]
            except ValueError:
                print(f"❌ Invalid status: {status_filter}")
                return

        if not workflows:
            print("📋 No scheduled workflows found.")
            return

        print("\n📅 Scheduled Workflows")
        print("=" * 80)

        for workflow in sorted(workflows, key=lambda w: w.next_run or datetime.max):
            status_icon = {
                ScheduleStatus.PENDING: "⏳",
                ScheduleStatus.RUNNING: "🔄",
                ScheduleStatus.COMPLETED: "✅",
                ScheduleStatus.FAILED: "❌",
                ScheduleStatus.PAUSED: "⏸️",
                ScheduleStatus.CANCELLED: "🛑"
            }.get(workflow.status, "❓")

            print(f"\n{status_icon} {workflow.name}")
            print(f"   ID: {workflow.id}")
            print(f"   Description: {workflow.description}")
            print(f"   Status: {workflow.status.value}")
            print(f"   Schedule: {workflow.schedule_type.value}")
            print(f"   Last Run: {self.format_datetime(workflow.last_run)}")
            print(f"   Next Run: {self.format_datetime(workflow.next_run)} {self.format_duration(workflow.next_run)}")
            print(f"   Run Count: {workflow.run_count}")

            if workflow.max_runs:
                print(f"   Max Runs: {workflow.max_runs}")

            if workflow.agent_types:
                print(f"   Agents: {', '.join(workflow.agent_types)}")

    async def show_workflow(self, workflow_id: str):
        """Show detailed information about a workflow."""
        workflow = await self.scheduler.get_workflow(workflow_id)

        if not workflow:
            print(f"❌ Workflow not found: {workflow_id}")
            return

        print(f"\n📋 Workflow Details: {workflow.name}")
        print("=" * 60)
        print(f"ID: {workflow.id}")
        print(f"Description: {workflow.description}")
        print(f"Goal: {workflow.goal}")
        print(f"Status: {workflow.status.value}")
        print(f"Schedule Type: {workflow.schedule_type.value}")
        print(f"Schedule Config: {json.dumps(workflow.schedule_config, indent=2)}")
        print(f"Created: {self.format_datetime(workflow.created_at)}")
        print(f"Last Run: {self.format_datetime(workflow.last_run)}")
        print(f"Next Run: {self.format_datetime(workflow.next_run)}")
        print(f"Run Count: {workflow.run_count}")

        if workflow.max_runs:
            print(f"Max Runs: {workflow.max_runs}")

        if workflow.workspace_template:
            print(f"Workspace Template: {workflow.workspace_template}")

        if workflow.agent_types:
            print(f"Agent Types: {', '.join(workflow.agent_types)}")

        if workflow.notifications:
            print(f"Notifications: {workflow.notifications}")

        if workflow.metadata:
            print(f"Metadata: {json.dumps(workflow.metadata, indent=2)}")

    async def schedule_workflow(self, args):
        """Schedule a new workflow."""
        try:
            schedule_type = ScheduleType(args.schedule_type)
        except ValueError:
            print(f"❌ Invalid schedule type: {args.schedule_type}")
            return

        # Build schedule config based on type
        config = {}

        if schedule_type == ScheduleType.ONCE:
            if not args.run_at:
                print("❌ --run-at is required for one-time schedules")
                return
            config['run_at'] = args.run_at

        elif schedule_type == ScheduleType.DAILY:
            config['hour'] = args.hour or 9
            config['minute'] = args.minute or 0

        elif schedule_type == ScheduleType.WEEKLY:
            config['day_of_week'] = args.day_of_week or 0
            config['hour'] = args.hour or 9
            config['minute'] = args.minute or 0

        elif schedule_type == ScheduleType.INTERVAL:
            config['interval_value'] = args.interval_value or 1
            config['interval_unit'] = args.interval_unit or 'hours'

        # Parse agent types
        agent_types = args.agent_types.split(',') if args.agent_types else []

        workflow_id = await self.scheduler.schedule_workflow(
            name=args.name,
            description=args.description,
            goal=args.goal,
            schedule_type=schedule_type,
            schedule_config=config,
            max_runs=args.max_runs,
            workspace_template=args.workspace_template,
            agent_types=agent_types,
            metadata={'created_by': 'scheduler_cli'}
        )

        print(f"✅ Scheduled workflow '{args.name}' with ID: {workflow_id}")

        # Show next run time
        workflow = await self.scheduler.get_workflow(workflow_id)
        if workflow.next_run:
            print(f"📅 Next run: {self.format_datetime(workflow.next_run)} {self.format_duration(workflow.next_run)}")

    async def pause_workflow(self, workflow_id: str):
        """Pause a workflow."""
        success = await self.scheduler.pause_workflow(workflow_id)
        if success:
            print(f"⏸️ Paused workflow: {workflow_id}")
        else:
            print(f"❌ Failed to pause workflow: {workflow_id}")

    async def resume_workflow(self, workflow_id: str):
        """Resume a workflow."""
        success = await self.scheduler.resume_workflow(workflow_id)
        if success:
            print(f"▶️ Resumed workflow: {workflow_id}")
        else:
            print(f"❌ Failed to resume workflow: {workflow_id}")

    async def cancel_workflow(self, workflow_id: str):
        """Cancel a workflow."""
        success = await self.scheduler.cancel_workflow(workflow_id)
        if success:
            print(f"🛑 Cancelled workflow: {workflow_id}")
        else:
            print(f"❌ Failed to cancel workflow: {workflow_id}")

    async def delete_workflow(self, workflow_id: str):
        """Delete a workflow."""
        success = await self.scheduler.delete_workflow(workflow_id)
        if success:
            print(f"🗑️ Deleted workflow: {workflow_id}")
        else:
            print(f"❌ Failed to delete workflow: {workflow_id}")

    async def show_upcoming(self, hours: int = 24):
        """Show upcoming workflow runs."""
        upcoming = self.scheduler.get_upcoming_runs(hours)

        if not upcoming:
            print(f"📅 No workflows scheduled in the next {hours} hours.")
            return

        print(f"\n📅 Upcoming Workflow Runs (Next {hours} hours)")
        print("=" * 80)

        for run in upcoming:
            print(f"\n🔄 {run['name']}")
            print(f"   ID: {run['workflow_id']}")
            print(f"   When: {self.format_datetime(run['next_run'])} {self.format_duration(run['next_run'])}")
            print(f"   Description: {run['description']}")

    async def start_daemon(self):
        """Start the scheduler daemon."""
        print("🚀 Starting El Jefe Workflow Scheduler Daemon...")
        print("Press Ctrl+C to stop")

        def orchestrator_factory():
            return Orchestrator(self.workspace_path)

        try:
            await self.scheduler.start_scheduler(orchestrator_factory)
        except KeyboardInterrupt:
            print("\n⏹️ Stopping scheduler daemon...")
        finally:
            await self.scheduler.shutdown()


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="El Jefe Workflow Scheduler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schedule a daily report at 9 AM
  %(prog)s schedule "Daily Report" "Generate daily analytics report" daily --hour 9

  # Schedule a weekly backup every Sunday at 2 AM
  %(prog)s schedule "Weekly Backup" "Backup project files" weekly --day-of-week 6 --hour 2

  # Schedule an hourly task
  %(prog)s schedule "Hourly Check" "Check system status" interval --interval-unit hours

  # List all workflows
  %(prog)s list

  # Show upcoming runs
  %(prog)s upcoming

  # Start scheduler daemon
  %(prog)s start-daemon
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List scheduled workflows')
    list_parser.add_argument('--status', help='Filter by status (pending, running, completed, failed, paused, cancelled)')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show workflow details')
    show_parser.add_argument('workflow_id', help='Workflow ID')

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a new workflow')
    schedule_parser.add_argument('name', help='Workflow name')
    schedule_parser.add_argument('description', help='Workflow description')
    schedule_parser.add_argument('goal', help='Goal/task for the orchestrator')
    schedule_parser.add_argument('schedule_type', help='Schedule type: once, daily, weekly, interval')

    # Schedule options
    schedule_parser.add_argument('--run-at', help='Run at specific time (ISO format, for once schedules)')
    schedule_parser.add_argument('--hour', type=int, help='Hour to run (0-23, for daily/weekly)')
    schedule_parser.add_argument('--minute', type=int, help='Minute to run (0-59, for daily/weekly)')
    schedule_parser.add_argument('--day-of-week', type=int, help='Day of week (0=Monday, for weekly)')
    schedule_parser.add_argument('--interval-value', type=int, help='Interval value (for interval schedules)')
    schedule_parser.add_argument('--interval-unit', choices=['minutes', 'hours', 'days'], help='Interval unit')

    # Additional options
    schedule_parser.add_argument('--max-runs', type=int, help='Maximum number of runs')
    schedule_parser.add_argument('--workspace-template', help='Workspace name template')
    schedule_parser.add_argument('--agent-types', help='Comma-separated list of agent types')

    # Control commands
    pause_parser = subparsers.add_parser('pause', help='Pause a workflow')
    pause_parser.add_argument('workflow_id', help='Workflow ID')

    resume_parser = subparsers.add_parser('resume', help='Resume a workflow')
    resume_parser.add_argument('workflow_id', help='Workflow ID')

    cancel_parser = subparsers.add_parser('cancel', help='Cancel a workflow')
    cancel_parser.add_argument('workflow_id', help='Workflow ID')

    delete_parser = subparsers.add_parser('delete', help='Delete a workflow')
    delete_parser.add_argument('workflow_id', help='Workflow ID')

    # Upcoming command
    upcoming_parser = subparsers.add_parser('upcoming', help='Show upcoming runs')
    upcoming_parser.add_argument('--hours', type=int, default=24, help='Hours ahead to show')

    # Start daemon command
    daemon_parser = subparsers.add_parser('start-daemon', help='Start scheduler daemon')

    return parser


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = SchedulerCLI()
    await cli.initialize()

    try:
        if args.command == 'list':
            await cli.list_workflows(args.status)
        elif args.command == 'show':
            await cli.show_workflow(args.workflow_id)
        elif args.command == 'schedule':
            await cli.schedule_workflow(args)
        elif args.command == 'pause':
            await cli.pause_workflow(args.workflow_id)
        elif args.command == 'resume':
            await cli.resume_workflow(args.workflow_id)
        elif args.command == 'cancel':
            await cli.cancel_workflow(args.workflow_id)
        elif args.command == 'delete':
            await cli.delete_workflow(args.workflow_id)
        elif args.command == 'upcoming':
            await cli.show_upcoming(args.hours)
        elif args.command == 'start-daemon':
            await cli.start_daemon()
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())