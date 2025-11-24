import os
import sys
import json
from datetime import datetime
import asyncio
from agents.researcher_agent import run_researcher_agent
from agents.writer_agent import run_writer_agent
from agents.coder_agent import run_coder_agent

PROJECTS_DIR = "projects"

def create_project_folder(project_name):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(os.path.join(project_path, "agent_outputs"), exist_ok=True)
    for fname in ["context-main.md", "workflow-history.json", "research_notes.md", "draft_article.md"]:
        with open(os.path.join(project_path, fname), "w") as f:
            if fname.endswith(".md"):
                f.write(f"# {project_name} context\n\n")
            else:
                json.dump([], f)
    print(f"Created {project_path}")
    return project_path

async def orchestrator(project_name, task):
    project_path = create_project_folder(project_name)
    context_path = os.path.join(project_path, "context-main.md")
    log_path = os.path.join(project_path, "workflow-history.json")
    notes_path = os.path.join(project_path, "research_notes.md")
    article_path = os.path.join(project_path, "draft_article.md")

    history = []
    # 1) Run researcher agent
    research_result = await run_researcher_agent(task, notes_path, context_path)
    history.append({"step": "research", "result": research_result})

    # 2) Run writer agent
    write_result = await run_writer_agent(notes_path, article_path, context_path)
    history.append({"step": "write", "result": write_result})

    # 3) Optional: run coder agent (e.g., for code snippets)
    # coder_result = await run_coder_agent(article_path, context_path)
    # history.append({"step": "code", "result": coder_result})
    
    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Workflow log saved in {log_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python orchestrator.py <project-name> <task>")
        sys.exit(1)
    asyncio.run(orchestrator(sys.argv[1], sys.argv[2]))
