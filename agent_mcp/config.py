"""Configuration management for Context MCP server.

Loads configuration from environment variables with validation.
"""
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    """Project configuration loaded from environment variables.

    Attributes:
        root_path: Project root directory (absolute path)
        search_timeout: Search operation timeout in seconds
        log_retention_days: Log file retention period
    """
    root_path: Path
    search_timeout: int = 60
    log_retention_days: int = 7

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
            raise ValueError(f"log_retention_days must be >= 1: {self.log_retention_days}")


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

    # Create and validate config
    return ProjectConfig(
        root_path=root_path,
        search_timeout=search_timeout,
        log_retention_days=7  # Fixed per requirements
    )


# Global config instance (loaded on module import)
try:
    config = load_config()
except ValueError as e:
    # Allow import even if config is invalid (for testing)
    # Real server will fail at startup
    config = None
    print(f"Warning: Configuration not loaded: {e}")
