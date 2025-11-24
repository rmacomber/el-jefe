"""
Enhanced CLI Input Module with History and Auto-completion

Provides advanced command-line input functionality including:
- Arrow key navigation through command history
- Intelligent auto-completion suggestions
- Tab key completion for accepting suggestions
- Persistent command history storage
"""

import os
import json
import re
import asyncio
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque


@dataclass
class CommandSuggestion:
    """Represents a command suggestion."""
    text: str
    description: str
    score: float = 0.0
    category: str = "general"


class CLIInput:
    """Enhanced CLI input with history and auto-completion."""

    def __init__(self, history_file: Optional[Path] = None, max_history: int = 1000):
        """
        Initialize the CLI input system.

        Args:
            history_file: Path to store command history
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        self.history_file = history_file or Path.home() / ".el-jefe" / "command_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Command history
        self.history: deque[str] = deque(maxlen=max_history)
        self.history_index = -1

        # Auto-completion data
        self.command_patterns = self._load_command_patterns()
        self.recent_commands = []

        # Current input state
        self.current_input = ""
        self.cursor_position = 0
        self.suggestions: List[CommandSuggestion] = []
        self.selected_suggestion = 0

        # Load existing history
        self._load_history()

        # Keyboard state tracking
        self._setup_keyboard_detection()

    def _load_command_patterns(self) -> Dict[str, List[CommandSuggestion]]:
        """Load command patterns for auto-completion."""
        return {
            # Workflow commands
            "start": [
                CommandSuggestion(
                    "start \"research AI trends\"",
                    "Start autonomous workflow with research goal",
                    0.9,
                    "workflow"
                ),
                CommandSuggestion(
                    "start \"Build a Python API\"",
                    "Start autonomous workflow with development goal",
                    0.9,
                    "workflow"
                ),
                CommandSuggestion(
                    "start \"Write documentation\"",
                    "Start autonomous workflow with writing goal",
                    0.8,
                    "workflow"
                ),
                CommandSuggestion(
                    "start \"Analyze data\"",
                    "Start autonomous workflow with analysis goal",
                    0.8,
                    "workflow"
                ),
                CommandSuggestion(
                    "start \"Create presentation\"",
                    "Start autonomous workflow with presentation goal",
                    0.7,
                    "workflow"
                )
            ],
            "start-streaming": [
                CommandSuggestion(
                    "start-streaming \"Real-time monitoring\"",
                    "Start streaming workflow with real-time output",
                    0.8,
                    "workflow"
                ),
                CommandSuggestion(
                    "start-streaming \"API development\"",
                    "Start streaming workflow for API development",
                    0.8,
                    "workflow"
                ),
                CommandSuggestion(
                    "start-streaming \"Data analysis\"",
                    "Start streaming workflow for data analysis",
                    0.8,
                    "workflow"
                )
            ],

            # Scheduler commands
            "schedule": [
                CommandSuggestion(
                    "schedule-list",
                    "List all scheduled workflows",
                    1.0,
                    "scheduler"
                ),
                CommandSuggestion(
                    "schedule-add \"Daily Report\" \"Generate daily analytics\" \"daily\"",
                    "Add daily scheduled workflow",
                    0.9,
                    "scheduler"
                ),
                CommandSuggestion(
                    "schedule-add \"Weekly Backup\" \"Backup files\" \"weekly\"",
                    "Add weekly scheduled workflow",
                    0.9,
                    "scheduler"
                )
            ],
            "schedule-daemon": [
                CommandSuggestion(
                    "schedule-daemon",
                    "Start scheduler daemon for automatic execution",
                    1.0,
                    "scheduler"
                )
            ],

            # Management commands
            "list": [
                CommandSuggestion(
                    "list",
                    "List recent workspaces",
                    1.0,
                    "management"
                )
            ],
            "cleanup": [
                CommandSuggestion(
                    "cleanup 7",
                    "Clean up workspaces older than 7 days",
                    0.8,
                    "management"
                )
            ],
            "resume": [
                CommandSuggestion(
                    "resume workspaces/week-47/",
                    "Resume work in existing workspace",
                    0.9,
                    "management"
                )
            ],

            # Help and info commands
            "help": [
                CommandSuggestion(
                    "help",
                    "Show available commands and usage",
                    1.0,
                    "help"
                )
            ],
            "schedule-help": [
                CommandSuggestion(
                    "schedule-help",
                    "Show scheduler-specific help",
                    1.0,
                    "help"
                )
            ],

            # Interactive mode commands
            "exit": [
                CommandSuggestion(
                    "exit",
                    "Exit the application",
                    1.0,
                    "system"
                ),
                CommandSuggestion(
                    "quit",
                    "Exit the application",
                    1.0,
                    "system"
                )
            ]
        }

    def _load_history(self) -> None:
        """Load command history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    history = data.get('history', [])
                    self.history = deque(history, maxlen=self.max_history)
                    self.history_index = -1
        except (FileNotFoundError, json.JSONDecodeError):
            # Start with empty history
            pass

    def _save_history(self) -> None:
        """Save command history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump({
                    'history': list(self.history),
                    'last_saved': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            # Silently fail for history saving issues
            pass

    def _setup_keyboard_detection(self) -> None:
        """Setup keyboard detection (works in most terminals)."""
        # This is a simplified approach - in a real implementation,
        # you might use libraries like prompt_toolkit or readchar
        pass

    def get_command_suggestions(self, partial_input: str) -> List[CommandSuggestion]:
        """Get intelligent suggestions based on partial input."""
        suggestions = []

        # Extract first word to check for patterns
        first_word = partial_input.strip().split()[0] if partial_input.strip() else ""

        # Add suggestions based on patterns
        if first_word in self.command_patterns:
            suggestions.extend(self.command_patterns[first_word])

        # Add general goal suggestions
        if not first_word or partial_input.strip().startswith('"'):
            goal_suggestions = [
                CommandSuggestion(
                    f"Research \"{partial_input.strip().strip('"') or 'Research latest trends'}\"",
                    "Research and analyze current trends",
                    0.7,
                    "goal"
                ),
                CommandSuggestion(
                    f"Analyze \"{partial_input.strip().strip('"') or 'Analyze data patterns'}\"",
                    "Analyze data and identify patterns",
                    0.7,
                    "goal"
                ),
                CommandSuggestion(
                    f"Create \"{partial_input.strip().strip('"') or 'Create documentation'}\"",
                    "Create comprehensive documentation",
                    0.7,
                    "goal"
                ),
                CommandSuggestion(
                    f"Build \"{partial_input.strip().strip('"') or 'Build Python script'}\"",
                    "Build Python application with proper structure",
                    0.7,
                    "goal"
                ),
                CommandSuggestion(
                    f"Design \"{partial_input.strip().strip('"') or 'Design system architecture'}\"",
                    "Design scalable system architecture",
                    0.7,
                    "goal"
                )
            ]

            # Filter by partial input
            for suggestion in goal_suggestions:
                if partial_input.lower() in suggestion.text.lower() or not partial_input.strip():
                    suggestions.append(suggestion)

        # Add recent commands if they match
        for cmd in self.recent_commands[-5:]:  # Last 5 recent commands
            if partial_input.lower() in cmd.lower():
                suggestions.append(CommandSuggestion(
                    cmd,
                    f"Recent command: {cmd}",
                    0.6,
                    "recent"
                ))

        # Sort by score and relevance
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:10]  # Top 10 suggestions

    def format_prompt_with_suggestion(self, base_prompt: str, suggestion: CommandSuggestion) -> str:
        """Format the prompt line with the selected suggestion."""
        if suggestion and suggestion.text:
            # Replace partial input with suggestion
            current_words = base_prompt.strip().split()
            if current_words:
                # Replace the current word/phrase with suggestion
                last_word = current_words[-1]
                if suggestion.text.startswith(last_word):
                    new_prompt = ' '.join(current_words[:-1]) + ' ' + suggestion.text
                else:
                    new_prompt = suggestion.text
            else:
                new_prompt = suggestion.text
        else:
            new_prompt = base_prompt

        return f"💬 El Jefe> {new_prompt}"

    async def get_enhanced_input(self, prompt: str = "") -> str:
        """
        Get user input with history navigation and auto-completion.

        Args:
            prompt: Base prompt to display

        Returns:
            User input string
        """
        try:
            import readline  # Import here for interactive use only
        except ImportError:
            # Fallback to basic input if readline not available
            return input(f"\n💬 El Jefe> {prompt}")

        # Configure readline for auto-completion
        try:
            # Set up tab completion
            readline.set_completer(self._tab_completer)

            # Set up history
            readline.set_history_length(self.max_history)
            for cmd in self.history:
                readline.add_history(cmd)

            # Add current input to readline history
            if self.current_input:
                readline.add_history(self.current_input)

            # Custom prompt
            full_prompt = f"💬 El Jefe> {prompt}"

            # Get user input
            user_input = input(full_prompt).strip()

            # Update history if input is not empty
            if user_input:
                self._add_to_history(user_input)
                self._update_recent_commands(user_input)

            return user_input

        except Exception as e:
            # Fallback to basic input if readline fails
            return input(f"\n💬 El Jefe> {prompt}").strip()

    def _tab_completer(self, text: str, state: int) -> List[str]:
        """Tab completion function for readline."""
        if state == 0:  # First tab press - show suggestions
            line = readline.get_line_buffer()
            cursor_pos = readline.get_begidx() if hasattr(readline, 'get_begidx') else 0
            current_text = line[:cursor_pos]

            suggestions = self.get_command_suggestions(current_text)
            if suggestions:
                self.suggestions = suggestions
                self.selected_suggestion = 0
                return [s.text for s in suggestions]
            else:
                self.suggestions = []
                return []

        elif state == 1: # Second tab - cycle through suggestions
            if self.suggestions:
                self.selected_suggestion = (self.selected_suggestion + 1) % len(self.suggestions)
                return [self.suggestions[self.selected_suggestion].text]
            else:
                return []
        else:
            return []

    def _add_to_history(self, command: str) -> None:
        """Add command to history."""
        # Avoid duplicates
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
            self._save_history()

    def _update_recent_commands(self, command: str) -> None:
        """Update recent commands list."""
        # Remove from recent if it exists
        if command in self.recent_commands:
            self.recent_commands.remove(command)

        # Add to beginning
        self.recent_commands.insert(0, command)

        # Keep only last 20 commands
        self.recent_commands = self.recent_commands[:20]

    def navigate_history_up(self) -> Optional[str]:
        """Navigate up through command history."""
        if not self.history:
            return None

        if self.history_index == -1:
            self.history_index = len(self.history) - 1
        elif self.history_index > 0:
            self.history_index -= 1

        return self.history[self.history_index]

    def navigate_history_down(self) -> Optional[str]:
        """Navigate down through command history."""
        if not self.history:
            return None

        if self.history_index < len(self.history) - 1:
            self.history_index += 1
        elif self.history_index == len(self.history) - 1:
            self.history_index = -1

        return self.history[self.history_index] if self.history_index >= 0 else None

    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()
        self.recent_commands.clear()
        self._save_history()

    def get_history_stats(self) -> Dict[str, Any]:
        """Get statistics about command history."""
        return {
            'total_commands': len(self.history),
            'recent_commands': len(self.recent_commands),
            'history_file': str(self.history_file),
            'max_history': self.max_history
        }