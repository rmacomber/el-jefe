"""
Enhanced Agent Manager with Streaming Capabilities

Provides real-time streaming output, parallel agent execution,
and advanced monitoring integration with the Claude Agent SDK.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncIterator, Callable
from dataclasses import dataclass, field
from pathlib import Path
import aiofiles
import uuid

from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions
from agent_manager import AgentType, AgentConfig
from monitoring import AgentStatus


@dataclass
class StreamingAgentOptions:
    """Enhanced options for streaming agent execution."""
    system_prompt: str
    allowed_tools: List[str]
    max_turns: int
    stream_responses: bool = True
    on_progress: Optional[Callable] = None
    on_tool_use: Optional[Callable] = None
    timeout: Optional[float] = 300.0
    interruptible: bool = True
    session_id: Optional[str] = None
    priority: str = "normal"  # "low", "normal", "high"


@dataclass
class AgentMetrics:
    """Real-time metrics for agent execution."""
    agent_id: str
    tokens_used: int = 0
    api_calls: int = 0
    response_time: float = 0.0
    tool_calls: int = 0
    words_generated: int = 0
    error_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


class StreamingAgentManager:
    """Enhanced agent manager with real-time streaming capabilities."""

    def __init__(self, workspace_path: Path, monitoring_callback: Optional[Callable] = None):
        self.workspace_path = workspace_path
        self.monitoring_callback = monitoring_callback
        self.active_streams: Dict[str, asyncio.Task] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.agent_outputs_dir = workspace_path / "agent_outputs"
        self.agent_outputs_dir.mkdir(exist_ok=True)

        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.workflow_state = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "agents_spawned": [],
            "total_tokens": 0,
            "total_words": 0
        }

    async def spawn_streaming_agent(
        self,
        agent_type: AgentType,
        task_description: str,
        options: StreamingAgentOptions,
        context_files: List[str] = None,
        output_file: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Spawn an agent with real-time streaming output capabilities.

        Yields updates as the agent processes the task including:
        - Agent initialization
        - Real-time text chunks
        - Tool usage events
        - Progress updates
        - Completion status
        """
        agent_id = f"{agent_type.value}_{datetime.now().strftime('%H%M%S')}_{str(uuid.uuid4())[:8]}"

        # Initialize metrics
        self.agent_metrics[agent_id] = AgentMetrics(
            agent_id=agent_id,
            start_time=datetime.now()
        )

        # Update workflow state
        self.workflow_state["agents_spawned"].append({
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "task": task_description,
            "started_at": datetime.now().isoformat()
        })

        # Prepare context
        context = await self._prepare_context(context_files or [])
        full_prompt = self._build_prompt(task_description, context)

        # Create SDK options
        sdk_options = ClaudeAgentOptions(
            system_prompt=options.system_prompt,
            allowed_tools=options.allowed_tools,
            max_turns=options.max_turns
        )

        # Create agent status for monitoring
        agent_status = AgentStatus(
            agent_id=agent_id,
            agent_type=agent_type.value,
            task=task_description,
            status='starting',
            progress=0.0,
            current_step="Initializing agent",
            total_steps=options.max_turns,
            current_step_index=0,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            workspace_path=str(self.workspace_path),
            messages=[],
            metadata={"session_id": options.session_id or self.session_id},
            session_id=options.session_id or self.session_id
        )

        # Notify monitoring callback
        if self.monitoring_callback:
            try:
                await self.monitoring_callback(agent_status)
            except Exception as e:
                print(f"Error in monitoring callback: {e}")

        # Yield initialization event
        yield {
            "type": "agent_initialized",
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "task": task_description,
            "session_id": options.session_id or self.session_id,
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace_path)
        }

        try:
            # Update agent status to running
            agent_status.status = 'running'
            agent_status.current_step = f"Executing: {task_description}"
            if self.monitoring_callback:
                await self.monitoring_callback(agent_status)

            # Execute with streaming
            response_buffer = []
            tool_usage_log = []
            tokens_used = 0
            api_calls = 0

            async for message in query(prompt=full_prompt, options=sdk_options):
                # Track metrics
                api_calls += 1
                agent_status.last_activity = datetime.now()

                # Extract content from SDK message
                content_blocks = getattr(message, 'content', [])

                for block in content_blocks:
                    if getattr(block, "type", None) == "text":
                        text = block.text
                        response_buffer.append(text)

                        # Update metrics
                        words = len(text.split())
                        self.agent_metrics[agent_id].words_generated += words
                        self.workflow_state["total_words"] += words

                        # Update progress
                        progress = min(0.9, self.agent_metrics[agent_id].words_generated / 500)  # Estimate progress
                        agent_status.progress = progress

                        # Yield text chunk
                        yield {
                            "type": "text_chunk",
                            "agent_id": agent_id,
                            "agent_type": agent_type.value,
                            "content": text,
                            "session_id": options.session_id or self.session_id,
                            "timestamp": datetime.now().isoformat(),
                            "word_count": words,
                            "progress": progress
                        }

                        # Call progress callback
                        if options.on_progress:
                            try:
                                await options.on_progress(agent_id, text)
                            except Exception as e:
                                print(f"Error in progress callback: {e}")

                        # Notify monitoring callback
                        if self.monitoring_callback:
                            await self.monitoring_callback(agent_status)

                    elif getattr(block, "type", None) == "tool_use":
                        tool_info = {
                            "tool": getattr(block, "name", "unknown"),
                            "input": getattr(block, "input", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                        tool_usage_log.append(tool_info)

                        # Update metrics
                        self.agent_metrics[agent_id].tool_calls += 1
                        agent_status.current_step = f"Using tool: {tool_info['tool']}"

                        # Yield tool use event
                        yield {
                            "type": "tool_use",
                            "agent_id": agent_id,
                            "agent_type": agent_type.value,
                            "tool": tool_info["tool"],
                            "tool_input": tool_info["input"],
                            "session_id": options.session_id or self.session_id,
                            "timestamp": tool_info["timestamp"]
                        }

                        # Call tool use callback
                        if options.on_tool_use:
                            try:
                                await options.on_tool_use(agent_id, tool_info)
                            except Exception as e:
                                print(f"Error in tool use callback: {e}")

                        # Notify monitoring callback
                        if self.monitoring_callback:
                            await self.monitoring_callback(agent_status)

                    # Track token usage if available
                    if hasattr(message, 'usage'):
                        usage = getattr(message, 'usage', {})
                        if isinstance(usage, dict):
                            tokens = usage.get('total_tokens', 0)
                            tokens_used += tokens
                            self.agent_metrics[agent_id].tokens_used += tokens
                            self.workflow_state["total_tokens"] += tokens

            # Finalize metrics
            self.agent_metrics[agent_id].api_calls = api_calls
            self.agent_metrics[agent_id].tokens_used = tokens_used

            # Save complete output
            full_output = "\n".join(response_buffer)
            output_path = await self._save_agent_output(agent_id, full_output, output_file)

            # Update agent status to completed
            agent_status.status = 'completed'
            agent_status.progress = 1.0
            agent_status.current_step = "Completed"
            agent_status.last_activity = datetime.now()

            # Update metrics completion time
            self.agent_metrics[agent_id].end_time = datetime.now()
            response_time = (self.agent_metrics[agent_id].end_time -
                           self.agent_metrics[agent_id].start_time).total_seconds()
            self.agent_metrics[agent_id].response_time = response_time

            # Notify monitoring callback
            if self.monitoring_callback:
                await self.monitoring_callback(agent_status)

            # Yield completion event
            yield {
                "type": "agent_completed",
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "output_file": output_file,
                "output_preview": full_output[:200] + "..." if len(full_output) > 200 else full_output,
                "total_words": self.agent_metrics[agent_id].words_generated,
                "total_tokens": self.agent_metrics[agent_id].tokens_used,
                "api_calls": self.agent_metrics[agent_id].api_calls,
                "tool_calls": self.agent_metrics[agent_id].tool_calls,
                "response_time": response_time,
                "tools_used": [t["tool"] for t in tool_usage_log],
                "session_id": options.session_id or self.session_id,
                "timestamp": datetime.now().isoformat()
            }

        except asyncio.CancelledError:
            # Handle interruption
            agent_status.status = 'interrupted'
            agent_status.metadata['interruption_reason'] = 'User cancelled'
            agent_status.last_activity = datetime.now()

            self.agent_metrics[agent_id].end_time = datetime.now()

            if self.monitoring_callback:
                await self.monitoring_callback(agent_status)

            yield {
                "type": "agent_interrupted",
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "reason": "User cancelled",
                "session_id": options.session_id or self.session_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            # Handle error
            agent_status.status = 'failed'
            agent_status.metadata['error'] = str(e)
            agent_status.last_activity = datetime.now()
            self.agent_metrics[agent_id].error_count += 1

            if self.monitoring_callback:
                await self.monitoring_callback(agent_status)

            yield {
                "type": "agent_error",
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "error": str(e),
                "session_id": options.session_id or self.session_id,
                "timestamp": datetime.now().isoformat()
            }

    async def spawn_parallel_agents(
        self,
        agent_configs: List[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Spawn multiple agents in parallel and yield their updates.

        Useful for workflows that can run tasks concurrently like
        parallel research or simultaneous code generation.
        """
        async def agent_wrapper(config: Dict[str, Any]):
            async for update in self.spawn_streaming_agent(**config):
                update["batch_id"] = config.get("batch_id", "parallel")
                yield update

        # Create tasks for all agents
        tasks = [
            agent_wrapper(config)
            for config in agent_configs
        ]

        # Execute in parallel and merge streams
        async for update in self._merge_streams(tasks):
            yield update

    async def interrupt_agent(self, agent_id: str) -> bool:
        """Interrupt a running agent gracefully."""
        if agent_id in self.active_streams:
            self.active_streams[agent_id].cancel()
            del self.active_streams[agent_id]

            # Update agent status
            for agent_status in self.get_active_agents():
                if agent_status.agent_id == agent_id:
                    agent_status.status = 'interrupted'
                    agent_status.metadata['interruption_reason'] = 'Manual interruption'
                    break

            return True
        return False

    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get detailed metrics for a specific agent."""
        return self.agent_metrics.get(agent_id)

    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get overall workflow metrics."""
        total_tokens = sum(m.tokens_used for m in self.agent_metrics.values())
        total_words = sum(m.words_generated for m in self.agent_metrics.values())
        total_api_calls = sum(m.api_calls for m in self.agent_metrics.values())
        total_tool_calls = sum(m.tool_calls for m in self.agent_metrics.values())

        completed_agents = sum(1 for m in self.agent_metrics.values() if m.end_time)
        avg_response_time = 0

        if completed_agents > 0:
            total_time = sum(
                (m.end_time - m.start_time).total_seconds()
                for m in self.agent_metrics.values()
                if m.end_time
            )
            avg_response_time = total_time / completed_agents

        return {
            "session_id": self.session_id,
            "total_agents": len(self.agent_metrics),
            "completed_agents": completed_agents,
            "total_tokens": total_tokens,
            "total_words": total_words,
            "total_api_calls": total_api_calls,
            "total_tool_calls": total_tool_calls,
            "average_response_time": avg_response_time,
            "agent_metrics": {
                aid: {
                    "tokens_used": m.tokens_used,
                    "words_generated": m.words_generated,
                    "api_calls": m.api_calls,
                    "tool_calls": m.tool_calls,
                    "response_time": m.response_time,
                    "error_count": m.error_count,
                    "status": "completed" if m.end_time else "running"
                }
                for aid, m in self.agent_metrics.items()
            }
        }

    async def _prepare_context(self, context_files: List[str]) -> str:
        """Prepare context from files."""
        context_parts = []

        for file_path in context_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                async with aiofiles.open(full_path, 'r') as f:
                    content = await f.read()
                    context_parts.append(f"=== {file_path} ===\n{content}\n")

        return "\n".join(context_parts)

    def _build_prompt(self, task_description: str, context: str) -> str:
        """Build the full prompt for the agent."""
        if context:
            return f"""CONTEXT:
{context}

TASK:
{task_description}

Please complete this task based on the provided context. Provide a comprehensive and well-structured response."""
        else:
            return task_description

    async def _save_agent_output(
        self,
        agent_id: str,
        content: str,
        output_file: Optional[str] = None
    ) -> str:
        """Save agent output to file."""
        if output_file:
            file_path = self.workspace_path / output_file
        else:
            file_path = self.agent_outputs_dir / f"{agent_id}_output.md"

        async with aiofiles.open(file_path, 'w') as f:
            await f.write(f"# Agent Output: {agent_id}\n\n")
            await f.write(f"Generated at: {datetime.now().isoformat()}\n\n")
            await f.write("---\n\n")
            await f.write(content)

        return str(file_path)

    async def _merge_streams(
        self,
        streams: List[AsyncIterator]
    ) -> AsyncIterator[Dict[str, Any]]:
        """Merge multiple async streams into one with proper ordering."""
        queues = [asyncio.Queue(maxsize=100) for _ in streams]

        # Create producer tasks
        async def producer(stream: AsyncIterator, queue: asyncio.Queue):
            try:
                async for item in stream:
                    await queue.put(item)
            except Exception as e:
                await queue.put({"type": "stream_error", "error": str(e)})
            finally:
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
                try:
                    item = task.result()
                    if item is None:
                        active_producers -= 1
                    else:
                        yield item
                except Exception as e:
                    yield {"type": "merge_error", "error": str(e)}

        # Clean up producer tasks
        for producer in producers:
            if not producer.done():
                producer.cancel()

    def get_active_agents(self) -> List[AgentStatus]:
        """Get list of active agents (placeholder for monitoring integration)."""
        # This would integrate with the monitoring system
        return []

    async def cleanup(self):
        """Clean up resources and cancel all active streams."""
        for agent_id, task in self.active_streams.items():
            if not task.done():
                task.cancel()

        # Wait for tasks to complete cancellation
        if self.active_streams:
            await asyncio.gather(*self.active_streams.values(), return_exceptions=True)

        self.active_streams.clear()