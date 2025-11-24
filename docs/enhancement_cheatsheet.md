# AI Orchestrator Enhancement Cheat Sheet

## Quick Reference for Enhanced Features

## 1. Streaming Agent Execution

### Basic Usage
```python
from src.enhanced_agent_manager import StreamingAgentManager, StreamingAgentOptions

# Initialize manager
manager = StreamingAgentManager(workspace_path)

# Configure streaming options
options = StreamingAgentOptions(
    system_prompt="You are a research specialist...",
    allowed_tools=["search_web", "write_md"],
    max_turns=8,
    stream_responses=True,
    on_progress=lambda aid, text: print(f"Progress: {len(text)} chars")
)

# Execute with streaming
async for update in manager.spawn_streaming_agent(
    agent_type=AgentType.RESEARCHER,
    task_description="Research AI trends",
    options=options,
    output_file="research.md"
):
    if update["type"] == "text_chunk":
        print(update["content"])
    elif update["type"] == "tool_use":
        print(f"Using tool: {update['tool']}")
```

### Event Types
- `agent_initialized` - Agent started
- `text_chunk` - Text response fragment
- `tool_use` - Tool execution event
- `agent_completed` - Agent finished
- `agent_error` - Error occurred

## 2. Real-Time Monitoring

### Setup Monitoring
```python
from src.enhanced_monitoring import EnhancedProgressMonitor

# Initialize monitor
monitor = EnhancedProgressMonitor(storage_path=Path("monitoring"))

# Create monitoring stream
async for metrics in monitor.create_monitoring_stream(
    session_id="session_123",
    agent_id="researcher_1430"
):
    print(f"CPU: {metrics['performance']['cpu']}%")
    print(f"Memory: {metrics['performance']['memory']}%")
```

### Track SDK Execution
```python
# Wrap SDK calls for metrics tracking
result = await monitor.track_sdk_execution(
    agent_id="agent_123",
    execution_coro=agent_sdk_call()
)
```

## 3. Streaming Orchestrator

### Execute Goal with Streaming
```python
from src.enhanced_orchestrator import StreamingOrchestrator

orchestrator = StreamingOrchestrator(enable_monitoring=True)

async for update in orchestrator.execute_goal_streaming(
    goal="Research AI trends for podcast",
    session_id="podcast_research_123"
):
    if update["type"] == "step_started":
        print(f"Starting: {update['description']}")
    elif update["type"] == "text_chunk":
        print(f"Output: {update['content'][:100]}...")
    elif update["type"] == "workflow_completed":
        print(f"Done! Results in: {update['workspace']}")
```

## 4. Session Management

### Create and Restore Sessions
```python
from src.session_manager import AdvancedSessionManager

session_mgr = AdvancedSessionManager(Path("sessions"))

# Create session
version_id = await session_mgr.create_session(
    session_id="my_session",
    initial_state={
        "workflow": {"goal": "..."},
        "agents": {...},
        "history": [...]
    }
)

# Update session
await session_mgr.update_session(
    session_id="my_session",
    updates={"workflow": {"step": 2}},
    create_snapshot=True
)

# Resume session
state = await session_mgr.resume_session(
    session_id="my_session",
    version_id="latest"  # or specific version
)
```

## 5. Event System

### Subscribe to Events
```python
from src.event_system import EventBus, EventType

# Create event bus
event_bus = EventBus()

# Subscribe to events
def on_agent_completed(event):
    print(f"Agent {event.data['agent_id']} completed!")

event_bus.subscribe(EventType.AGENT_COMPLETED, on_agent_completed)

# Publish events
await event_bus.publish(Event(
    event_id="evt_001",
    event_type=EventType.AGENT_COMPLETED,
    timestamp=datetime.now(),
    source="orchestrator",
    data={"agent_id": "researcher_123"},
    session_id="session_456"
))
```

## 6. Plugin System

### Create Custom Plugin
```python
from src.plugin_system import BasePlugin, PluginMetadata

@dataclass
class MyPluginMetadata(PluginMetadata):
    name: str = "my_plugin"
    version: str = "1.0.0"
    description: str = "My custom plugin"
    author: str = "Me"
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    agent_types: List[str] = field(default_factory=lambda: ["researcher"])

class MyPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return MyPluginMetadata()

    async def initialize(self, config, context):
        # Initialize plugin
        pass

    async def execute(self, input_data, context):
        # Plugin logic
        return {"result": "processed"}

# Load plugin
plugin_mgr = PluginManager()
await plugin_mgr.load_plugin(
    plugin_path="plugins/my_plugin.py",
    config={"option": "value"}
)
```

## 7. Performance Optimization

### Parallel Agent Execution
```python
# Execute multiple agents in parallel
configs = [
    {
        "agent_type": AgentType.RESEARCHER,
        "task_description": "Research topic A",
        "options": options,
        "batch_id": "batch_001"
    },
    {
        "agent_type": AgentType.RESEARCHER,
        "task_description": "Research topic B",
        "options": options,
        "batch_id": "batch_001"
    }
]

async for update in agent_manager.spawn_parallel_agents(configs):
    print(f"Batch {update['batch_id']}: {update['type']}")
```

### Context Optimization
```python
# Compress context for large sessions
compressed_context = session_mgr.compress_context(
    session_context,
    preserve_keys=["goal", "current_step", "agent_results"]
)

# Create session diff
diff = await session_mgr.create_session_diff(
    session_id="my_session",
    from_version="v1",
    to_version="v2"
)
```

## 8. Error Handling

### Agent Error Recovery
```python
try:
    async for update in manager.spawn_streaming_agent(...):
        # Process updates
        pass
except Exception as e:
    # Get recovery suggestions
    recovery = await manager.get_recovery_suggestions(e)
    print(f"Suggested action: {recovery['action']}")
```

### Workflow Resumption
```python
# Resume interrupted workflow
if workflow_state["status"] == "interrupted":
    async for update in orchestrator.resume_workflow(
        session_id=workflow_state["session_id"],
        from_step=workflow_state["last_completed_step"]
    ):
        # Continue execution
        pass
```

## 9. Monitoring Commands

### CLI Integration
```bash
# Start with streaming
python main.py --streaming "Research AI trends"

# Resume session
python main.py --resume sessions/session_123/latest

# Monitor active sessions
python main.py --monitor

# Clean up old sessions
python main.py --cleanup 7  # 7 days
```

### Real-time Dashboard
```python
# Start dashboard server
from src.dashboard import DashboardServer

dashboard = DashboardServer(port=8080)
await dashboard.start()

# Access at http://localhost:8080
```

## 10. Best Practices

### Performance
- Use streaming for long-running tasks
- Monitor token usage and costs
- Compress context for large sessions
- Use parallel execution when possible

### Reliability
- Create session snapshots regularly
- Implement retry logic for failures
- Monitor system resources
- Set appropriate timeouts

### Security
- Validate plugin permissions
- Restrict file access to workspaces
- Sanitize agent outputs
- Use secure session storage

### Scalability
- Use event-driven architecture
- Implement connection pooling
- Cache frequently used data
- Load balance across instances

## 11. Debugging

### Enable Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use verbose flag
orchestrator = StreamingOrchestrator(verbose=True)
```

### Common Issues
1. **Agent not responding** - Check timeout settings
2. **Memory issues** - Monitor context size
3. **Slow execution** - Check token usage
4. **Lost updates** - Verify event subscriptions

### Debug Commands
```python
# Get session state
state = await session_mgr.get_active_session("session_id")

# List active agents
agents = await agent_manager.list_active_agents()

# Get performance metrics
metrics = monitor.get_performance_metrics()
```

## 12. Migration Guide

### From Basic to Enhanced
```python
# Old way
result = await orchestrator.execute_goal("Research AI")

# New way with streaming
async for update in orchestrator.execute_goal_streaming("Research AI"):
    # Handle real-time updates
    pass

# Enhanced agent spawning
# Old: agent_manager.spawn_agent(...)
# New: agent_manager.spawn_streaming_agent(...)
```

### Backward Compatibility
- Existing agent configs work unchanged
- Can run both modes side by side
- Gradual migration possible