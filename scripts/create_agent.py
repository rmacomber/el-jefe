#!/usr/bin/env python3
"""
Interactive Agent Creation Script for El Jefe

Provides a command-line interface for creating agents from templates
with customizations and validation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from templated_agent_manager import TemplatedAgentManager, TemplateRegistry


class AgentCreatorCLI:
    """Interactive CLI for creating agents from templates."""

    def __init__(self):
        self.workspace_path = Path("workspaces/demo_agent_creation")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.template_manager = TemplatedAgentManager(self.workspace_path)

        print("🚀 El Jefe Agent Template System")
        print("=" * 50)

    def show_available_templates(self):
        """Display available templates."""
        print("\n📋 Available Agent Templates:")
        print("-" * 30)

        templates = self.template_manager.list_available_templates()

        if not templates:
            print("No templates available.")
            return

        for name, info in templates.items():
            print(f"\n🏷️  {name}")
            print(f"   Domain: {info['domain']}")
            print(f"   Description: {info['description'][:60]}...")
            print(f"   Expertise: {', '.join(info['expertise_areas'])}")
            print(f"   Use Cases: {', '.join(info['use_cases'])}")

    def run(self):
        """Run the interactive CLI."""
        while True:
            print(f"\n🎯 What would you like to do?")
            print(f"1. List available templates")
            print(f"2. Exit")

            choice = input(f"\nEnter choice (1-2): ").strip()

            if choice == "1":
                self.show_available_templates()
            elif choice == "2":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-2.")


def main():
    """Main entry point."""
    cli = AgentCreatorCLI()
    cli.run()


if __name__ == "__main__":
    main()
