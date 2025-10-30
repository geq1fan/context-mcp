"""Logging configuration for Context MCP server.

Implements optional TimedRotatingFileHandler with 7-day retention period.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(
    log_file: str = "context_mcp.log",
    level: int = logging.WARNING,
    enable_file_log: bool = False,
) -> logging.Logger:
    """Configure logging with optional file output.

    Args:
        log_file: Log file name (default: context_mcp.log)
        level: Logging level (default: WARNING)
        enable_file_log: Whether to enable file logging (default: False)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("context_mcp")
    logger.setLevel(level)

    # Set format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Check if handlers already exist
    has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, TimedRotatingFileHandler) for h in logger.handlers)
    has_file = any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers)

    # Add console handler if not exists (stderr)
    if not has_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Conditionally add file handler
    if enable_file_log and not has_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        if log_path.parent != Path("."):
            log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure timed rotating file handler (daily rotation, 7 days retention)
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when="D",  # Daily rotation
            interval=1,  # Every 1 day
            backupCount=7,  # Keep 7 days of logs
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger instance (console only)
logger = setup_logging()
