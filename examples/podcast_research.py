#!/usr/bin/env python3
"""
Example: Podcast Research Workflow

This example demonstrates how to use the AI Orchestrator SDK
to research topics for a podcast episode.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.orchestrator import Orchestrator


async def main():
    """Run podcast research example."""

    # Initialize orchestrator
    orchestrator = Orchestrator(
        base_dir="workspaces",
        interactive=True
    )

    # Define research goals for different podcast types
    research_goals = [
        "Research the latest AI developments for this week's tech podcast",
        "Find interesting stories about startup failures and lessons learned",
        "Investigate the impact of remote work on company culture",
        "Explore sustainable technology innovations of 2024",
        "Analyze the rise of creator economy and its future trends"
    ]

    print("🎙️ Podcast Research Assistant")
    print("=" * 50)
    print("\nAvailable research topics:")

    for i, goal in enumerate(research_goals, 1):
        print(f"{i}. {goal}")

    print("\n9. Custom research topic")
    print("0. Exit")

    # Get user choice
    while True:
        try:
            choice = input("\nSelect a topic (0-9): ").strip()

            if choice == "0":
                print("Goodbye! 👋")
                return
            elif choice == "9":
                custom_topic = input("Enter your research topic: ").strip()
                if custom_topic:
                    goal = custom_topic
                    break
            elif choice.isdigit() and 1 <= int(choice) <= len(research_goals):
                goal = research_goals[int(choice) - 1]
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            return

    print(f"\n🔍 Researching: {goal}")
    print("This may take a few minutes...\n")

    try:
        # Execute the research
        result = await orchestrator.execute_goal(goal)

        # Display results
        print("\n" + "=" * 50)
        print("✅ RESEARCH COMPLETED")
        print("=" * 50)

        print(f"\n📁 Workspace: {result['workspace']}")
        print(f"📊 Steps completed: {len(result['results'])}")
        print(f"📈 Success rate: {result['summary']['success_rate']}")

        # Show generated files
        if result['summary']['output_files']:
            print("\n📄 Generated files:")
            for file_path in result['summary']['output_files']:
                if file_path:  # Skip None values
                    print(f"   - {file_path}")

        # Show workspace structure
        workspace_path = Path(result['workspace'])
        if workspace_path.exists():
            print("\n📂 Workspace contents:")
            for file_path in sorted(workspace_path.rglob("*")):
                if file_path.is_file():
                    relative_path = file_path.relative_to(workspace_path)
                    size = file_path.stat().st_size
                    print(f"   {relative_path} ({size} bytes)")

        print(f"\n🎯 Next steps:")
        print(f"1. Review the generated files in: {result['workspace']}")
        print(f"2. Check context-main.md for the complete research summary")
        print(f"3. Use the research notes to craft your podcast episode")

    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())