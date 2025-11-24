Chain-of-Thought Prompt: Personal Orchestrator SDK Agent
Goal
You are an advanced, tool-using coding agent. Your mission is to build a Python project using the Claude Agent SDK that can orchestrate complex tasks: break down goals, spawn specialist agents, and organize all work in clean, date-based folders for personal research, creation, and learning.

Instructions
Requirements Gathering

Clarify the goal: “Build a personal orchestrator that can research, code, write, analyze, or design by spawning specialist agents for each sub-task and storing all work in organized folders.”

Project Structure

Create main folder: personal-orchestrator-agent/

Subfolders: src/, examples/, scripts/, workspaces/, config/, docs/

Key files: src/orchestrator.py, requirements.txt, .env.example, README.md, SETUP_GUIDE.md

Define Agent Types

Researcher: research and synthesize information.

Coder: build software, write scripts.

Writer: create and edit documents/content.

Analyst: data and trend analysis.

Designer: architecture and system planning.

QA Tester: validation and testing.

Workspace Management

Implement a WorkspaceManager class that:

Creates a folder structure like workspaces/week-XX/day/TASKNAME-hhmmss/

Initializes files: context-main.md, workflow-history.json

Logs agent actions and workflow steps in JSON.

Custom SDK Tools

Tool1: create_task_workspace(task_name, task_description) — creates a workspace and logs context.

Tool2: spawn_specialist_agent(agent_type, task_description, context, output_files) — launches a specialist agent, assigns tools based on type, contains work to current workspace, records results.

Tool3: review_workspace() — summarizes all work, agents, and progress for the workspace.

Tool4: request_user_input(question, context) — pauses and asks the user for clarification/approval, logs result.

Orchestrator Agent Logic

Compose a chain of steps:

Parse the user’s goal into logical sub-tasks.

Create an organized workspace.

For each sub-task, select a specialist agent type, spawn the agent, and assign the task.

Coordinate agents: run tasks sequentially if dependent, parallel if independent.

Aggregate all outputs and document progress.

Always update context-main.md and workflow-history.json.

Review final results, summarize in markdown.

Ask the user for decisions before expensive or destructive steps.

Human-in-the-Loop

Enable user control at critical steps (tool use, major decisions).

Implement an approval/confirmation prompt before agent actions that affect data or incur cost.

API/CLI Interface

Main script receives the goal as an argument: python src/orchestrator.py "Research topics for my podcast"

Orchestrator agent launches and runs the workflow.

Examples and Utilities

Provide example scripts for research, coding, content creation, and analysis tasks.

Utilities: cost summary, workspace cleaner, workspace lister scripts in scripts/.

Documentation

Write comprehensive README.md explaining usage, features, architecture, agent types, safety features, and best practices.

Step-by-step SETUP_GUIDE.md for installation, prerequisites, configuration, and troubleshooting.

Example workflows in EXAMPLES.md.

Extensibility

Make agent types and config easily modifiable: allow user to add new agent specializations or customize tool chains in one place.

Best Practices

Keep all context and progress in single markdown file per workspace.

Use JSON for detailed workflow logs.

Limit agent turns to control cost.

Always respect file boundaries; agents only write in their workspace.

Provide clear error handling and logging.

Deliverable
A complete, ready-to-run Python project—with all code, docs, and utilities—following the above logic and architecture. Organize source files so everything is read