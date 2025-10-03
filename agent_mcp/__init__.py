"""Context MCP - MCP server for project context integration.

Provides read-only filesystem operations for AI agents to analyze projects.
"""
from dataclasses import dataclass
from typing import Literal, Optional
from pathlib import Path


# ============================================================================
# Core Data Models
# ============================================================================

@dataclass(frozen=True)
class ProjectConfig:
    """Server configuration from environment variables."""
    root_path: Path
    search_timeout: int = 60
    log_retention_days: int = 7


@dataclass
class FileEntry:
    """Directory entry with metadata."""
    name: str
    type: Literal["file", "dir"]
    size: int
    mtime: float
    path: str


@dataclass
class SearchMatch:
    """Single search match result."""
    file_path: str
    line_number: int
    line_content: str
    match_start: Optional[int] = None
    match_end: Optional[int] = None


@dataclass
class SearchQuery:
    """Search query parameters."""
    query: str
    file_pattern: str = "*"
    path: str = "."
    use_regex: bool = False
    exclude_query: str = ""
    timeout: int = 60


@dataclass
class FileContent:
    """File reading result."""
    file_path: str
    content: str
    encoding: str
    line_count: int
    is_partial: bool = False


@dataclass
class TreeNode:
    """Directory tree node (recursive structure)."""
    name: str
    type: Literal["file", "dir"]
    depth: int
    children: Optional[list['TreeNode']] = None


# ============================================================================
# Exception Classes
# ============================================================================

class MCPError(Exception):
    """Base exception for all MCP errors."""
    pass


class PathSecurityError(MCPError):
    """Raised when path is outside project root."""

    def __init__(self, requested_path: str, root_path: str):
        self.requested_path = requested_path
        self.root_path = root_path
        super().__init__(
            f"PATH_SECURITY_ERROR: Path '{requested_path}' is outside root '{root_path}'"
        )


class BinaryFileError(MCPError):
    """Raised when attempting to read binary file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(
            f"BINARY_FILE_ERROR: Cannot read binary file '{file_path}'"
        )


class SearchTimeoutError(MCPError):
    """Raised when search operation times out."""

    def __init__(self, timeout_seconds: int, partial_results: Optional[list[SearchMatch]] = None):
        self.timeout_seconds = timeout_seconds
        self.partial_results = partial_results
        super().__init__(
            f"SEARCH_TIMEOUT: Search timed out after {timeout_seconds}s"
        )


class PermissionDeniedError(MCPError):
    """Raised when file permission is denied."""

    def __init__(self, file_path: str, operation: str):
        self.file_path = file_path
        self.operation = operation
        super().__init__(
            f"PERMISSION_DENIED: Cannot {operation} '{file_path}'"
        )


# Package version
__version__ = "0.1.0"

# Export all public APIs
__all__ = [
    # Data models
    "ProjectConfig",
    "FileEntry",
    "SearchMatch",
    "SearchQuery",
    "FileContent",
    "TreeNode",
    # Exceptions
    "MCPError",
    "PathSecurityError",
    "BinaryFileError",
    "SearchTimeoutError",
    "PermissionDeniedError",
]
