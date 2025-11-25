# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Orchestrator SDK designed for personal projects and podcast research. The system coordinates multiple specialized AI agents to automate research, content creation, and code generation workflows in isolated project environments.

## Core Architecture

The orchestrator follows a multi-agent pipeline pattern:

1. **Orchestrator Agent** (`orchestrator_agent.py`) - Main coordinator that manages the workflow pipeline and project isolation
2. **Specialized Agents** (`agents/`) - Domain-specific agents with distinct roles:
   - `researcher_agent.py` - Web research and information gathering
   - `writer_agent.py` - Content creation and script writing
   - `coder_agent.py` - Code generation and development tasks

Each agent uses the `claude-agent-sdk` with configured `ClaudeAgentOptions` for system prompts, tool access, and turn limits.

## Development Commands

### Running the System
```bash
# Main orchestrator execution - primary command
python orchestrator_agent.py <project-folder> "<task/topic description>"

# Example usage
python orchestrator_agent.py 2025-11-24-ai-podcast-news "Research new AI trends for this week's podcast"
```

### Environment Setup
```bash
# Install required dependencies
pip install -r requirements.txt

# Required packages: claude-agent-sdk, aiofiles
```

### Testing and Debugging

#### El Jefe Dashboard Testing Suite

The El Jefe monitoring dashboard has a comprehensive web application testing suite installed and configured:

**Quick Validation:**
```bash
# Run basic setup validation
pytest tests/test_basic.py -v
```

**Full Test Suite:**
```bash
# Run all dashboard tests (requires dashboard running on localhost:8080)
python3 tests/run_tests.py --test-type all
```

**Individual Test Types:**
```bash
# Unit tests only
python3 tests/run_tests.py --test-type unit

# End-to-end browser tests
python3 tests/run_tests.py --test-type e2e

# Performance and load testing
python3 tests/run_tests.py --test-type performance

# Security validation tests
python3 tests/run_tests.py --test-type security
```

**Load Testing with Locust:**
```bash
# Performance testing with 20 concurrent users for 60 seconds
locust -f tests/locustfile.py --headless --users 20 --run-time 60s --host http://localhost:8080

# Interactive web interface for load testing
locust -f tests/locustfile.py --host http://localhost:8080
# Visit http://localhost:8089 for web interface
```

**Cross-Browser Testing:**
```bash
# Run E2E tests on specific browsers
pytest tests/test_end_to_end.py --browser chromium
pytest tests/test_end_to_end.py --browser firefox
pytest tests/test_end_to_end.py --browser webkit
```

**Dashboard Requirements:**
- Dashboard must be running on http://localhost:8080
- Authentication: eljefe_admin (configured automatically)
- Dependencies: pytest, playwright, locust (all installed)

**Test Coverage:**
- API endpoints and authentication
- Workflow assignment and execution
- Chat interface and file uploads
- Cross-browser compatibility
- Mobile responsive design
- Performance and load testing
- Security validation (XSS, SQL injection)
- Accessibility compliance (WCAG 2.1 AA)

#### Agent Testing
Test individual orchestrator agents:
```python
# Import and test individual agent functions
from agents.researcher_agent import run_researcher_agent
from agents.writer_agent import run_writer_agent
from agents.coder_agent import run_coder_agent

# Each agent follows the pattern: run_<agent>_agent(inputs..., output_path, context_path)
```

## Project Structure

The system creates isolated project environments under `projects/` with this structure:
- `context-main.md` - Main project context and background information
- `workflow-history.json` - Workflow execution log with step results
- `research_notes.md` - Research agent outputs and findings
- `draft_article.md` - Writer agent outputs and content drafts
- `agent_outputs/` - Individual agent logs and output files

## Agent Configuration

### Researcher Agent
- **Purpose**: Web research and information synthesis
- **Tools**: `search_web`, `write_md`
- **Max Turns**: 8
- **Output**: Structured research notes in bullet points

### Writer Agent
- **Purpose**: Content creation and script writing
- **Tools**: `write_md`
- **Max Turns**: 6
- **Input**: Research notes from researcher agent
- **Output**: Conversational, informative podcast scripts

### Coder Agent
- **Purpose**: Code generation and development tasks
- **Tools**: `write_md`
- **Max Turns**: 5
- **Input**: Content from writer agent
- **Output**: Python code snippets and utilities

## Workflow Pipeline Architecture

The orchestrator executes agents sequentially with data flow between stages:

1. **Research Stage**: `researcher_agent.py` scrapes web content and outputs structured notes to `research_notes.md`
2. **Writing Stage**: `writer_agent.py` reads research notes and generates content to `draft_article.md`
3. **Optional Code Stage**: `coder_agent.py` (commented out by default) can generate code based on written content

Each stage passes context through shared files and maintains workflow state in `workflow-history.json`.

## Key Implementation Details

- **Async Pipeline**: All agents use async/await with `aiofiles` for non-blocking file operations
- **SDK Integration**: Uses `claude-agent-sdk` with `ClaudeAgentOptions` for tool authorization and turn limits
- **Message Processing**: Extracts text content from SDK messages: `getattr(message, 'content', [])`
- **Project Sandboxing**: Each project gets isolated directory under `projects/` with all agent outputs
- **State Persistence**: Workflow progress logged to JSON with step results and timestamps

## Adding New Agents

New agents must follow the established pattern:

```python
async def run_<agent>_agent(input_paths..., output_path, context_path):
    # Read inputs from input_paths
    # Configure ClaudeAgentOptions with system_prompt and allowed_tools
    # Process with claude_agent_sdk.query()
    # Write results to output_path
    # Return results list
```

Add the agent call to `orchestrator_agent.py` and log the step in the history array.