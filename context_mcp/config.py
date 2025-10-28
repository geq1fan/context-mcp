"""Configuration management for Context MCP server.

Loads configuration from environment variables with validation.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    """Project configuration loaded from environment variables.

    Attributes:
        root_path: Project root directory (absolute path)
        search_timeout: Search operation timeout in seconds
        log_retention_days: Log file retention period
        log_level: Logging level (integer constant from logging module)
    """

    root_path: Path
    search_timeout: int = 60
    log_retention_days: int = 7
    log_level: int = logging.WARNING

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate root_path exists and is a directory
        if not self.root_path.exists():
            raise ValueError(f"PROJECT_ROOT does not exist: {self.root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"PROJECT_ROOT is not a directory: {self.root_path}")

        # Validate search_timeout
        if self.search_timeout <= 0:
            raise ValueError(f"SEARCH_TIMEOUT must be positive: {self.search_timeout}")

        # Validate log_retention_days
        if self.log_retention_days < 1:
            raise ValueError(
                f"log_retention_days must be >= 1: {self.log_retention_days}"
            )

        # Validate log_level
        valid_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        if self.log_level not in valid_levels:
            level_names = [logging.getLevelName(level) for level in valid_levels]
            raise ValueError(
                f"log_level must be one of {level_names}: {self.log_level}"
            )


def load_config() -> ProjectConfig:
    """Load configuration from environment variables.

    Returns:
        ProjectConfig instance with validated settings

    Raises:
        ValueError: If PROJECT_ROOT is not set or invalid
    """
    # PROJECT_ROOT is required
    root_str = os.getenv("PROJECT_ROOT")
    if not root_str:
        raise ValueError(
            "PROJECT_ROOT environment variable is required. "
            "Set it to your project directory path."
        )

    root_path = Path(root_str).resolve()

    # SEARCH_TIMEOUT is optional (default: 60)
    timeout_str = os.getenv("SEARCH_TIMEOUT", "60")
    try:
        search_timeout = int(timeout_str)
    except ValueError:
        raise ValueError(f"SEARCH_TIMEOUT must be an integer: {timeout_str}")

    # LOG_LEVEL is optional (default: WARNING)
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()
    try:
        log_level = getattr(logging, log_level_str)
        if not isinstance(log_level, int):
            raise AttributeError()
    except AttributeError:
        valid_names = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        raise ValueError(f"LOG_LEVEL must be one of {valid_names}: {log_level_str}")

    # Create and validate config
    return ProjectConfig(
        root_path=root_path,
        search_timeout=search_timeout,
        log_retention_days=7,  # Fixed per requirements
        log_level=log_level,
    )


# Global config instance (loaded on module import)
config: ProjectConfig | None
try:
    config = load_config()
except ValueError as e:
    # Allow import even if config is invalid (for testing)
    # Real server will fail at startup
    config = None
    print(f"Warning: Configuration not loaded: {e}")
