from claude_agent_sdk import query, ClaudeAgentOptions
import aiofiles

async def run_coder_agent(article_path, context_path):
    with open(article_path, "r") as f:
        script = f.read()
    prompt = f"Based on this podcast script, generate Python code for a newsletter generator."
    options = ClaudeAgentOptions(
        system_prompt="You are a Python developer bot. Generate code snippets as needed.",
        allowed_tools=["write_md"], max_turns=5
    )
    results = []
    async for message in query(prompt, options=options):
        for block in getattr(message, 'content', []):
            if getattr(block, "type", None) == "text":
                results.append(block.text)
    return results
