# AI Orchestrator SDK (Personal Projects & Podcast Research)

## Setup
- Python 3.9+
- claude-agent-sdk (Install via pip)
- aiofiles (for async file I/O)

## Usage
1. Clone folder structure.
2. Run: `python orchestrator.py <project-folder> "<task/topic description>"`
   - Example: `python orchestrator.py 2025-11-24-ai-podcast-news "Research new AI trends for this week's podcast"`
3. Agent outputs saved in `projects/<your-folder>/`
   - Notes, logs, draft scripts, code snippets.

## Extendability
- Add more agent types in `agents/`
- Customize tools in `tools/`
- Log and review workflow steps in `workflow-history.json`
- Attach large context/history in `context-main.md`

## Best Practice
- Use one folder per topic/project for pristine context and easy cleanup.
- All agents read/write only files inside the project folder for separation and privacy.
