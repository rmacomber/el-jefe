"""
Agent Manager Module

Handles spawning and coordinating specialist agents for different tasks.
Manages agent lifecycle, tool authorization, and result collection.
"""

import json
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import aiofiles

from claude_agent_sdk import query, ClaudeAgentOptions


class AgentType(Enum):
    """Enumeration of available agent types."""
    RESEARCHER = "researcher"
    CODER = "coder"
    WRITER = "writer"
    ANALYST = "analyst"
    DESIGNER = "designer"
    QA_TESTER = "qa_tester"
    # Template-based agents
    SECURITY_ANALYST = "security_analyst"
    DATA_SCIENTIST = "data_scientist"
    API_DEVELOPER = "api_developer"


class AgentConfig:
    """Configuration for agent types."""

    AGENT_CONFIGS = {
        AgentType.RESEARCHER: {
            "system_prompt": "You are a research specialist. Your task is to gather, synthesize, and present information in a clear, structured manner. Use credible sources and always verify facts. Present findings in well-organized bullet points with proper attribution.",
            "allowed_tools": ["search_web", "write_md", "read_files"],
            "max_turns": 8,
            "description": "Researches and synthesizes information from various sources"
        },
        AgentType.CODER: {
            "system_prompt": "You are a senior software developer. Write clean, well-documented, and efficient code. Follow best practices and design patterns. Include error handling and comments where necessary. Focus on Python but can work with other languages as needed.",
            "allowed_tools": ["write_md", "write_file", "read_files", "list_directory"],
            "max_turns": 6,
            "description": "Builds software solutions and writes scripts"
        },
        AgentType.WRITER: {
            "system_prompt": "You are a professional writer and content creator. Create engaging, clear, and well-structured content. Adapt your tone to the target audience. Focus on readability, coherence, and proper grammar.",
            "allowed_tools": ["write_md", "read_files"],
            "max_turns": 6,
            "description": "Creates and edits documents and content"
        },
        AgentType.ANALYST: {
            "system_prompt": "You are a data analyst and trend specialist. Analyze data patterns, identify trends, and provide actionable insights. Use quantitative methods and present findings with supporting evidence.",
            "allowed_tools": ["search_web", "write_md", "read_files", "analyze_data"],
            "max_turns": 7,
            "description": "Performs data analysis and trend identification"
        },
        AgentType.DESIGNER: {
            "system_prompt": "You are a system architect and designer. Create scalable, maintainable system designs and architectures. Consider best practices, security, and performance. Provide clear documentation and diagrams.",
            "allowed_tools": ["write_md", "create_diagram", "read_files"],
            "max_turns": 5,
            "description": "Designs architectures and system plans"
        },
        AgentType.QA_TESTER: {
            "system_prompt": "You are a quality assurance specialist. Test, validate, and verify deliverables. Identify issues, suggest improvements, and ensure quality standards are met. Provide detailed test reports.",
            "allowed_tools": ["write_md", "test_code", "read_files", "validate_output"],
            "max_turns": 5,
            "description": "Validates and tests deliverables"
        },
        AgentType.SECURITY_ANALYST: {
            "system_prompt": "You are a Security Analyst specializing in application security, vulnerability assessment, and security best practices. Your core expertise areas include threat assessment, security implementation, compliance standards, and security testing. Always provide specific, actionable security recommendations with code examples when possible.",
            "allowed_tools": ["read_files", "write_md", "scan_vulnerabilities", "analyze_code", "search_web"],
            "max_turns": 8,
            "description": "Performs security analysis and vulnerability assessment"
        },
        AgentType.DATA_SCIENTIST: {
            "system_prompt": "You are a Data Scientist specializing in data analysis, machine learning, and statistical modeling. Your core expertise areas include exploratory data analysis, statistical testing, machine learning model development, and data visualization. Always provide code examples and explain statistical concepts clearly.",
            "allowed_tools": ["read_files", "write_md", "analyze_data", "visualize_data", "search_web"],
            "max_turns": 10,
            "description": "Performs data analysis and machine learning tasks"
        },
        AgentType.API_DEVELOPER: {
            "system_prompt": "You are an API Developer specializing in RESTful API design, development, and integration. Your core expertise areas include API design principles, backend development, API documentation, and performance optimization. Always focus on creating scalable, maintainable, and well-documented APIs.",
            "allowed_tools": ["read_files", "write_md", "create_api", "test_api", "search_web"],
            "max_turns": 8,
            "description": "Designs and implements RESTful APIs and backend services"
        }
    }


class AgentManager:
    """Manages spawning and coordinating specialist agents."""

    def __init__(self, workspace_path: Path):
        """
        Initialize the agent manager.

        Args:
            workspace_path: Path to the current workspace
        """
        self.workspace_path = workspace_path
        self.active_agents: Dict[str, Dict] = {}
        self.agent_outputs_dir = workspace_path / "agent_outputs"
        self.agent_outputs_dir.mkdir(exist_ok=True)

    async def spawn_agent(
        self,
        agent_type: AgentType,
        task_description: str,
        context_files: List[str] = None,
        output_file: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn a specialist agent for a specific task.

        Args:
            agent_type: Type of agent to spawn
            task_description: Description of the task for the agent
            context_files: List of context files to provide to the agent
            output_file: Output file name for the agent's results
            custom_instructions: Additional instructions for the agent

        Returns:
            Dictionary containing agent execution results
        """
        # Get agent configuration
        config = AgentConfig.AGENT_CONFIGS[agent_type]

        # Generate agent ID
        agent_id = f"{agent_type.value}_{datetime.now().strftime('%H%M%S')}"

        # Prepare context
        context = await self._prepare_context(context_files or [])

        # Build the full prompt
        full_prompt = self._build_prompt(task_description, context, custom_instructions)

        # Configure agent options
        options = ClaudeAgentOptions(
            system_prompt=config["system_prompt"],
            allowed_tools=config["allowed_tools"],
            max_turns=config["max_turns"]
        )

        # Execute agent
        agent_result = {
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "task": task_description,
            "spawned_at": datetime.now().isoformat(),
            "status": "running"
        }

        self.active_agents[agent_id] = agent_result

        try:
            # Run the agent
            results = []
            async for message in query(prompt=full_prompt, options=options):
                for block in getattr(message, 'content', []):
                    # Check if it's a TextBlock and extract text
                    if hasattr(block, 'text'):
                        results.append(block.text)

            # Save results
            results_text = "\n".join(results)
            await self._save_agent_output(agent_id, results_text, output_file)

            # Update agent result
            agent_result.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "results": results[:5],  # Store first 5 results as preview
                "output_file": output_file,
                "num_results": len(results)
            })

            # Log to workspace
            await self._log_agent_execution(agent_result)

            return agent_result

        except Exception as e:
            agent_result.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            await self._log_agent_execution(agent_result)
            raise

    async def _prepare_context(self, context_files: List[str]) -> str:
        """
        Prepare context from provided files.

        Args:
            context_files: List of file paths to read for context

        Returns:
            Combined context text
        """
        context_parts = []

        for file_path in context_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                async with aiofiles.open(full_path, 'r') as f:
                    content = await f.read()
                    context_parts.append(f"--- Context from {file_path} ---\n{content}\n")

        return "\n".join(context_parts)

    def _build_prompt(self, task: str, context: str, custom_instructions: Optional[str]) -> str:
        """
        Build the full prompt for the agent.

        Args:
            task: Main task description
            context: Context from files
            custom_instructions: Additional instructions

        Returns:
            Complete prompt string
        """
        prompt_parts = [f"Task: {task}"]

        if context:
            prompt_parts.append(f"\nContext:\n{context}")

        if custom_instructions:
            prompt_parts.append(f"\nAdditional Instructions:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    async def _save_agent_output(self, agent_id: str, content: str, output_file: Optional[str]):
        """
        Save the agent's output to file.

        Args:
            agent_id: Unique identifier for the agent
            content: Output content from the agent
            output_file: Optional output file name
        """
        # Save to agent-specific log
        log_file = self.agent_outputs_dir / f"{agent_id}.log"
        async with aiofiles.open(log_file, 'w') as f:
            await f.write(f"Agent ID: {agent_id}\n")
            await f.write(f"Generated: {datetime.now().isoformat()}\n")
            await f.write(f"{'='*50}\n\n")
            await f.write(content)

        # Save to specified output file if provided
        if output_file:
            output_path = self.workspace_path / output_file
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(content)

    async def _log_agent_execution(self, agent_result: Dict[str, Any]):
        """
        Log agent execution to workspace history.

        Args:
            agent_result: Result of agent execution
        """
        history_path = self.workspace_path / "workflow-history.json"

        # Read existing history, create if doesn't exist
        if history_path.exists():
            async with aiofiles.open(history_path, 'r') as f:
                history = json.loads(await f.read())
        else:
            # Create initial history structure
            history = {
                "workspace_created": datetime.now().isoformat(),
                "task_name": agent_result["agent_id"],
                "steps": [],
                "agents_spawned": []
            }

        # Add agent to spawned list
        history["agents_spawned"].append({
            "agent_id": agent_result["agent_id"],
            "agent_type": agent_result["agent_type"],
            "task": agent_result["task"],
            "spawned_at": agent_result["spawned_at"],
            "status": agent_result["status"],
            "output_file": agent_result.get("output_file")
        })

        # Add as workflow step
        history["steps"].append({
            "step_type": "agent_execution",
            "agent_id": agent_result["agent_id"],
            "agent_type": agent_result["agent_type"],
            "timestamp": agent_result["spawned_at"],
            "status": agent_result["status"],
            "summary": f"Spawned {agent_result['agent_type']} agent: {agent_result['task']}"
        })

        # Write back
        async with aiofiles.open(history_path, 'w') as f:
            await f.write(json.dumps(history, indent=2))

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific agent.

        Args:
            agent_id: ID of the agent to check

        Returns:
            Agent status dictionary or None if not found
        """
        return self.active_agents.get(agent_id)

    async def list_active_agents(self) -> List[Dict[str, Any]]:
        """
        List all active agents.

        Returns:
            List of agent dictionaries
        """
        return list(self.active_agents.values())

    async def cleanup_completed_agents(self):
        """Clean up completed agents from memory."""
        completed_ids = [
            agent_id for agent_id, agent in self.active_agents.items()
            if agent["status"] in ["completed", "failed"]
        ]

        for agent_id in completed_ids:
            del self.active_agents[agent_id]