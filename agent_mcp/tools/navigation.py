"""Navigation tools: list_directory and show_tree.

Provides directory listing and tree visualization capabilities.
"""
import os
import subprocess
from pathlib import Path
from typing import Literal, Optional
from agent_mcp.config import config
from agent_mcp.validators.path_validator import PathValidator
from agent_mcp import FileEntry, TreeNode
from agent_mcp.utils.logger import logger


# Initialize path validator with project root
if config:
    validator = PathValidator(config.root_path)
else:
    validator = None


def list_directory(
    path: str = ".",
    sort_by: Literal["name", "size", "time"] = "name",
    order: Literal["asc", "desc"] = "asc",
    limit: int = -1
) -> dict:
    """List directory contents with sorting and limiting.

    Args:
        path: Directory path relative to project root
        sort_by: Sort field (name, size, time)
        order: Sort order (asc, desc)
        limit: Maximum entries to return (-1 = unlimited)

    Returns:
        dict with keys: entries (list[FileEntry]), total (int), truncated (bool)

    Raises:
        PathSecurityError: If path is outside project root
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory cannot be accessed
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"list_directory: path={path}, sort_by={sort_by}, order={order}, limit={limit}")

    # Validate path
    abs_path = validator.validate(path)

    # Check directory exists
    if not abs_path.exists():
        raise FileNotFoundError(f"PATH_NOT_FOUND: Directory does not exist: {path}")

    if not abs_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    # List directory contents
    entries = []
    try:
        for item in abs_path.iterdir():
            stat = item.stat()
            entry = FileEntry(
                name=item.name,
                type="dir" if item.is_dir() else "file",
                size=stat.st_size if item.is_file() else 0,
                mtime=stat.st_mtime,
                path=str(item.relative_to(config.root_path))
            )
            entries.append(entry)
    except PermissionError as e:
        raise PermissionError(f"PERMISSION_DENIED: Cannot list directory: {path}") from e

    # Sort entries
    if sort_by == "name":
        entries.sort(key=lambda e: e.name, reverse=(order == "desc"))
    elif sort_by == "size":
        entries.sort(key=lambda e: e.size, reverse=(order == "desc"))
    elif sort_by == "time":
        entries.sort(key=lambda e: e.mtime, reverse=(order == "desc"))

    # Apply limit
    total = len(entries)
    truncated = False
    if limit > 0 and len(entries) > limit:
        entries = entries[:limit]
        truncated = True

    return {
        "entries": [
            {
                "name": e.name,
                "type": e.type,
                "size": e.size,
                "mtime": e.mtime,
                "path": e.path
            }
            for e in entries
        ],
        "total": total,
        "truncated": truncated
    }


def show_tree(
    path: str = ".",
    max_depth: int = 3
) -> dict:
    """Show directory tree structure.

    Args:
        path: Starting directory path relative to project root
        max_depth: Maximum depth to traverse (1-10)

    Returns:
        dict with keys: tree (TreeNode), max_depth_reached (bool)

    Raises:
        PathSecurityError: If path is outside project root
        FileNotFoundError: If directory doesn't exist
    """
    if not validator:
        raise RuntimeError("Configuration not loaded")

    logger.info(f"show_tree: path={path}, max_depth={max_depth}")

    # Validate inputs
    if max_depth < 1 or max_depth > 10:
        raise ValueError("max_depth must be between 1 and 10")

    # Validate path
    abs_path = validator.validate(path)

    if not abs_path.exists():
        raise FileNotFoundError(f"PATH_NOT_FOUND: Directory does not exist: {path}")

    if not abs_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    # Build tree recursively
    max_depth_reached = False

    def build_tree_node(current_path: Path, current_depth: int) -> dict:
        nonlocal max_depth_reached

        node = {
            "name": current_path.name if current_path != abs_path else ".",
            "type": "dir" if current_path.is_dir() else "file",
            "depth": current_depth
        }

        # Add children if directory and not at max depth
        if current_path.is_dir() and current_depth < max_depth:
            children = []
            try:
                for item in sorted(current_path.iterdir(), key=lambda p: p.name):
                    child_node = build_tree_node(item, current_depth + 1)
                    children.append(child_node)
            except PermissionError:
                pass  # Skip inaccessible directories

            if children:
                node["children"] = children
        elif current_path.is_dir() and current_depth >= max_depth:
            max_depth_reached = True

        return node

    tree = build_tree_node(abs_path, 0)

    return {
        "tree": tree,
        "max_depth_reached": max_depth_reached
    }


def _discover_context_file(filename: str, project_root: Path) -> dict:
    """Discover and read a single context file.

    Args:
        filename: Name of the context file (AGENTS.md or CLAUDE.md)
        project_root: Project root directory path

    Returns:
        dict with keys: filename, exists, readable, size_bytes, content, error
    """
    file_path = project_root / filename

    # Initialize result
    result = {
        "filename": filename,
        "exists": False,
        "readable": False,
        "size_bytes": None,
        "content": None,
        "error": None
    }

    # Check if file exists
    if not file_path.exists():
        return result

    result["exists"] = True

    # Validate path security
    try:
        validator = PathValidator(project_root)
        validator.validate(file_path)
    except Exception as e:
        result["readable"] = False
        result["error"] = str(e)
        return result

    # Try to read file
    try:
        # Get file size
        size_bytes = file_path.stat().st_size

        # Log warning for large files (>1MB)
        if size_bytes > 1024 * 1024:
            size_mb = size_bytes / (1024 * 1024)
            logger.warning(f"Context file {filename} is large ({size_mb:.1f} MB)")

        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Only set size_bytes and content if read succeeded
        result["size_bytes"] = size_bytes
        result["content"] = content
        result["readable"] = True

    except PermissionError as e:
        result["readable"] = False
        result["error"] = f"Permission denied: {e}"

    except UnicodeDecodeError as e:
        result["readable"] = False
        result["error"] = f"Invalid UTF-8 encoding: {e}"

    except Exception as e:
        result["readable"] = False
        result["error"] = f"Read error: {e}"

    return result


def _generate_response(files: list[dict]) -> dict:
    """Generate response from discovered context files.

    Args:
        files: List of context file dictionaries from _discover_context_file

    Returns:
        dict with keys: files, message, total_found
    """
    # Calculate total found (exists AND readable)
    total_found = sum(1 for f in files if f["exists"] and f["readable"])

    # Generate message based on results
    num_files = len(files)
    if total_found == 0:
        # Check if any exist but not readable
        exists_not_readable = any(f["exists"] and not f["readable"] for f in files)
        if exists_not_readable:
            count = sum(1 for f in files if f["exists"] and not f["readable"])
            message = f"Found 0 of {num_files} context files ({count} exists but not readable)"
        else:
            message = "No context files found in PROJECT_ROOT"
    else:
        message = f"Found {total_found} of {num_files} context files"

    return {
        "files": files,
        "message": message,
        "total_found": total_found
    }


def read_project_context() -> dict:
    """Read project context files (AGENTS.md, CLAUDE.md) from PROJECT_ROOT.

    Discovers and reads AI agent context files to understand project-specific
    conventions, coding standards, and behavioral guidelines.

    Returns:
        dict: {
            "files": List[dict],    # Context file metadata and content
            "message": str,          # Human-readable result summary
            "total_found": int       # Count of readable files
        }

    Raises:
        RuntimeError: If PROJECT_ROOT is not set or invalid
    """
    # Get project root from config
    from agent_mcp.config import config as cfg

    if not cfg or not cfg.root_path:
        raise RuntimeError("PROJECT_ROOT is not configured")

    logger.info("read_project_context: Discovering context files")

    project_root = cfg.root_path

    # Discover files in priority order
    context_filenames = ["AGENTS.md", "CLAUDE.md"]
    files = []

    for filename in context_filenames:
        file_result = _discover_context_file(filename, project_root)
        files.append(file_result)

    # Generate and return response
    response = _generate_response(files)

    logger.info(
        f"read_project_context: Found {response['total_found']} of {len(context_filenames)} files"
    )

    return response
