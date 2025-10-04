"""Tool detector: Detect availability of high-performance CLI tools.

This module provides a singleton ToolDetector class that checks for the
availability of ripgrep (rg) and fd tools on the system.
"""

import shutil
import subprocess
from typing import Optional


class ToolDetector:
    """Singleton tool detector for high-performance CLI tools.

    Detects availability of:
    - ripgrep (rg): Fast search tool
    - fd: Fast file finding tool

    The detection is performed once during initialization and cached
    for the lifetime of the process.
    """

    _instance: Optional["ToolDetector"] = None

    def __new__(cls) -> "ToolDetector":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize tool detection (runs only once)."""
        if self._initialized:
            return

        self._initialized = True
        self._ripgrep_path: Optional[str] = None
        self._fd_path: Optional[str] = None

        # Detect tools
        self._detect_ripgrep()
        self._detect_fd()

    def _detect_ripgrep(self) -> None:
        """Detect ripgrep availability."""
        self._ripgrep_path = self._check_tool("rg")

    def _detect_fd(self) -> None:
        """Detect fd availability."""
        self._fd_path = self._check_tool("fd")

    def _check_tool(self, tool_name: str) -> Optional[str]:
        """Check if a tool is available and executable.

        Args:
            tool_name: Name of the tool to check

        Returns:
            Path to the tool if available, None otherwise
        """
        # First check if tool exists in PATH
        tool_path = shutil.which(tool_name)
        if tool_path is None:
            return None

        # Verify tool is executable by running --version
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0:
                return tool_path
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

        return None

    @property
    def has_ripgrep(self) -> bool:
        """Check if ripgrep is available."""
        return self._ripgrep_path is not None

    @property
    def has_fd(self) -> bool:
        """Check if fd is available."""
        return self._fd_path is not None
