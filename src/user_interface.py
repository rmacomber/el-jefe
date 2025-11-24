"""
User Interface Module

Handles user interactions, prompts, and confirmations.
Provides both interactive and non-interactive modes.
"""

import asyncio
from typing import Optional, Union, Dict, Any
from enum import Enum


class ResponseType(Enum):
    """Types of user responses."""
    YES = "yes"
    NO = "no"
    CUSTOM = "custom"
    CANCEL = "cancel"


class UserInterface:
    """
    Handles user interactions and approvals.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the user interface.

        Args:
            verbose: Whether to show detailed prompts
        """
        self.verbose = verbose
        self.interactive = True

    def set_interactive(self, interactive: bool):
        """
        Set the interactive mode.

        Args:
            interactive: Whether to prompt for user input
        """
        self.interactive = interactive

    async def request_approval(self, prompt: str, default: bool = False) -> bool:
        """
        Request user approval for an action.

        Args:
            prompt: The approval prompt
            default: Default response if non-interactive

        Returns:
            True if approved, False otherwise
        """
        if not self.interactive:
            return default

        while True:
            try:
                response = input(f"\n{prompt}\nProceed? (y/n): ").strip().lower()
                if response in ['y', 'yes', 'Y', 'YES']:
                    return True
                elif response in ['n', 'no', 'N', 'NO']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled")
                return False

    async def get_user_input(
        self,
        prompt: str,
        default: Optional[str] = None,
        validation_func: Optional[callable] = None
    ) -> Optional[str]:
        """
        Get input from the user.

        Args:
            prompt: The input prompt
            default: Default value if user provides no input
            validation_func: Function to validate the input

        Returns:
            User input or default value
        """
        if not self.interactive:
            return default

        while True:
            try:
                if default:
                    full_prompt = f"{prompt} (default: {default}): "
                else:
                    full_prompt = f"{prompt}: "

                response = input(full_prompt).strip()

                if not response and default:
                    return default

                if validation_func:
                    if validation_func(response):
                        return response
                    else:
                        print("Invalid input. Please try again.")
                else:
                    return response

            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled")
                return None

    async def select_from_list(
        self,
        prompt: str,
        options: list,
        default_index: Optional[int] = None
    ) -> Optional[Union[str, int]]:
        """
        Let user select from a list of options.

        Args:
            prompt: The selection prompt
            options: List of options to choose from
            default_index: Default selection index

        Returns:
            Selected option or index
        """
        if not self.interactive:
            return options[default_index] if default_index and default_index < len(options) else None

        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            marker = " (default)" if i - 1 == default_index else ""
            print(f"{i}. {option}{marker}")

        while True:
            try:
                if default_index is not None:
                    response = input(f"Select option (1-{len(options)}) or press Enter for default: ")
                    if not response:
                        return options[default_index]
                else:
                    response = input(f"Select option (1-{len(options)}): ")

                choice = int(response)
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(options)}")

            except ValueError:
                print("Please enter a valid number")
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled")
                return None

    async def confirm_file_operation(self, operation: str, file_path: str) -> bool:
        """
        Confirm a file operation with the user.

        Args:
            operation: Description of the operation
            file_path: Path to the file

        Returns:
            True if confirmed, False otherwise
        """
        return await self.request_approval(
            f"About to {operation}: {file_path}",
            default=False
        )

    async def show_progress(self, steps: list, current_step: int):
        """
        Show progress of workflow execution.

        Args:
            steps: List of all steps
            current_step: Current step index
        """
        if not self.verbose:
            return

        total = len(steps)
        completed = current_step
        remaining = total - completed

        progress_bar = self._create_progress_bar(completed, total)
        print(f"\n{progress_bar} {completed}/{total} steps completed")

        # Show current and next steps
        if completed < total:
            print(f"Current: {steps[completed]['description']}")
            if completed + 1 < total:
                print(f"Next: {steps[completed + 1]['description']}")

    def _create_progress_bar(self, completed: int, total: int, width: int = 40) -> str:
        """
        Create a text progress bar.

        Args:
            completed: Number of completed items
            total: Total number of items
            width: Width of the progress bar

        Returns:
            Progress bar string
        """
        filled = int(width * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    async def show_summary(self, summary: Dict[str, Any]):
        """
        Show a summary of execution results.

        Args:
            summary: Summary dictionary
        """
        print("\n" + "="*50)
        print("EXECUTION SUMMARY")
        print("="*50)

        print(f"\nGoal: {summary.get('goal', 'N/A')}")
        print(f"Status: {summary.get('status', 'N/A').upper()}")

        if 'total_steps' in summary:
            print(f"\nSteps Executed: {summary['total_steps']}")
            if 'completed_steps' in summary:
                print(f"Completed: {summary['completed_steps']}")
                print(f"Failed: {summary.get('failed_steps', 0)}")

        if 'agents_used' in summary:
            print(f"\nAgents Used: {', '.join(summary['agents_used'])}")

        if 'workspace' in summary:
            print(f"\nWorkspace: {summary['workspace']}")

        if 'execution_time' in summary:
            print(f"\nExecution Time: {summary['execution_time']}")

        print("\n" + "="*50)

    async def show_error(self, error: Exception, context: Optional[str] = None):
        """
        Show an error message.

        Args:
            error: The exception that occurred
            context: Additional context about the error
        """
        print(f"\n❌ Error: {str(error)}")
        if context:
            print(f"Context: {context}")

    async def show_warning(self, message: str):
        """
        Show a warning message.

        Args:
            message: Warning message
        """
        print(f"\n⚠️  Warning: {message}")

    async def show_info(self, message: str):
        """
        Show an informational message.

        Args:
            message: Information message
        """
        print(f"\nℹ️  {message}")

    async def show_success(self, message: str):
        """
        Show a success message.

        Args:
            message: Success message
        """
        print(f"\n✅ {message}")