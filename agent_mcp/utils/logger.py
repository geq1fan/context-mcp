"""Logging configuration for Context MCP server.

Implements TimedRotatingFileHandler with 7-day retention period.
"""
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(log_file: str = "agent_mcp.log", level: int = logging.INFO) -> logging.Logger:
    """Configure logging with timed rotation.

    Args:
        log_file: Log file name (default: agent_mcp.log)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("agent_mcp")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    if log_path.parent != Path("."):
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure timed rotating file handler (daily rotation, 7 days retention)
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='D',           # Daily rotation
        interval=1,         # Every 1 day
        backupCount=7,      # Keep 7 days of logs
        encoding='utf-8'
    )

    # Set format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Also log to console in development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_logging()
