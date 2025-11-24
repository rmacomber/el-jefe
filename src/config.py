"""
Configuration Module

Manages configuration settings for the AI Orchestrator SDK.
Includes agent configurations, workspace settings, and environment variables.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class WorkspaceConfig:
    """Configuration for workspace management."""
    base_dir: str = "workspaces"
    max_workspace_age_days: int = 30
    auto_cleanup: bool = False
    workspace_template_dir: Optional[str] = None


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""
    default_max_turns: int = 6
    default_timeout: int = 300  # seconds
    cost_tracking: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    allow_external_apis: bool = True
    restrict_file_access: bool = True
    allowed_file_extensions: list = None
    sandbox_mode: bool = False

    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = [
                '.md', '.txt', '.json', '.csv', '.py', '.js',
                '.html', '.css', '.yaml', '.yml', '.xml'
            ]


@dataclass
class OrchestratorConfig:
    """Main configuration for the orchestrator."""
    workspace: WorkspaceConfig = None
    agent: AgentConfig = None
    security: SecurityConfig = None

    def __post_init__(self):
        if self.workspace is None:
            self.workspace = WorkspaceConfig()
        if self.agent is None:
            self.agent = AgentConfig()
        if self.security is None:
            self.security = SecurityConfig()


class ConfigManager:
    """
    Manages configuration loading and saving.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or "config/orchestrator.json"
        self.config = OrchestratorConfig()
        self._load_config()

    def _load_config(self):
        """Load configuration from file and environment."""
        # Start with defaults
        config_data = {}

        # Load from file if it exists
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                config_data.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")

        # Override with environment variables
        env_overrides = self._load_env_overrides()
        config_data.update(env_overrides)

        # Update config object
        if config_data:
            self._update_config_object(config_data)

    def _load_env_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables."""
        overrides = {}
        prefix = "ORCHESTRATOR_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                # Convert nested keys with __
                if "__" in config_key:
                    parts = config_key.split("__")
                    overrides = self._set_nested_value(overrides, parts, self._parse_value(value))
                else:
                    overrides[config_key] = self._parse_value(value)

        return overrides

    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type."""
        # Handle booleans
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Handle numbers
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Handle JSON
        if value.startswith('{') or value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # Default to string
        return value

    def _set_nested_value(self, data: Dict, parts: list, value: Any) -> Dict:
        """Set a nested value in a dictionary."""
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
        return data

    def _update_config_object(self, config_data: Dict[str, Any]):
        """Update the config object with loaded data."""
        # Update workspace config
        if "workspace" in config_data:
            for key, value in config_data["workspace"].items():
                if hasattr(self.config.workspace, key):
                    setattr(self.config.workspace, key, value)

        # Update agent config
        if "agent" in config_data:
            for key, value in config_data["agent"].items():
                if hasattr(self.config.agent, key):
                    setattr(self.config.agent, key, value)

        # Update security config
        if "security" in config_data:
            for key, value in config_data["security"].items():
                if hasattr(self.config.security, key):
                    setattr(self.config.security, key, value)

    def save_config(self, config_file: Optional[str] = None):
        """
        Save current configuration to file.

        Args:
            config_file: Path to save configuration (uses default if None)
        """
        if config_file is None:
            config_file = self.config_file

        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dictionary
        config_dict = {
            "workspace": asdict(self.config.workspace),
            "agent": asdict(self.config.agent),
            "security": asdict(self.config.security)
        }

        # Save to file
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def get_config(self) -> OrchestratorConfig:
        """Get the current configuration."""
        return self.config

    def update_config(self, **kwargs):
        """
        Update configuration values.

        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> OrchestratorConfig:
    """Get the global configuration."""
    return config_manager.get_config()


def reload_config():
    """Reload configuration from file and environment."""
    config_manager._load_config()