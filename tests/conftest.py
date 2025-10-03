"""Pytest configuration for context-mcp tests.

Sets up PROJECT_ROOT environment variable for all tests.
"""
import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables before any tests run."""
    # Set PROJECT_ROOT to the repository root
    repo_root = Path(__file__).parent.parent.resolve()
    os.environ["PROJECT_ROOT"] = str(repo_root)

    # Re-import config module to load configuration with new environment
    import importlib
    import agent_mcp.config
    importlib.reload(agent_mcp.config)

    # Also reload tool modules to pick up new config
    import agent_mcp.tools.navigation
    import agent_mcp.tools.search
    import agent_mcp.tools.read

    importlib.reload(agent_mcp.tools.navigation)
    importlib.reload(agent_mcp.tools.search)
    importlib.reload(agent_mcp.tools.read)

    yield

    # Cleanup after tests (optional)
    # os.environ.pop("PROJECT_ROOT", None)
