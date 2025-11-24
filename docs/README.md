# AI Orchestrator SDK Documentation

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Core Components](#core-components)
5. [Agent Types](#agent-types)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

The AI Orchestrator SDK is a comprehensive Python framework for coordinating multiple specialized AI agents to automate complex tasks. It breaks down high-level goals into manageable steps, spawns appropriate specialist agents for each step, and manages the complete workflow in organized, isolated workspaces.

### Key Features

- **Multi-Agent Coordination**: Seamlessly orchestrate different specialist agents
- **Intelligent Task Planning**: Automatically break down goals into logical steps
- **Workspace Isolation**: Each task runs in its own organized workspace
- **Human-in-the-Loop**: Optional user approval at critical steps
- **Comprehensive Logging**: Complete workflow history and tracking
- **Extensible Architecture**: Easy to add new agent types and tools
- **Production Ready**: Robust error handling and async support

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/ai-orchestrator-sdk.git
cd ai-orchestrator-sdk

# Install dependencies
pip install -r requirements.txt

# Install the SDK
pip install -e .
```

### Basic Usage

```python
from src.orchestrator import Orchestrator

# Create orchestrator instance
orchestrator = Orchestrator(interactive=True)

# Execute a goal
result = await orchestrator.execute_goal(
    "Research AI trends for my podcast"
)

# Check results
print(f"Results saved to: {result['workspace']}")
```

### Command Line Interface

```bash
# Execute a goal
python main.py "Build a Python script to analyze sales data"

# List recent workspaces
python main.py --list

# Resume a workspace
python main.py --resume workspaces/week-47/2024-11-23/my-task

# Non-interactive mode
python main.py --non-interactive "Write documentation for API"
```

## Architecture

The AI Orchestrator follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Main Orchestrator                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  Workspace Mgr  │  │      Task Planner            │  │
│  │                 │  │                             │  │
│  │ - Create Folders│  │ - Analyze Goals             │  │
│  │ - Manage Files  │  │ - Plan Workflows            │  │
│  │ - Track Context │  │ - Select Agents             │  │
│  └─────────────────┘  └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  Agent Manager  │  │     User Interface          │  │
│  │                 │  │                             │  │
│  │ - Spawn Agents  │  │ - Get Approvals             │  │
│  │ - Track Status  │  │ - Show Progress             │  │
│  │ - Collect Results│ │ - Display Summaries         │  │
│  └─────────────────┘  └─────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                     Specialist Agents                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ Researcher  │ │    Coder    │ │     Writer      │   │
│  │             │ │             │ │                 │   │
│  │ - Web Search│ │ - Generate  │ │ - Create Content│   │
│  │ - Synthesize│ │   Code      │ │ - Edit Text     │   │
│  │ - Find Facts │ │ - Test Code │ │ - Format Docs  │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │   Analyst   │ │   Designer  │ │   QA Tester     │   │
│  │             │ │             │ │                 │   │
│  │ - Analyze   │ │ - Architecture│ │ - Validate     │   │
│  │   Data      │ │ - Plan Systems│ │   Outputs      │   │
│  │ - Find      │ │ - Create    │ │ - Test Quality  │   │
│  │   Trends    │ │   Blueprints│ │ - Report Issues │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Orchestrator

The main coordinator that manages the entire workflow:

```python
from src.orchestrator import Orchestrator

orchestrator = Orchestrator(
    base_dir="workspaces",
    interactive=True  # Prompt for user approval
)

# Execute a complete goal
result = await orchestrator.execute_goal("Your goal here")
```

### 2. Workspace Manager

Handles workspace creation and file management:

```python
from src.workspace_manager import WorkspaceManager

workspace_manager = WorkspaceManager()

# Create a new workspace
workspace_info = await workspace_manager.create_workspace(
    task_name="my-task",
    task_description="Description of the task"
)

# Update workspace context
await workspace_manager.update_context(
    workspace_path,
    "Progress Summary",
    "Completed initial research phase"
)
```

### 3. Task Planner

Analyzes goals and creates execution plans:

```python
from src.task_planner import TaskPlanner

planner = TaskPlanner()

# Create a task plan
task_plan = await planner.create_task_plan(
    "Build a web scraper for news articles"
)

# View the planned steps
for step in task_plan["steps"]:
    print(f"- {step['description']} (Agent: {step['agent_type']})")
```

### 4. Agent Manager

Spawns and coordinates specialist agents:

```python
from src.agent_manager import AgentManager, AgentType

agent_manager = AgentManager(workspace_path)

# Spawn a researcher agent
result = await agent_manager.spawn_agent(
    agent_type=AgentType.RESEARCHER,
    task_description="Research Python web scraping libraries",
    output_file="research_notes.md"
)
```

## Agent Types

### Researcher Agent
- **Purpose**: Gather and synthesize information from various sources
- **Tools**: Web search, file reading, markdown writing
- **Use Cases**: Market research, fact-finding, competitive analysis
- **Max Turns**: 8

### Coder Agent
- **Purpose**: Generate and write code
- **Tools**: File operations, code generation, testing
- **Use Cases**: Script development, API implementation, utilities
- **Max Turns**: 6

### Writer Agent
- **Purpose**: Create and edit content
- **Tools**: Markdown writing, editing, formatting
- **Use Cases**: Documentation, articles, scripts, reports
- **Max Turns**: 6

### Analyst Agent
- **Purpose**: Analyze data and identify patterns
- **Tools**: Data analysis, statistics, trend identification
- **Use Cases**: Data insights, trend analysis, metrics
- **Max Turns**: 7

### Designer Agent
- **Purpose**: Design architectures and systems
- **Tools**: Diagramming, planning, architecture design
- **Use Cases**: System design, architecture planning, workflow design
- **Max Turns**: 5

### QA Tester Agent
- **Purpose**: Validate and test deliverables
- **Tools**: Testing, validation, quality assurance
- **Use Cases**: Code testing, document review, validation
- **Max Turns**: 5

## Usage Examples

### Example 1: Research Task

```python
# Research AI trends for a podcast
result = await orchestrator.execute_goal(
    "Research the latest AI trends for this week's tech podcast"
)

# Output structure:
# workspaces/week-47/2024-11-23/ai-trends-143022/
# ├── context-main.md          # Main context and progress
# ├── workflow-history.json    # Detailed execution log
# ├── research_notes.md        # Researcher agent output
# ├── research_synthesis.md    # Analyst agent output
# └── research_summary.md      # Final summary
```

### Example 2: Development Task

```python
# Build a data analysis script
result = await orchestrator.execute_goal(
    "Create a Python script to analyze CSV sales data and generate charts"
)

# Workflow:
# 1. Designer agent: Creates architecture plan
# 2. Coder agent: Implements the script
# 3. QA Tester agent: Tests and validates
```

### Example 3: Content Creation

```python
# Write blog post
result = await orchestrator.execute_goal(
    "Write a blog post about remote work best practices"
)

# Workflow:
# 1. Researcher agent: Gathers information
# 2. Writer agent: Creates first draft
# 3. QA Tester agent: Reviews and edits
```

### Example 4: Custom Workflow

```python
from src.orchestrator import Orchestrator
from src.agent_manager import AgentType

# Create custom workflow
orchestrator = Orchestrator()

# Create workspace manually
workspace_info = await orchestrator.workspace_manager.create_workspace(
    "custom-analysis",
    "Multi-step data analysis project"
)

# Execute custom steps
step1 = await orchestrator.agent_manager.spawn_agent(
    agent_type=AgentType.RESEARCHER,
    task="Research data analysis best practices",
    output_file="best_practices.md"
)

step2 = await orchestrator.agent_manager.spawn_agent(
    agent_type=AgentType.CODER,
    task="Create data analysis script",
    context_files=["best_practices.md"],
    output_file="analysis_script.py"
)
```

## Configuration

The SDK can be configured through:

### 1. Configuration File

Create `config/orchestrator.json`:

```json
{
  "workspace": {
    "base_dir": "workspaces",
    "max_workspace_age_days": 30,
    "auto_cleanup": false
  },
  "agent": {
    "default_max_turns": 6,
    "default_timeout": 300,
    "cost_tracking": true,
    "enable_logging": true
  },
  "security": {
    "allow_external_apis": true,
    "restrict_file_access": true,
    "sandbox_mode": false
  }
}
```

### 2. Environment Variables

```bash
export ORCHESTRATOR_WORKSPACE__BASE_DIR="my-workspaces"
export ORCHESTRATOR_AGENT__DEFAULT_MAX_TURNS="10"
export ORCHESTRATOR_SECURITY__SANDBOX_MODE="true"
```

### 3. Code Configuration

```python
from src.config import get_config, reload_config

# Get current config
config = get_config()
print(f"Workspace dir: {config.workspace.base_dir}")

# Reload config from file
reload_config()
```

## API Reference

### Orchestrator Class

```python
class Orchestrator:
    def __init__(self, base_dir: str = "workspaces", interactive: bool = True)

    async def execute_goal(self, goal: str) -> Dict[str, Any]
    async def list_workspaces(self, limit: int = 10) -> List[Dict]
    async def resume_workspace(self, workspace_path: str) -> bool
    async def cleanup_old_workspaces(self, days: int = 30)
```

### WorkspaceManager Class

```python
class WorkspaceManager:
    def __init__(self, base_dir: str = "workspaces")

    async def create_workspace(self, task_name: str, task_description: str) -> Dict
    async def log_workflow_step(self, workspace_path: Path, step: Dict)
    async def update_context(self, workspace_path: Path, section: str, content: str)
    async def get_workspace_summary(self, workspace_path: Path) -> Dict
    async def list_workspaces(self, limit: int = 10) -> List[Dict]
```

### AgentManager Class

```python
class AgentManager:
    def __init__(self, workspace_path: Path)

    async def spawn_agent(
        self,
        agent_type: AgentType,
        task_description: str,
        context_files: List[str] = None,
        output_file: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]

    async def get_agent_status(self, agent_id: str) -> Optional[Dict]
    async def list_active_agents(self) -> List[Dict]
```

## Best Practices

### 1. Goal Definition
- Be specific about what you want to accomplish
- Include context about the target audience or use case
- Mention any specific requirements or constraints

### 2. Workspace Management
- Use descriptive task names for easy identification
- Regularly clean up old workspaces
- Review workflow history to understand agent decisions

### 3. Agent Coordination
- Let the task planner automatically select agents
- Provide context files when agents depend on previous work
- Use custom instructions for specific requirements

### 4. Performance Optimization
- Limit the number of parallel agents to control costs
- Use the non-interactive mode for automated workflows
- Monitor agent turn counts to avoid unnecessary iterations

### 5. Security
- Enable sandbox mode for untrusted tasks
- Restrict file access to workspaces only
- Review agent outputs before using in production

## Troubleshooting

### Common Issues

1. **Agent Execution Fails**
   - Check if the Claude Agent SDK is properly installed
   - Verify API credentials are configured
   - Review error messages in workflow-history.json

2. **Workspace Creation Errors**
   - Ensure workspace directory has write permissions
   - Check available disk space
   - Verify the base directory exists

3. **Context Not Updated**
   - Check if context files are being written correctly
   - Verify file permissions in the workspace
   - Review the workflow log for errors

4. **Agent Not Responding**
   - Check network connectivity for web searches
   - Verify timeout settings
   - Try reducing max_turns for complex tasks

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use verbose flag
orchestrator = Orchestrator(verbose=True)
```

### Getting Help

- Check the [Examples](../examples/) directory for sample code
- Review test cases for usage patterns
- Open an issue on GitHub for bugs or questions

## Advanced Topics

### Custom Agent Types

Add new agent types by extending the agent configuration:

```python
from src.agent_manager import AgentConfig, AgentType

# Add custom agent type
AgentConfig.AGENT_CONFIGS[AgentType.CUSTOM] = {
    "system_prompt": "You are a specialist in...",
    "allowed_tools": ["custom_tool"],
    "max_turns": 5,
    "description": "Custom agent for specific tasks"
}
```

### Custom Tools

Create custom tools for agents:

```python
from src.tools import BaseTool

class CustomTool(BaseTool):
    async def execute(self, *args, **kwargs):
        # Implement custom functionality
        pass
```

### Workflow Templates

Create reusable workflow templates:

```python
WORKFLOW_TEMPLATES = {
    "podcast_episode": [
        {"agent": "researcher", "task": "Research topic"},
        {"agent": "writer", "task": "Write script"},
        {"agent": "coder", "task": "Create show notes"}
    ]
}
```

---

For more detailed information, check the individual module documentation and examples.