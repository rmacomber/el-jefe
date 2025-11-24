#!/usr/bin/env python3
"""
Example: Data Analysis Workflow

This example demonstrates how to use the AI Orchestrator SDK
to create a complete data analysis solution.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.orchestrator import Orchestrator


async def main():
    """Run data analysis example."""

    # Initialize orchestrator
    orchestrator = Orchestrator(
        base_dir="workspaces",
        interactive=True
    )

    print("📊 Data Analysis Assistant")
    print("=" * 50)

    # Sample data analysis tasks
    analysis_tasks = [
        "Create a Python script to analyze sales data from CSV and generate charts",
        "Build a dashboard to visualize customer analytics with matplotlib",
        "Develop a data pipeline to process and clean raw sensor data",
        "Analyze website traffic patterns and generate insights report",
        "Create a machine learning model to predict customer churn"
    ]

    print("\nPre-configured analysis tasks:")

    for i, task in enumerate(analysis_tasks, 1):
        print(f"{i}. {task}")

    print("\n9. Custom analysis task")
    print("0. Exit")

    # Get user choice
    while True:
        try:
            choice = input("\nSelect a task (0-9): ").strip()

            if choice == "0":
                print("Goodbye! 👋")
                return
            elif choice == "9":
                custom_task = input("Describe your data analysis task: ").strip()
                if custom_task:
                    task = custom_task
                    break
            elif choice.isdigit() and 1 <= int(choice) <= len(analysis_tasks):
                task = analysis_tasks[int(choice) - 1]
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            return

    # Ask for specific requirements
    print("\n📝 Additional requirements (optional):")
    requirements = []

    if input("Include data visualization? (y/n): ").lower() == 'y':
        requirements.append("Include interactive charts and visualizations")

    if input("Generate documentation? (y/n): ").lower() == 'y':
        requirements.append("Include comprehensive documentation and comments")

    if input("Add unit tests? (y/n): ").lower() == 'y':
        requirements.append("Include unit tests for the solution")

    # Build full task description
    if requirements:
        task += f"\n\nAdditional requirements:\n" + "\n".join(f"- {r}" for r in requirements)

    print(f"\n🔧 Building solution: {task}")
    print("This may take several minutes...\n")

    try:
        # Execute the task
        result = await orchestrator.execute_goal(task)

        # Display results
        print("\n" + "=" * 50)
        print("✅ ANALYSIS SOLUTION COMPLETED")
        print("=" * 50)

        print(f"\n📁 Workspace: {result['workspace']}")
        print(f"📊 Steps completed: {len(result['results'])}")
        print(f"📈 Success rate: {result['summary']['success_rate']}")

        # Show agent usage
        if 'agents_used' in result['summary']:
            print(f"\n🤖 Agents used: {', '.join(result['summary']['agents_used'])}")

        # Show generated files
        output_files = [f for f in result['summary']['output_files'] if f]
        if output_files:
            print(f"\n📄 Generated files:")
            for file_path in output_files:
                print(f"   - {file_path}")

        # Check for Python files specifically
        workspace_path = Path(result['workspace'])
        python_files = list(workspace_path.glob("*.py"))
        if python_files:
            print(f"\n🐍 Python scripts created:")
            for py_file in python_files:
                print(f"   - {py_file.name}")

        # Show how to run the solution
        if python_files:
            print(f"\n🚀 To run the solution:")
            print(f"   cd {workspace_path}")
            for py_file in python_files:
                print(f"   python {py_file.name}")

        print(f"\n📋 Next steps:")
        print(f"1. Review the generated code in: {result['workspace']}")
        print(f"2. Check architecture_design.md for the solution overview")
        print(f"3. Test the implementation with your data")
        print(f"4. Review test_report.md for quality validation")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())