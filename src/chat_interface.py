"""
Chat Interface for El Jefe - Interactive Mode

Provides Claude Code-style chat interface for planning and managing
autonomous agent workflows while maintaining real-time oversight capabilities.
"""

import asyncio
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Import each module individually to handle partial failures
Orchestrator = None
StreamingOrchestrator = None
UserInterface = None
ProgressMonitor = None
CLIInput = None

try:
    from cli_input import CLIInput
except ImportError:
    CLIInput = None

try:
    from orchestrator import Orchestrator
except ImportError:
    Orchestrator = None

try:
    from streaming_orchestrator import StreamingOrchestrator
except ImportError:
    StreamingOrchestrator = None

try:
    from user_interface import UserInterface
except ImportError:
    UserInterface = None

try:
    from monitoring import ProgressMonitor
except ImportError:
    ProgressMonitor = None


@dataclass
class ChatSession:
    """Represents a chat session with context and state."""
    session_id: str
    started_at: datetime
    conversation_history: List[Dict[str, Any]]
    active_workflows: Dict[str, Dict[str, Any]]
    context: Dict[str, Any]


class ChatInterface:
    """Interactive chat interface for El Jefe."""

    def __init__(self):
        self.session = ChatSession(
            session_id=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            started_at=datetime.now(),
            conversation_history=[],
            active_workflows={},
            context={}
        )

        # Initialize enhanced CLI input system
        if CLIInput is not None:
            self.cli_input = CLIInput()
        else:
            self.cli_input = None

        # Initialize streaming orchestrator and monitoring if available
        if StreamingOrchestrator is not None:
            self.streaming_orchestrator = StreamingOrchestrator(
                base_dir="workspaces",
                enable_monitoring=True,
                enable_streaming=True
            )
            # Fallback to regular orchestrator for compatibility
            self.orchestrator = Orchestrator(
                base_dir="workspaces",
                interactive=True
            ) if Orchestrator is not None else None
        else:
            self.streaming_orchestrator = None
            self.orchestrator = Orchestrator(
                base_dir="workspaces",
                interactive=True
            ) if Orchestrator is not None else None

        # Initialize monitoring system
        if ProgressMonitor is not None:
            self.monitor = ProgressMonitor()
            self.monitor.start_monitoring()
        else:
            self.monitor = None

        if UserInterface is not None:
            self.ui = UserInterface(verbose=False)
        else:
            self.ui = None

        self.running = True
        self.streaming_mode = True  # Default to streaming mode

        # Available commands
        self.commands = {
            '/help': self.cmd_help,
            '/start': self.cmd_start,
            '/start-streaming': self.cmd_start_streaming,
            '/pause': self.cmd_pause,
            '/resume': self.cmd_resume,
            '/interrupt': self.cmd_interrupt,
            '/status': self.cmd_status,
            '/agents': self.cmd_agents,
            '/workspaces': self.cmd_workspaces,
            '/monitor': self.cmd_monitor,
            '/metrics': self.cmd_metrics,
            '/mode': self.cmd_mode,
            '/clear': self.cmd_clear,
            '/exit': self.cmd_exit,
            '/quit': self.cmd_exit
        }

    async def start(self) -> None:
        """Start the interactive chat interface."""
        await self.show_welcome()

        while self.running:
            try:
                # Get user input
                user_input = await self.get_user_input()

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    await self.handle_command(user_input)
                else:
                    # Regular chat message
                    await self.handle_chat_message(user_input)

            except KeyboardInterrupt:
                await self.show_message("\n👋 Goodbye!")
                break
            except Exception as e:
                await self.show_error(f"Error: {e}")

    async def show_welcome(self) -> None:
        """Display welcome message."""
        await self.show_message("""
╔══════════════════════════════════════════════════════════════╗
║                    🤖 El Jefe - Interactive Mode                ║
╚══════════════════════════════════════════════════════════════╝

Welcome to El Jefe! I'm your AI orchestrator that can coordinate
specialized agents to help you accomplish complex tasks.

💡 Try these commands to get started:
  /help     - Show all available commands
  /start    - Start an autonomous workflow
  /status   - Show current system status

Or just tell me what you'd like to accomplish, and I'll help you plan it!
""")

    async def get_user_input(self) -> str:
        """Get user input with enhanced CLI features."""
        try:
            if self.cli_input is not None:
                # Use enhanced CLI input with history and auto-completion
                return await self.cli_input.get_enhanced_input()
            else:
                # Fallback to basic input
                return input("\n💬 El Jefe> ")
        except EOFError:
            return "/exit"

    async def handle_command(self, command: str) -> None:
        """Handle chat commands."""
        parts = command.strip().split()
        cmd = parts[0].lower()

        if cmd in self.commands:
            args = parts[1:] if len(parts) > 1 else []
            await self.commands[cmd](args)
        else:
            await self.show_message(f"❌ Unknown command: {cmd}")
            await self.show_message("Type /help to see available commands.")

    async def handle_chat_message(self, message: str) -> None:
        """Handle regular chat messages."""
        # Add to conversation history
        self.session.conversation_history.append({
            'type': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

        # Simple response for now - can be enhanced with LLM integration
        await self.show_message(f"I understand you want to: {message}")
        await self.show_message("Let me help you plan this! Try using /start to begin an autonomous workflow.")

    # Command implementations
    async def cmd_help(self, args: List[str]) -> None:
        """Show help information."""
        await self.show_message("""
📚 Available Commands:

🚀 Workflow Commands:
  /start <goal>           - Start autonomous workflow with specified goal
  /start-streaming <goal> - Start workflow with real-time streaming output
  /interrupt <session_id> - Interrupt a running workflow
  /pause <id>             - Pause running workflow (use /status to see IDs)
  /resume <id>            - Resume paused workflow
  /status                 - Show status of all running workflows

🔍 Monitoring Commands:
  /agents                 - Show active agents and their current tasks
  /monitor                - Show real-time monitoring dashboard
  /metrics                - Display workflow performance metrics

⚙️  System Commands:
  /mode                   - Toggle between streaming and legacy mode
  /workspaces             - List recent workspaces
  /clear                  - Clear conversation history

💬 Chat Commands:
  /help                   - Show this help message
  /exit, /quit            - Exit chat mode

💡 Examples:
  /start "Research AI trends for my podcast"
  /start-streaming "Build a Python API for data analysis"
  /status
  /monitor
  /mode
        """)

    async def cmd_start(self, args: List[str]) -> None:
        """Start an autonomous workflow."""
        if not args:
            await self.show_message("❌ Please specify a goal: /start \"your goal here\"")
            return

        goal = ' '.join(args)
        await self.show_message(f"🚀 Starting autonomous workflow: {goal}")

        try:
            # Execute goal using existing orchestrator
            if self.orchestrator is not None:
                result = await self.orchestrator.execute_goal(goal)

                # Store in active workflows
                workflow_id = f"workflow_{datetime.now().strftime('%H%M%S')}"
                self.session.active_workflows[workflow_id] = {
                    'goal': goal,
                    'status': 'completed',
                    'result': result,
                    'started_at': datetime.now().isoformat()
                }

                await self.show_message("✅ Workflow completed successfully!")
            else:
                await self.show_message("⚠️ Orchestrator not available - running in demo mode")
                await self.show_message(f"Would start workflow: {goal}")

        except Exception as e:
            await self.show_error(f"❌ Workflow failed: {e}")

    async def cmd_pause(self, args: List[str]) -> None:
        """Pause a running workflow."""
        await self.show_message("⏸️ Pause functionality coming soon!")

    async def cmd_resume(self, args: List[str]) -> None:
        """Resume a paused workflow."""
        await self.show_message("▶️ Resume functionality coming soon!")

    async def cmd_status(self, args: List[str]) -> None:
        """Show status of active workflows."""
        if not self.session.active_workflows:
            await self.show_message("📊 No active workflows.")
            return

        await self.show_message("📊 Active Workflows:")
        for workflow_id, workflow in self.session.active_workflows.items():
            status_emoji = "✅" if workflow['status'] == 'completed' else "⏸️"
            await self.show_message(f"  {status_emoji} {workflow_id}: {workflow['goal']}")
            await self.show_message(f"     Status: {workflow['status']}")
            await self.show_message(f"     Started: {workflow['started_at']}")

    async def cmd_agents(self, args: List[str]) -> None:
        """Show information about available agents."""
        await self.show_message("""
🤖 Available Agent Types:

🔬 Researcher    - Web research, information gathering, fact-finding
💻 Coder        - Code generation, development, technical tasks
✍️ Writer       - Content creation, documentation, editing
📊 Analyst      - Data analysis, insights, trend identification
🏗️ Designer     - Architecture planning, system design
🔍 QA Tester    - Testing, validation, quality assurance

Use /start to launch workflows that coordinate these agents automatically!
        """)

    async def cmd_workspaces(self, args: List[str]) -> None:
        """List recent workspaces."""
        await self.show_message("📁 Listing recent workspaces...")
        try:
            if self.orchestrator is not None:
                workspaces = await self.orchestrator.list_workspaces(limit=10)
                if workspaces:
                    for workspace in workspaces:
                        await self.show_message(f"  📂 {workspace}")
                else:
                    await self.show_message("   No workspaces found.")
            else:
                await self.show_message("⚠️ Orchestrator not available - running in demo mode")
        except Exception as e:
            await self.show_error(f"❌ Failed to list workspaces: {e}")

    async def cmd_clear(self, args: List[str]) -> None:
        """Clear conversation history."""
        self.session.conversation_history.clear()
        await self.show_message("🧹 Conversation history cleared.")

    async def cmd_start_streaming(self, args: List[str]) -> None:
        """Start a streaming workflow with real-time output."""
        if not args:
            await self.show_message("❌ Please specify a goal: /start-streaming \"your goal here\"")
            return

        goal = ' '.join(args)
        await self.show_message(f"🚀 Starting streaming workflow: {goal}")

        try:
            if self.streaming_orchestrator is not None:
                # Execute streaming workflow
                session_id = f"streaming_{datetime.now().strftime('%H%M%S')}"

                async for update in self.streaming_orchestrator.execute_goal_streaming(
                    goal, session_id=session_id, enable_parallel=True
                ):
                    timestamp = update["timestamp"][-8:]  # Last 8 chars for time

                    if update["type"] == "workflow_started":
                        await self.show_message(f"\n[{timestamp}] 📂 Workflow Started")
                        await self.show_message(f"  Session: {update['session_id']}")
                        await self.show_message(f"  Workspace: {update['workspace']}")

                    elif update["type"] == "workflow_planned":
                        await self.show_message(f"\n[{timestamp}] 📋 Planned {update['total_steps']} steps")
                        for step in update["steps"]:
                            await self.show_message(f"  Step {step['step']}: {step['description']} ({step['agent_type']})")

                    elif update["type"] == "step_started":
                        await self.show_message(f"\n[{timestamp}] ⚡ Step {update['step']}/{update['total_steps']}")
                        await self.show_message(f"  Agent: {update['agent_type']}")
                        await self.show_message(f"  Task: {update['description']}")

                    elif update["type"] == "text_chunk":
                        # Show real-time text output (truncated for readability)
                        text = update["content"][:150]
                        if len(update["content"]) > 150:
                            text += "..."
                        await self.show_message(f"  📝 {text}")

                    elif update["type"] == "tool_use":
                        await self.show_message(f"  🔧 Using tool: {update['tool']}")

                    elif update["type"] == "agent_completed":
                        await self.show_message(f"\n[{timestamp}] ✅ Agent Completed")
                        await self.show_message(f"  Words: {update['total_words']}")
                        await self.show_message(f"  Tokens: {update['total_tokens']}")
                        await self.show_message(f"  Tools used: {', '.join(update['tools_used'])}")

                    elif update["type"] == "step_completed":
                        await self.show_message(f"✅ Step {update['step']} completed")

                    elif update["type"] == "workflow_completed":
                        await self.show_message(f"\n[{timestamp}] 🎉 Workflow Completed!")
                        await self.show_message(f"  Session: {update['session_id']}")
                        await self.show_message(f"  Workspace: {update['workspace']}")

                        # Display metrics
                        metrics = update.get("metrics", {})
                        if metrics:
                            await self.show_message(f"  📊 Metrics:")
                            await self.show_message(f"    Total Tokens: {metrics.get('total_tokens', 0)}")
                            await self.show_message(f"    Total Words: {metrics.get('total_words', 0)}")
                            await self.show_message(f"    Avg Response Time: {metrics.get('average_response_time', 0):.2f}s")

                        # Store in active workflows
                        self.session.active_workflows[session_id] = {
                            'goal': goal,
                            'status': 'completed',
                            'session_id': session_id,
                            'workspace': update['workspace'],
                            'metrics': metrics,
                            'started_at': update['timestamp']
                        }

                        break

                    elif update["type"] == "workflow_error":
                        await self.show_error(f"❌ Workflow Error: {update['error']}")
                        break

            else:
                await self.show_message("⚠️ Streaming orchestrator not available - falling back to regular execution")
                await self.cmd_start(args)

        except Exception as e:
            await self.show_error(f"❌ Streaming workflow failed: {e}")

    async def cmd_interrupt(self, args: List[str]) -> None:
        """Interrupt a running workflow."""
        if not args:
            await self.show_message("❌ Please specify session ID: /interrupt <session_id>")
            await self.show_message("Use /status to see active sessions")
            return

        session_id = args[0]

        try:
            if self.streaming_orchestrator is not None:
                success = await self.streaming_orchestrator.interrupt_workflow(session_id)
                if success:
                    await self.show_message(f"⏹️ Successfully interrupted workflow: {session_id}")
                else:
                    await self.show_message(f"❌ Failed to interrupt workflow: {session_id}")
                    await self.show_message("Session may not exist or may already be completed")
            else:
                await self.show_message("⚠️ Streaming orchestrator not available")

        except Exception as e:
            await self.show_error(f"❌ Failed to interrupt workflow: {e}")

    async def cmd_monitor(self, args: List[str]) -> None:
        """Show real-time monitoring dashboard."""
        await self.show_message("🔍 Real-Time Monitoring Dashboard")
        await self.show_message("=" * 50)

        if self.monitor is not None:
            try:
                # Get all agent status
                all_agents = self.monitor.get_all_agent_status()

                if all_agents:
                    await self.show_message(f"🤖 Active Agents: {len(all_agents)}")
                    for agent_id, agent_status in all_agents.items():
                        status_emoji = {
                            'running': '🟢',
                            'paused': '⏸️',
                            'completed': '✅',
                            'failed': '❌',
                            'interrupted': '⏹️'
                        }.get(agent_status.status, '❓')

                        await self.show_message(f"  {status_emoji} {agent_id}")
                        await self.show_message(f"    Type: {agent_status.agent_type}")
                        await self.show_message(f"    Task: {agent_status.task[:50]}...")
                        await self.show_message(f"    Progress: {agent_status.progress:.1%}")
                        await self.show_message(f"    Current: {agent_status.current_step}")
                        await self.show_message("")
                else:
                    await self.show_message("🤖 No active agents")

                # Show monitoring sessions
                if self.monitor.active_sessions:
                    await self.show_message(f"📊 Active Sessions: {len(self.monitor.active_sessions)}")
                    for session_id, session in self.monitor.active_sessions.items():
                        await self.show_message(f"  📂 {session_id}")
                        await self.show_message(f"    Status: {session.status}")
                        await self.show_message(f"    Active Agents: {len(session.active_agents)}")
                        await self.show_message(f"    Workspace: {session.workspace_path}")
                else:
                    await self.show_message("📊 No active monitoring sessions")

            except Exception as e:
                await self.show_error(f"❌ Error accessing monitoring data: {e}")
        else:
            await self.show_message("⚠️ Monitoring system not available")

    async def cmd_metrics(self, args: List[str]) -> None:
        """Display workflow performance metrics."""
        await self.show_message("📈 Performance Metrics")
        await self.show_message("=" * 30)

        if self.streaming_orchestrator is not None:
            try:
                all_workflows = self.streaming_orchestrator.get_all_workflows()

                if all_workflows:
                    # Calculate overall metrics
                    total_sessions = len(all_workflows)
                    total_tokens = sum(w.get('metrics', {}).get('total_tokens', 0) for w in all_workflows.values())
                    total_words = sum(w.get('metrics', {}).get('total_words', 0) for w in all_workflows.values())
                    total_agents = sum(w.get('metrics', {}).get('total_agents', 0) for w in all_workflows.values())

                    await self.show_message(f"📊 Overall Statistics:")
                    await self.show_message(f"  Total Sessions: {total_sessions}")
                    await self.show_message(f"  Total Tokens: {total_tokens:,}")
                    await self.show_message(f"  Total Words: {total_words:,}")
                    await self.show_message(f"  Total Agents: {total_agents}")

                    await self.show_message("\n🔍 Session Details:")
                    for session_id, workflow in all_workflows.items():
                        metrics = workflow.get('metrics', {})
                        status = workflow.get('status', 'unknown')

                        await self.show_message(f"  📂 {session_id}")
                        await self.show_message(f"    Status: {status}")
                        await self.show_message(f"    Tokens: {metrics.get('total_tokens', 0):,}")
                        await self.show_message(f"    Words: {metrics.get('total_words', 0):,}")
                        await self.show_message(f"    Agents: {metrics.get('total_agents', 0)}")
                        await self.show_message("")
                else:
                    await self.show_message("📊 No workflow data available")

            except Exception as e:
                await self.show_error(f"❌ Error retrieving metrics: {e}")
        else:
            await self.show_message("⚠️ Streaming orchestrator not available")

    async def cmd_mode(self, args: List[str]) -> None:
        """Toggle or display execution mode."""
        if args and args[0].lower() in ['streaming', 'legacy']:
            new_mode = args[0].lower()
            if new_mode == 'streaming':
                self.streaming_mode = True
                await self.show_message("✅ Switched to streaming mode")
            else:
                self.streaming_mode = False
                await self.show_message("✅ Switched to legacy mode")
        else:
            current_mode = "Streaming" if self.streaming_mode else "Legacy"
            await self.show_message(f"📊 Current Mode: {current_mode}")
            await self.show_message("Use /mode streaming or /mode legacy to switch")

    async def cmd_exit(self, args: List[str]) -> None:
        """Exit chat mode."""
        await self.show_message("👋 Goodbye! See you next time!")

        # Cleanup resources
        if self.streaming_orchestrator:
            try:
                await self.streaming_orchestrator.cleanup()
            except Exception as e:
                await self.show_error(f"Error during cleanup: {e}")

        if self.monitor:
            try:
                self.monitor.stop_monitoring()
            except Exception as e:
                await self.show_error(f"Error stopping monitor: {e}")

        self.running = False

    # Helper methods
    async def show_message(self, message: str) -> None:
        """Display a message to the user."""
        print(message)

    async def show_error(self, message: str) -> None:
        """Display an error message."""
        print(f"❌ {message}")