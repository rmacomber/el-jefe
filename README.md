# AI Orchestrator SDK

A comprehensive Python framework for orchestrating multiple specialized AI agents to automate complex tasks. Break down goals, spawn specialist agents, and organize all work in clean, date-based folders for personal research, content creation, and development.

## 🚀 Features

- **Multi-Agent Coordination**: Seamlessly coordinate 6 specialized agent types
- **Intelligent Task Planning**: Automatically breaks down goals into logical workflow steps
- **Workspace Isolation**: Each task runs in its own organized workspace with proper file isolation
- **Human-in-the-Loop**: Optional user approvals at critical steps
- **Comprehensive Logging**: Complete workflow history with detailed execution tracking
- **Production Ready**: Robust async support, error handling, and configuration management
- **Extensible**: Easy to add new agent types and custom tools

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    AI Orchestrator                       │
│                                                         │
│  Breaks down goals → Plans workflow → Spawns agents     │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │  Workspace Mgr  │  │      Task Planner            │   │
│  │                 │  │                             │   │
│  │ • Date-based    │  │ • Analyze goals             │   │
│  │   folders       │  │ • Select agents             │   │
│  │ • Context mgmt  │  │ • Plan steps                │   │
│  └─────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   Specialist Agents                      │
│                                                         │
│  🔬 Researcher  │  💻 Coder  │  ✍️ Writer  │  📊 Analyst │
│                 │            │            │            │
│  • Web search   │  • Code    │  • Content  │  • Data    │
│  • Synthesize   │    gen     │  • Docs     │    analysis│
│  • Fact-find    │  • Testing │  • Editing  │  • Trends  │
│                 │            │            │            │
│  🏗️ Designer   │  🔍 QA Tester                        │
│                 │                                      │
│  • Architecture │  • Validation                        │
│  • Systems plan │  • Quality check                     │
│  • Blueprints   │  • Testing                           │
└─────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- Claude Agent SDK (requires API key)
- asyncio compatible environment

### Quick Install

```bash
# Clone the repository
git clone https://github.com/your-org/ai-orchestrator-sdk.git
cd ai-orchestrator-sdk

# Install dependencies
pip install -r requirements.txt

# Install the SDK in development mode
pip install -e .
```

### Dependencies

```bash
# Core dependencies
pip install claude-agent-sdk aiofiles

# Optional dependencies for enhanced functionality
pip install pandas matplotlib seaborn  # For data analysis
pip install requests beautifulsoup4   # For enhanced web scraping
pip install jinja2                     # For template rendering
```

## 🎯 Quick Start

### Command Line Usage

```bash
# Basic goal execution
python main.py "Research AI trends for my podcast"

# Development task
python main.py "Build a Python script to analyze sales data"

# Writing task
python main.py "Write documentation for my REST API"

# List recent workspaces
python main.py --list

# Non-interactive mode (no prompts)
python main.py --non-interactive "Generate weekly report"

# Resume an existing workspace
python main.py --resume workspaces/week-47/2024-11-23/my-task

# Clean up old workspaces
python main.py --cleanup 30
```

### Python API Usage

```python
from src.orchestrator import Orchestrator

# Create orchestrator instance
orchestrator = Orchestrator(
    base_dir="workspaces",  # Base directory for workspaces
    interactive=True        # Prompt for user approvals
)

# Execute a goal
result = await orchestrator.execute_goal(
    "Create a data analysis dashboard for sales metrics"
)

# Check results
print(f"✅ Completed {len(result['results'])} steps")
print(f"📁 Workspace: {result['workspace']}")
print(f"📊 Success rate: {result['summary']['success_rate']}")
```

## 📁 Workspace Structure

Each task creates an organized workspace:

```text
workspaces/
└── week-47/
    └── 2024-11-23/
        └── analyze-sales-data-143022/
            ├── context-main.md          # Main context and progress
            ├── workflow-history.json    # Detailed execution log
            ├── workflow-state.json      # Current workflow state
            ├── workspace-info.json      # Workspace metadata
            ├── execution-summary.md     # Final results summary
            ├── agent_outputs/           # Individual agent logs
            │   ├── researcher_143025.log
            │   ├── coder_143042.log
            │   └── analyst_143058.log
            ├── research_notes.md        # Research findings
            ├── architecture_design.md   # System architecture
            ├── implementation.md        # Generated code
            └── analysis_report.md       # Final analysis
```

## 🤖 Agent Types

### Researcher Agent

- **Purpose**: Gather and synthesize information
- **Tools**: Web search, file reading, markdown writing
- **Use Cases**: Market research, fact-finding, trend analysis
- **Max Turns**: 8

```python
# Spawn researcher directly
from src.agent_manager import AgentManager, AgentType

agent_manager = AgentManager(workspace_path)
result = await agent_manager.spawn_agent(
    agent_type=AgentType.RESEARCHER,
    task="Research Python web scraping libraries",
    output_file="scraping_research.md"
)
```

### Coder Agent

- **Purpose**: Generate and implement code
- **Tools**: File operations, code generation, testing
- **Use Cases**: Scripts, APIs, utilities, automation
- **Max Turns**: 6

### Writer Agent

- **Purpose**: Create and polish content
- **Tools**: Markdown writing, editing, formatting
- **Use Cases**: Documentation, articles, scripts, reports
- **Max Turns**: 6

### Analyst Agent

- **Purpose**: Analyze data and identify patterns
- **Tools**: Data analysis, statistics, trend identification
- **Use Cases**: Business insights, data trends, metrics
- **Max Turns**: 7

### Designer Agent

- **Purpose**: Design architectures and systems
- **Tools**: Architecture planning, system design
- **Use Cases**: System architecture, workflow design
- **Max Turns**: 5

### QA Tester Agent

- **Purpose**: Validate and test deliverables
- **Tools**: Testing, validation, quality assurance
- **Use Cases**: Code testing, document review
- **Max Turns**: 5

## 🔧 Configuration

### Environment Configuration

Set up your environment:

```bash
# Required: Claude API Key
export CLAUDE_API_KEY="your-api-key-here"

# Optional: Custom workspace directory
export ORCHESTRATOR_WORKSPACE__BASE_DIR="my-workspaces"

# Optional: Default agent settings
export ORCHESTRATOR_AGENT__DEFAULT_MAX_TURNS="10"
export ORCHESTRATOR_AGENT__ENABLE_LOGGING="true"

# Optional: Security settings
export ORCHESTRATOR_SECURITY__SANDBOX_MODE="true"
export ORCHESTRATOR_SECURITY__RESTRICT_FILE_ACCESS="true"
```

### Configuration File

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
    "allowed_file_extensions": [
      ".md", ".txt", ".json", ".csv", ".py", ".js",
      ".html", ".css", ".yaml", ".yml"
    ],
    "sandbox_mode": false
  }
}
```

## 📚 Examples

### Example 1: Podcast Research

```python
# Research AI trends for podcast
result = await orchestrator.execute_goal(
    "Research the latest AI developments for this week's tech podcast"
)

# Output files created:
# - research_notes.md      # Initial research findings
# - research_synthesis.md  # Analyzed and synthesized data
# - podcast_script.md      # Draft podcast episode
# - show_notes.md         # Supporting materials
```

### Example 2: Data Analysis Project

```python
# Build complete data analysis solution
result = await orchestrator.execute_goal(
    "Create a Python dashboard to analyze monthly sales data with charts"
)

# Workflow executed:
# 1. Designer: Plans dashboard architecture
# 2. Researcher: Finds best visualization libraries
# 3. Coder: Implements dashboard script
# 4. QA Tester: Validates and tests
```

### Example 3: Documentation Project

```python
# Generate comprehensive API docs
result = await orchestrator.execute_goal(
    "Write complete documentation for my REST API including examples"
)

# Custom workflow with specific instructions:
await orchestrator.agent_manager.spawn_agent(
    agent_type=AgentType.RESEARCHER,
    task="Analyze the API endpoints and understand functionality",
    custom_instructions="Focus on user perspective and use cases"
)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_orchestrator.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

- ✅ Workspace Management
- ✅ Agent Spawning and Coordination
- ✅ Task Planning
- ✅ File Operations
- ✅ Configuration Loading
- ✅ Error Handling

## 🔒 Security

The SDK includes several security features:

1. **Workspace Isolation**: Agents can only access files within their workspace
2. **File Type Restrictions**: Configurable allowed file extensions
3. **Sandbox Mode**: Optional restricted execution environment
4. **No Code Execution**: Agents generate code but don't execute it directly
5. **User Approvals**: Optional prompts before critical operations

## 📈 Performance Tips

1. **Control Costs**: Limit agent turns and parallel executions
2. **Reuse Workspaces**: Resume existing workspaces when possible
3. **Batch Operations**: Group related tasks in single goals
4. **Monitor Logs**: Check workflow-history.json for inefficiencies
5. **Clean Up**: Regularly remove old workspaces

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and install
git clone https://github.com/your-org/ai-orchestrator-sdk.git
cd ai-orchestrator-sdk
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run linting
flake8 src/
black src/
```

## 📖 Documentation

- [Full API Documentation](docs/README.md)
- [Architecture Guide](docs/architecture.md)
- [Agent Development Guide](docs/agent-development.md)
- [Examples and Tutorials](examples/)

## 🐛 Troubleshooting

### Common Issues

1. **"Agent failed to spawn"**
   - Check API key configuration
   - Verify network connectivity
   - Review agent permissions

2. **"Workspace creation failed"**
   - Check directory permissions
   - Verify disk space
   - Check base directory exists

3. **"Context not updating"**
   - Check file write permissions
   - Verify workspace integrity
   - Review workflow history for errors

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use CLI flag
python main.py --verbose "Your task here"
```

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Claude Agent SDK for agent management
- OpenAI for powerful language models
- The Python async community for excellent async support

## 📞 Support

- 📧 Email: support@ai-orchestrator.com
- 💬 Discord: [Join our community](https://discord.gg/ai-orchestrator)
- 📖 Docs: [Full documentation](https://docs.ai-orchestrator.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/ai-orchestrator-sdk/issues)

---

### Built with ❤️ for the AI community