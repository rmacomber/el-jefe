from claude_agent_sdk import query, ClaudeAgentOptions
import aiofiles

async def run_researcher_agent(topic, notes_path, context_path):
    prompt = f"Research the topic '{topic}'. Summarize findings and recommend key points for a podcast episode. Write clear, actionable notes."
    options = ClaudeAgentOptions(
        system_prompt=f"You are a research agent specializing in {topic}. Write in clean bullet points.",
        allowed_tools=["search_web", "write_md"], max_turns=8
    )
    results = []
    async for message in query(prompt, options=options):
        for block in getattr(message, 'content', []):
            if getattr(block, "type", None) == "text":
                results.append(block.text)
    async with aiofiles.open(notes_path, "a") as f:
        await f.write("\n".join(results))
    return results
