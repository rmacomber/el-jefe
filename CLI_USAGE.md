# 🚀 AI Orchestrator CLI Usage Guide

## 📦 Installation

### Option 1: Use the Install Script (Recommended)
```bash
./install-local.sh
```

### Option 2: Manual Installation
Add this to your shell profile (`~/.zshrc`, `~/.bash_profile`):
```bash
export PATH="/Users/ryanmacomber/Documents/Orchestrator-Agent:$PATH"
```

Then restart your terminal or run:
```bash
source ~/.zshrc  # or ~/.bash_profile
```

## 🎯 Available Command

### **AI Orchestrator CLI**
```bash
el-jefe "Your goal here"
```

## 💡 Basic Usage Examples

### Research Tasks
```bash
el-jefe "Research AI trends for my podcast"
el-jefe "Find the best Python web frameworks for 2024"
el-jefe "Investigate sustainable technology innovations"
```

### Development Tasks
```bash
el-jefe "Build a Python script to analyze CSV data"
el-jefe "Create a REST API for user management"
el-jefe "Design a database schema for an e-commerce app"
```

### Content Creation
```bash
el-jefe "Write a blog post about microservices architecture"
el-jefe "Create documentation for my API"
el-jefe "Generate a tutorial on Docker basics"
```

### Data Analysis
```bash
el-jefe "Analyze monthly sales data and provide insights"
el-jefe "Create a dashboard for tracking user engagement"
el-jefe "Find trends in customer support tickets"
```

## 🔧 Command Options

el-jefe supports these options:

```bash
# Show help
el-jefe --help

# List recent workspaces
el-jefe --list

# Run without prompts (non-interactive)
el-jefe --non-interactive "Your task"

# Clean up old workspaces (older than 30 days)
el-jefe --cleanup 30

# Resume working on a previous project
el-jefe --resume workspaces/week-47/2025-11-23/your-task

# Use custom workspace directory
el-jefe --workspace-dir ~/my-projects "Your task"

# Show verbose output
el-jefe --verbose "Your task"
```

## 📁 Workspace Management

### View Your Projects
```bash
el-jefe --list
```

### Resume Previous Work
```bash
# Get the workspace path from --list
el-jefe --resume workspaces/week-47/2025-11-23/your-project-123456
```

### Clean Up Old Projects
```bash
# Remove projects older than 30 days
el-jefe --cleanup 30

# Remove projects older than 7 days
el-jefe --cleanup 7
```

## 🏗️ What Happens When You Run a Command?

When you run `el-jefe "Your goal"`, the system:

1. **Creates a Workspace** - Organized by week/date/timestamp
2. **Plans the Workflow** - Breaks your goal into logical steps
3. **Spawns Specialist Agents** - Researcher, Writer, Coder, Analyst, Designer, or QA Tester
4. **Executes Sequentially** - Each agent builds on previous work
5. **Saves Results** - All outputs saved in organized files

### Example Workspace Structure
```
workspaces/
└── week-47/
    └── 2025-11-23/
        └── your-goal-143022/
            ├── context-main.md          # Main progress tracking
            ├── workflow-history.json    # Detailed execution log
            ├── agent_outputs/           # Individual agent results
            ├── research_notes.md        # Research findings
            ├── draft.md                # Content drafts
            └── final_content.md        # Final output
```

## 🎭 Agent Types

The system automatically selects the right agents for your task:

- **🔬 Researcher** - Web research, fact-finding, trend analysis
- **💻 Coder** - Code generation, scripts, development tasks
- **✍️ Writer** - Content creation, documentation, articles
- **📊 Analyst** - Data analysis, insights, pattern identification
- **🏗️ Designer** - Architecture planning, system design
- **🔍 QA Tester** - Quality assurance, validation, testing

## 💼 Real-World Use Cases

### **For Content Creators**
```bash
el-jefe "Research trending topics for next week's tech podcast"
el-jefe "Write a script about the future of remote work"
el-jefe "Create show notes for my AI episode"
```

### **For Developers**
```bash
el-jefe "Build a Python API for todo management"
el-jefe "Write unit tests for my user authentication system"
el-jefe "Create a deployment script for my Flask app"
```

### **For Researchers**
```bash
el-jefe "Analyze recent papers on quantum computing"
el-jefe "Compare different machine learning frameworks"
el-jefe "Summarize key findings from climate change reports"
```

### **For Business Users**
```bash
el-jefe "Analyze customer feedback and identify key themes"
el-jefe "Create a presentation on quarterly sales performance"
el-jefe "Research competitor pricing strategies"
```

## 🔒 Working with API Keys

The system uses your existing `.env` file:
```bash
# Already configured in your project
ANTHROPIC_API_KEY=your-api-key
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

## 🚀 Quick Start Workflow

### **First Time Setup**
```bash
1. cd /Users/ryanmacomber/Documents/Orchestrator-Agent
2. ./install-local.sh
3. Restart terminal
```

### **Your First Task**
```bash
el-jefe "Write a brief introduction to AI orchestration"
```

### **Check Results**
```bash
el-jefe --list
ls workspaces/week-*/2025-*/
```

### **Continue Working**
```bash
el-jefe --resume workspaces/week-47/2025-11-23/your-task
```

## 🛠️ Advanced Usage

### **Non-Interactive Mode (Automation)**
```bash
# Perfect for scripts and automation
el-jefe --non-interactive "Generate weekly report"
```

### **Custom Workspace Location**
```bash
# Store projects in your preferred location
el-jefe --workspace-dir ~/Documents/AI-Projects "My project"
```

### **Verbose Logging**
```bash
# See detailed execution information
el-jefe --verbose "Complex research task"
```

## 📝 Tips for Best Results

### **Be Specific**
```bash
✅ Good: "Research the latest Python web frameworks and compare their performance"
❌ Vague: "Research Python"
```

### **Define the Output**
```bash
✅ Good: "Create a Python script to analyze sales data and generate charts"
❌ Vague: "Work with sales data"
```

### **Use Appropriate Scope**
```bash
✅ Good: "Write a blog post about microservices" (1-2 hours)
❌ Too Big: "Build a complete e-commerce platform" (days/weeks)
```

### **Iterate and Refine**
```bash
# Start broad
el-jefe "Research AI orchestration concepts"

# Then get specific
el-jefe --resume workspace-path "Create a tutorial on implementing agent coordination"
```

## 🆘 Troubleshooting

### **Command Not Found**
```bash
# Make sure installation worked
echo $PATH | grep Orchestrator

# Or use full path
/Users/ryanmacomber/Documents/Orchestrator-Agent/el-jefe --help
```

### **Check Dependencies**
```bash
cd /Users/ryanmacomber/Documents/Orchestrator-Agent
python3 test_orchestrator.py
```

### **API Issues**
```bash
# Check your .env file
cat .env

# Verify API key is working
el-jefe --verbose "Simple test task"
```

## 🎉 You're Ready!

Start using your AI orchestrator:

```bash
el-jefe "Your first AI-powered task"
```

The system will handle the rest - breaking down your goal, coordinating specialist agents, and delivering organized results!