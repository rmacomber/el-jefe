# Implementation Guide: Critical Enhancements

This guide provides step-by-step implementation instructions for the most critical enhancements to the AI Orchestrator system.

## 1. Enhanced Agent Manager with Streaming

### Step 1: Update Agent Manager

```python
# src/enhanced_agent_manager.py
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncIterator, Callable
from dataclasses import dataclass, field
from pathlib import Path
import aiofiles

from claude_agent_sdk import query, ClaudeAgentOptions
from .agent_manager import AgentType, AgentConfig
from .monitoring import AgentStatus

@dataclass
class StreamingAgentOptions:
    """Options for streaming agent execution."""
    system_prompt: str
    allowed_tools: List[str]
    max_turns: int
    stream_responses: bool = True
    on_progress: Optional[Callable] = None
    on_tool_use: Optional[Callable] = None
    timeout: Optional[float] = 300.0
    interruptible: bool = True

class StreamingAgentManager:
    """Enhanced agent manager with streaming capabilities."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.active_streams: Dict[str, asyncio.Task] = {}
        self.agent_outputs_dir = workspace_path / "agent_outputs"
        self.agent_outputs_dir.mkdir(exist_ok=True)

    async def spawn_streaming_agent(
        self,
        agent_type: AgentType,
        task_description: str,
        options: StreamingAgentOptions,
        context_files: List[str] = None,
        output_file: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Spawn an agent with streaming output capabilities.

        Yields real-time updates as the agent processes the task.
        """
        agent_id = f"{agent_type.value}_{datetime.now().strftime('%H%M%S')}"

        # Prepare context
        context = await self._prepare_context(context_files or [])
        full_prompt = self._build_prompt(task_description, context)

        # Create SDK options
        sdk_options = ClaudeAgentOptions(
            system_prompt=options.system_prompt,
            allowed_tools=options.allowed_tools,
            max_turns=options.max_turns
        )

        # Yield initialization event
        yield {
            "type": "agent_initialized",
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "task": task_description,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Execute with streaming
            response_buffer = []
            tool_usage_log = []

            async for message in query(prompt=full_prompt, options=sdk_options):
                # Extract content
                content_blocks = getattr(message, 'content', [])

                for block in content_blocks:
                    if getattr(block, "type", None) == "text":
                        text = block.text
                        response_buffer.append(text)

                        # Yield text chunk
                        yield {
                            "type": "text_chunk",
                            "agent_id": agent_id,
                            "content": text,
                            "timestamp": datetime.now().isoformat()
                        }

                        # Call progress callback
                        if options.on_progress:
                            await options.on_progress(agent_id, text)

                    elif getattr(block, "type", None) == "tool_use":
                        tool_info = {
                            "tool": getattr(block, "name", "unknown"),
                            "input": getattr(block, "input", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                        tool_usage_log.append(tool_info)

                        # Yield tool use event
                        yield {
                            "type": "tool_use",
                            "agent_id": agent_id,
                            "tool": tool_info["tool"],
                            "input": tool_info["input"],
                            "timestamp": tool_info["timestamp"]
                        }

                        # Call tool use callback
                        if options.on_tool_use:
                            await options.on_tool_use(agent_id, tool_info)

            # Save complete output
            full_output = "\n".join(response_buffer)
            await self._save_agent_output(agent_id, full_output, output_file)

            # Yield completion event
            yield {
                "type": "agent_completed",
                "agent_id": agent_id,
                "output_file": output_file,
                "total_words": len(full_output.split()),
                "tools_used": [t["tool"] for t in tool_usage_log],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Yield error event
            yield {
                "type": "agent_error",
                "agent_id": agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            raise

    async def spawn_parallel_agents(
        self,
        agent_configs: List[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Spawn multiple agents in parallel and yield their updates.

        Useful for workflows that can run tasks concurrently.
        """
        async def agent_wrapper(config: Dict[str, Any]):
            async for update in self.spawn_streaming_agent(**config):
                update["batch_id"] = config.get("batch_id")
                yield update

        # Create tasks for all agents
        tasks = [
            agent_wrapper(config)
            for config in agent_configs
        ]

        # Execute in parallel and merge streams
        async for update in self._merge_streams(tasks):
            yield update

    async def _merge_streams(
        self,
        streams: List[AsyncIterator]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Merge multiple async streams into one."""
        queues = [asyncio.Queue(maxsize=100) for _ in streams]

        # Create producer tasks
        async def producer(stream: AsyncIterator, queue: asyncio.Queue):
            async for item in stream:
                await queue.put(item)
            await queue.put(None)  # Sentinel

        producers = [
            asyncio.create_task(producer(s, q))
            for s, q in zip(streams, queues)
        ]

        # Consumer loop
        active_producers = len(producers)
        while active_producers > 0:
            # Wait for any queue to have an item
            done, _ = await asyncio.wait(
                [q.get() for q in queues],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                item = task.result()
                if item is None:
                    active_producers -= 1
                else:
                    yield item

    async def interrupt_agent(self, agent_id: str) -> bool:
        """Interrupt a running agent."""
        if agent_id in self.active_streams:
            self.active_streams[agent_id].cancel()
            del self.active_streams[agent_id]
            return True
        return False
```

### Step 2: Update Orchestrator to Use Streaming

```python
# src/enhanced_orchestrator.py
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .enhanced_agent_manager import StreamingAgentManager, StreamingAgentOptions
from .agent_manager import AgentType, AgentConfig
from .monitoring import ProgressMonitor, AgentStatus
from .workspace_manager import WorkspaceManager

class StreamingOrchestrator:
    """Orchestrator with real-time streaming capabilities."""

    def __init__(
        self,
        base_dir: str = "workspaces",
        enable_monitoring: bool = True
    ):
        self.workspace_manager = WorkspaceManager(base_dir)
        self.monitor = ProgressMonitor() if enable_monitoring else None
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    async def execute_goal_streaming(
        self,
        goal: str,
        session_id: Optional[str] = None
    ):
        """
        Execute a goal with real-time streaming output.

        Yields progress updates as the workflow executes.
        """
        # Create session
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create workspace
        task_name = goal.lower().replace(" ", "-")[:20]
        workspace_info = await self.workspace_manager.create_workspace(
            task_name=task_name,
            task_description=goal
        )
        workspace_path = Path(workspace_info["path"])

        # Initialize agent manager
        agent_manager = StreamingAgentManager(workspace_path)

        # Create monitoring session
        if self.monitor:
            monitor_session = self.monitor.create_session(
                session_id,
                str(workspace_path)
            )

        # Workflow state
        workflow_state = {
            "session_id": session_id,
            "goal": goal,
            "workspace": str(workspace_path),
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "current_step": 0
        }

        yield {
            "type": "workflow_started",
            "session_id": session_id,
            "goal": goal,
            "workspace": str(workspace_path),
            "timestamp": datetime.now().isoformat()
        }

        # Determine workflow steps
        steps = await self._plan_workflow(goal)
        workflow_state["steps"] = steps

        # Execute steps
        for i, step in enumerate(steps):
            workflow_state["current_step"] = i

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
                on_progress=lambda aid, txt: self._on_progress(
                    session_id, aid, txt
                )
            )

            # Execute agent
            agent_outputs = []
            async for update in agent_manager.spawn_streaming_agent(
                agent_type=AgentType(step["agent_type"]),
                task_description=step["task"],
                options=options,
                context_files=step.get("context_files", []),
                output_file=step.get("output_file"),
                session_id=session_id
            ):
                # Add session info to all updates
                update["session_id"] = session_id
                update["step"] = i + 1

                # Store agent outputs
                if update["type"] == "text_chunk":
                    agent_outputs.append(update["content"])

                # Yield update
                yield update

            # Step completed
            step_result = {
                "step": i + 1,
                "agent_type": step["agent_type"],
                "output": "".join(agent_outputs),
                "completed_at": datetime.now().isoformat()
            }
            workflow_state["steps_completed"] = workflow_state.get(
                "steps_completed", []
            ) + [step_result]

            yield {
                "type": "step_completed",
                "session_id": session_id,
                "step": i + 1,
                "result": step_result,
                "timestamp": datetime.now().isoformat()
            }

        # Workflow completed
        workflow_state["completed_at"] = datetime.now().isoformat()

        yield {
            "type": "workflow_completed",
            "session_id": session_id,
            "goal": goal,
            "workspace": str(workspace_path),
            "total_steps": len(steps),
            "timestamp": datetime.now().isoformat()
        }

    async def _on_progress(self, session_id: str, agent_id: str, text: str):
        """Handle progress updates from agents."""
        if self.monitor:
            # Update monitoring state
            pass

    async def _plan_workflow(self, goal: str) -> List[Dict[str, Any]]:
        """Plan workflow steps for the goal."""
        # Import existing task planner
        from .task_planner import TaskPlanner
        planner = TaskPlanner()

        task_plan = await planner.create_task_plan(goal)
        return task_plan["steps"]
```

## 2. Real-Time Progress Monitor Integration

### Step 1: Enhanced Monitoring with SDK Integration

```python
# src/enhanced_monitoring.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, AsyncIterator
from dataclasses import dataclass, field, asdict
from pathlib import Path
import psutil

from claude_agent_sdk import ClaudeAgentOptions
from .monitoring import AgentStatus, WorkflowSession

@dataclass
class PerformanceMetrics:
    """Detailed performance metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_io_read: int = 0
    disk_io_write: int = 0
    network_io_sent: int = 0
    network_io_recv: int = 0

@dataclass
class SDKMetrics:
    """SDK-specific metrics."""
    tokens_used: int = 0
    api_calls: int = 0
    response_times: List[float] = field(default_factory=list)
    tool_calls: int = 0
    errors: int = 0

class EnhancedProgressMonitor:
    """Enhanced progress monitor with SDK integration."""

    def __init__(self, storage_path: Path = Path("monitoring")):
        self.storage_path = storage_path
        self.storage_path.mkdir(exist_ok=True)

        self.active_sessions: Dict[str, WorkflowSession] = {}
        self.agent_metrics: Dict[str, SDKMetrics] = {}
        self.performance_history: List[Dict[str, Any]] = []

        # Real-time subscribers
        self.subscribers: Dict[str, asyncio.Queue] = {}

        # Start background collection
        self.running = True
        self.collection_task = asyncio.create_task(self._collect_metrics())

    async def create_monitoring_stream(
        self,
        session_id: str,
        agent_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Create a real-time monitoring stream.

        Provides continuous updates about agent execution.
        """
        stream_id = f"{session_id}_{agent_id}_{datetime.now().timestamp()}"
        queue = asyncio.Queue(maxsize=1000)
        self.subscribers[stream_id] = queue

        try:
            while True:
                # Collect current metrics
                metrics = {
                    "type": "metrics_update",
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "performance": self._get_performance_metrics(),
                    "session_status": self._get_session_status(session_id),
                    "agent_status": self._get_agent_status(agent_id) if agent_id else None
                }

                # Send metrics
                await queue.put(metrics)

                # Wait before next update
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass
        finally:
            if stream_id in self.subscribers:
                del self.subscribers[stream_id]

    async def track_sdk_execution(
        self,
        agent_id: str,
        execution_coro
    ):
        """
        Track SDK execution with detailed metrics.

        Wraps SDK execution to collect performance data.
        """
        metrics = SDKMetrics()
        self.agent_metrics[agent_id] = metrics

        start_time = datetime.now()

        try:
            # Track API call
            metrics.api_calls += 1

            # Execute and time
            result = await execution_coro

            # Record response time
            response_time = (datetime.now() - start_time).total_seconds()
            metrics.response_times.append(response_time)

            # Extract token usage if available
            if hasattr(result, 'usage'):
                metrics.tokens_used += result.usage.get('total_tokens', 0)

            return result

        except Exception as e:
            metrics.errors += 1
            raise

    async def _collect_metrics(self):
        """Background task to collect system metrics."""
        while self.running:
            try:
                # Get system metrics
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_io_counters()
                net = psutil.net_io_counters()

                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": cpu,
                    "memory_percent": memory.percent,
                    "memory_mb": memory.used / 1024 / 1024,
                    "disk_read": disk.read_bytes if disk else 0,
                    "disk_write": disk.write_bytes if disk else 0,
                    "net_sent": net.bytes_sent if net else 0,
                    "net_recv": net.bytes_recv if net else 0
                }

                self.performance_history.append(metrics)

                # Keep only last 1000 entries
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]

                # Check for alerts
                await self._check_alerts(metrics)

                await asyncio.sleep(5)  # Collect every 5 seconds

            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.performance_history:
            return {}

        latest = self.performance_history[-1]
        return {
            "cpu": latest["cpu_percent"],
            "memory": latest["memory_percent"],
            "memory_mb": latest["memory_mb"],
            "disk_io": {
                "read": latest["disk_read"],
                "write": latest["disk_write"]
            },
            "network_io": {
                "sent": latest["net_sent"],
                "recv": latest["net_recv"]
            }
        }

    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for performance alerts."""
        alerts = []

        if metrics["cpu_percent"] > 90:
            alerts.append({
                "type": "high_cpu",
                "value": metrics["cpu_percent"],
                "threshold": 90
            })

        if metrics["memory_percent"] > 90:
            alerts.append({
                "type": "high_memory",
                "value": metrics["memory_percent"],
                "threshold": 90
            })

        # Broadcast alerts
        for alert in alerts:
            await self._broadcast_alert(alert)

    async def _broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast alert to all subscribers."""
        alert_msg = {
            "type": "alert",
            "alert": alert,
            "timestamp": datetime.now().isoformat()
        }

        for queue in self.subscribers.values():
            if not queue.full():
                await queue.put(alert_msg)
```

## 3. Integration Example

### Example: Streaming Workflow Execution

```python
# examples/streaming_workflow.py
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.enhanced_orchestrator import StreamingOrchestrator

async def main():
    """Run streaming workflow example."""

    orchestrator = StreamingOrchestrator(enable_monitoring=True)

    # Define goal
    goal = "Research the latest AI developments for a tech podcast"

    print(f"🚀 Starting streaming workflow: {goal}")
    print("-" * 50)

    # Execute with streaming
    async for update in orchestrator.execute_goal_streaming(goal):
        timestamp = update["timestamp"][-8:]  # Last 8 chars for time

        if update["type"] == "workflow_started":
            print(f"\n[{timestamp}] 📂 Workflow started")
            print(f"  Session: {update['session_id']}")
            print(f"  Workspace: {update['workspace']}")

        elif update["type"] == "step_started":
            print(f"\n[{timestamp}] ⚡ Step {update['step']}/{update['total_steps']}")
            print(f"  Agent: {update['agent_type']}")
            print(f"  Task: {update['description']}")

        elif update["type"] == "text_chunk":
            # Show real-time text output (truncated)
            text = update["content"][:100]
            if len(update["content"]) > 100:
                text += "..."
            print(f"  📝 {text}")

        elif update["type"] == "tool_use":
            print(f"  🔧 Using tool: {update['tool']}")

        elif update["type"] == "agent_completed":
            print(f"\n[{timestamp}] ✅ Agent completed")
            print(f"  Words: {update['total_words']}")
            print(f"  Tools used: {', '.join(update['tools_used'])}")

        elif update["type"] == "workflow_completed":
            print(f"\n[{timestamp}] 🎉 Workflow completed!")
            print(f"  Total steps: {update['total_steps']}")
            print(f"  Workspace: {update['workspace']}")

            # Show generated files
            workspace_path = Path(update['workspace'])
            if workspace_path.exists():
                print("\n📄 Generated files:")
                for file_path in sorted(workspace_path.glob("*.md")):
                    size = file_path.stat().st_size
                    print(f"  - {file_path.name} ({size} bytes)")

            break

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Installation and Setup

### Step 1: Update Dependencies

```bash
# Add to requirements.txt
psutil>=5.9.0          # System monitoring
websockets>=11.0       # Real-time communication
aiofiles>=23.0.0       # Async file operations
python-socketio>=5.8   # Real-time events
```

### Step 2: Update Main Entry Point

```python
# main.py updates
async def execute_goal_streaming(orchestrator, ui, goal):
    """Execute goal with streaming output."""
    await ui.show_info(f"Starting streaming execution: {goal}")

    stream_orchestrator = StreamingOrchestrator()

    async for update in stream_orchestrator.execute_goal_streaming(goal):
        # Display updates based on type
        if update["type"] == "workflow_started":
            await ui.show_success(f"Started workflow in session: {update['session_id']}")
        elif update["type"] == "step_completed":
            await ui.show_info(f"Step {update['step']} completed")
        elif update["type"] == "workflow_completed":
            await ui.show_success("Workflow completed successfully!")
            await ui.show_info(f"Results in: {update['workspace']}")

# Add to argument parser
parser.add_argument(
    "--streaming", "-s",
    action="store_true",
    help="Enable streaming output mode"
)
```

## 5. Testing the Implementation

### Test 1: Basic Streaming

```python
# tests/test_streaming.py
import pytest
import asyncio
from src.enhanced_orchestrator import StreamingOrchestrator

@pytest.mark.asyncio
async def test_streaming_execution():
    """Test basic streaming workflow execution."""
    orchestrator = StreamingOrchestrator(enable_monitoring=False)

    updates = []
    goal = "Write a brief summary of Python"

    async for update in orchestrator.execute_goal_streaming(goal):
        updates.append(update)

        # Check for required update types
        assert "type" in update
        assert "timestamp" in update

    # Verify workflow completed
    assert any(u["type"] == "workflow_completed" for u in updates)
    assert any(u["type"] == "step_completed" for u in updates)

if __name__ == "__main__":
    asyncio.run(test_streaming_execution())
```

## 6. Next Steps

1. **Implement WebSocket server** for real-time UI updates
2. **Add persistence layer** for session recovery
3. **Create monitoring dashboard** with live metrics
4. **Implement error recovery** and retry logic
5. **Add plugin system** for extensibility
6. **Create API endpoints** for external integration

This implementation provides a solid foundation for an enhanced AI Orchestrator that fully leverages the Claude Agent SDK's capabilities while adding powerful features for real-time monitoring, streaming output, and dynamic workflow management.