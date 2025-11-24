# Setup Guide for AI Orchestrator SDK

This guide will help you set up and configure the AI Orchestrator SDK for use in your projects.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Keys Setup](#api-keys-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 1GB free disk space

### Recommended Requirements
- **Python**: 3.10 or higher
- **Memory**: 16GB+ RAM
- **Storage**: 10GB+ free disk space (for workspaces)
- **Network**: Stable internet connection for API calls

### Optional Dependencies
- **GPU**: Not required but can speed up certain operations
- **Additional Python packages**: For specific use cases (see below)

## Installation

### Step 1: Clone or Download

```bash
# Option 1: Clone the repository
git clone https://github.com/your-org/ai-orchestrator-sdk.git
cd ai-orchestrator-sdk

# Option 2: Download and extract
# Download from https://github.com/your-org/ai-orchestrator-sdk/releases
# Extract the ZIP file
# cd ai-orchestrator-sdk
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv ai-orchestrator-env

# Activate on Windows
ai-orchestrator-env\Scripts\activate

# Activate on macOS/Linux
source ai-orchestrator-env/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For development mode (includes additional tools)
pip install -e ".[dev]"
```

### Step 4: Verify Installation

```bash
# Check if the SDK is properly installed
python -c "from src.orchestrator import Orchestrator; print('✅ Installation successful!')"
```

## Configuration

### Step 1: Create Configuration File

The SDK looks for configuration in `config/orchestrator.json`. Create this file:

```bash
mkdir -p config
```

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
    "enable_logging": true,
    "log_level": "INFO"
  },
  "security": {
    "allow_external_apis": true,
    "restrict_file_access": true,
    "allowed_file_extensions": [
      ".md", ".txt", ".json", ".csv", ".py", ".js",
      ".html", ".css", ".yaml", ".yml", ".xml"
    ],
    "sandbox_mode": false
  }
}
```

### Step 2: Set Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Claude API Key
CLAUDE_API_KEY=your_claude_api_key_here

# Optional: Custom workspace directory
ORCHESTRATOR_WORKSPACE__BASE_DIR=my-workspaces

# Optional: Agent settings
ORCHESTRATOR_AGENT__DEFAULT_MAX_TURNS=8
ORCHESTRATOR_AGENT__ENABLE_LOGGING=true

# Optional: Security settings
ORCHESTRATOR_SECURITY__SANDBOX_MODE=false
ORCHESTRATOR_SECURITY__RESTRICT_FILE_ACCESS=true
```

### Step 3: Load Environment Variables

```bash
# Option 1: Use python-dotenv
pip install python-dotenv

# Add to your Python script:
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

# Option 2: Source the file (Linux/macOS)
source .env

# Option 3: Set manually (Windows)
set CLAUDE_API_KEY=your_api_key_here
```

## API Keys Setup

### Step 1: Get Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key securely

### Step 2: Configure API Key

```bash
# Option 1: Environment variable (recommended)
export CLAUDE_API_KEY="sk-ant-api03-..."

# Option 2: .env file
echo "CLAUDE_API_KEY=sk-ant-api03-..." >> .env

# Option 3: In code (not recommended for production)
import os
os.environ['CLAUDE_API_KEY'] = 'your-api-key'
```

### Step 3: Verify API Access

```python
# Test script to verify API access
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def test_api():
    try:
        options = ClaudeAgentOptions(
            system_prompt="You are a helpful assistant.",
            max_turns=1
        )
        async for message in query("Hello, can you respond with 'API works!'?", options=options):
            print("✅ API key is valid and working")
            return True
    except Exception as e:
        print(f"❌ API key error: {e}")
        return False

asyncio.run(test_api())
```

## Verification

### Step 1: Run Basic Test

```bash
# Test the CLI
python main.py --help

# Test workspace creation
python -c "
import asyncio
from src.workspace_manager import WorkspaceManager

async def test():
    wm = WorkspaceManager('test-workspaces')
    info = await wm.create_workspace('test', 'Test workspace')
    print(f'✅ Workspace created: {info[\"path\"]}')

asyncio.run(test())
"
```

### Step 2: Run Example

```bash
# Run a simple example
python examples/podcast_research.py

# Or use the CLI directly
python main.py "Write a hello world Python script"
```

### Step 3: Check Output

After running an example, you should see:

```
workspaces/
└── week-XX/
    └── YYYY-MM-DD/
        └── task-name-HHMMSS/
            ├── context-main.md
            ├── workflow-history.json
            ├── agent_outputs/
            └── [generated files]
```

## Troubleshooting

### Common Issues

#### 1. ImportError: No module named 'src'

```bash
# Solution: Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or run with:
python -m src.orchestrator
```

#### 2. API Key Not Found

```bash
# Check environment variable
echo $CLAUDE_API_KEY

# Check .env file
cat .env | grep CLAUDE_API_KEY

# Set it manually
export CLAUDE_API_KEY="your-key-here"
```

#### 3. Permission Denied

```bash
# Check directory permissions
ls -la workspaces/

# Fix permissions
chmod 755 workspaces/
chmod -R 644 workspaces/*
```

#### 4. Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.9+
```

#### 5. Timeouts or Slow Performance

```json
// In config/orchestrator.json
{
  "agent": {
    "default_timeout": 600,  // Increase timeout
    "default_max_turns": 4   // Reduce turns
  }
}
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use environment variable
export ORCHESTRATOR_AGENT__LOG_LEVEL=DEBUG
```

### Getting Help

1. Check the [FAQ](docs/FAQ.md)
2. Review [troubleshooting guide](docs/troubleshooting.md)
3. Search [GitHub Issues](https://github.com/your-org/ai-orchestrator-sdk/issues)
4. Join our [Discord community](https://discord.gg/ai-orchestrator)

## Next Steps

### 1. Run the Examples

```bash
# Podcast research example
python examples/podcast_research.py

# Data analysis example
python examples/data_analysis.py
```

### 2. Create Your First Workflow

```python
from src.orchestrator import Orchestrator

async def main():
    orchestrator = Orchestrator()
    result = await orchestrator.execute_goal(
        "Your task here"
    )
    print(f"Results: {result}")

asyncio.run(main())
```

### 3. Explore Documentation

- [API Reference](docs/README.md)
- [Agent Development Guide](docs/agent-development.md)
- [Best Practices](docs/best-practices.md)

### 4. Join the Community

- Discord: [AI Orchestrator Community](https://discord.gg/ai-orchestrator)
- Forum: [GitHub Discussions](https://github.com/your-org/ai-orchestrator-sdk/discussions)
- Twitter: [@AIOrchestrator](https://twitter.com/AIOrchestrator)

### 5. Customize for Your Use Case

- Add custom agents (see [agent development guide](docs/agent-development.md))
- Create custom tools (see [tools guide](docs/custom-tools.md))
- Configure workflows (see [workflows guide](docs/workflows.md))

---

## Quick Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Claude API key obtained
- [ ] API key configured (`export CLAUDE_API_KEY=...`)
- [ ] Configuration file created (`config/orchestrator.json`)
- [ ] Basic test passed
- [ ] Example script run successfully

If you've completed all these steps, you're ready to use the AI Orchestrator SDK! 🎉