from claude_agent_sdk import query, ClaudeAgentOptions
import aiofiles

async def run_writer_agent(notes_path, article_path, context_path):
    with open(notes_path, "r") as f:
        notes = f.read()
    prompt = f"Based on the following notes, draft a podcast episode script: {notes}"
    options = ClaudeAgentOptions(
        system_prompt="You are a podcast episode writer. Use given notes, maintain a conversational but informative tone.",
        allowed_tools=["write_md"], max_turns=6
    )
    results = []
    async for message in query(prompt, options=options):
        for block in getattr(message, 'content', []):
            if getattr(block, "type", None) == "text":
                results.append(block.text)
    async with aiofiles.open(article_path, "a") as f:
        await f.write("\n".join(results))
    return results
