"""FastMCP server entry point for Context MCP.

Registers all 11 MCP tools and starts the server.
"""

import logging
from fastmcp import FastMCP
from context_mcp.config import load_config
from context_mcp.utils.logger import setup_logging, logger
from context_mcp.utils.tool_detector import ToolDetector
from context_mcp.tools.navigation import list_directory, show_tree, read_project_context
from context_mcp.tools.search import (
    search_in_file,
    search_in_files,
    find_files_by_name,
    find_recently_modified_files,
)
from context_mcp.tools.read import (
    read_entire_file,
    read_file_lines,
    read_file_tail,
    read_files,
)
# Initialize FastMCP server
mcp = FastMCP("context-mcp")

# Detect high-performance tools on server startup
_detector = ToolDetector()

# Log tool availability
if _detector.has_ripgrep:
    logger.info("ripgrep detected - using high-performance search")
else:
    logger.warning(
        "ripgrep not available, search_in_files will use grep or Python fallback. "
        "For better performance, install ripgrep: https://github.com/BurntSushi/ripgrep#installation"
    )

if _detector.has_fd:
    logger.info("fd detected - using high-performance file finding")
else:
    logger.warning(
        "fd not available, find_files_by_name will use find or Python fallback. "
        "For better performance, install fd: https://github.com/sharkdp/fd#installation"
    )


# ============================================================================
# Register Navigation Tools
# ============================================================================


@mcp.tool()
def list_directory(
    path: str = ".", sort_by: str = "name", order: str = "asc", limit: int = -1
) -> dict:
    """List directory contents with sorting and limiting.

    Args:
        path: Directory path relative to project root (default: ".")
        sort_by: Sort field: name, size, or time (default: "name")
        order: Sort order: asc or desc (default: "asc")
        limit: Maximum entries to return, -1 for unlimited (default: -1)

    Returns:
        dict: entries (list), total (int), truncated (bool)
    """
    from typing import cast, Literal
    from context_mcp.tools.navigation import list_directory as list_dir_impl

    return list_dir_impl(
        path,
        cast(Literal["name", "size", "time"], sort_by),
        cast(Literal["asc", "desc"], order),
        limit,
    )


@mcp.tool()
def show_tree(path: str = ".", max_depth: int = 3) -> dict:
    """Show directory tree structure.

    Args:
        path: Starting directory path (default: ".")
        max_depth: Maximum depth to traverse, 1-10 (default: 3)

    Returns:
        dict: tree (TreeNode), max_depth_reached (bool)
    """
    from context_mcp.tools.navigation import show_tree as show_tree_impl
    return show_tree_impl(path, max_depth)


@mcp.tool()
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
    from context_mcp.tools.navigation import read_project_context as read_ctx_impl
    return read_ctx_impl()


# ============================================================================
# Register Search Tools
# ============================================================================


@mcp.tool()
def search_in_file(query: str, file_path: str, use_regex: bool = False) -> dict:
    """Search for text in a single file.

    Args:
        query: Search text or regex pattern
        file_path: File path relative to project root
        use_regex: Whether to treat query as regex (default: False)

    Returns:
        dict: matches (list), total_matches (int)
    """
    from context_mcp.tools.search import search_in_file as search_file_impl
    return search_file_impl(query, file_path, use_regex)


@mcp.tool()
def search_in_files(
    query: str,
    file_pattern: str = "*",
    path: str = ".",
    use_regex: bool = False,
    exclude_query: str = "",
    timeout: int = 60,
) -> dict:
    """Search for text across multiple files.

    Args:
        query: Search text or regex pattern
        file_pattern: File name glob pattern (default: "*")
        path: Starting directory (default: ".")
        use_regex: Whether to treat query as regex (default: False)
        exclude_query: Exclude matches containing this pattern (default: "")
        timeout: Timeout in seconds (default: 60)

    Returns:
        dict: matches (list), total_matches (int), timed_out (bool)
    """
    from context_mcp.tools.search import search_in_files as search_files_impl
    return search_files_impl(query, file_pattern, path, use_regex, exclude_query, timeout)


@mcp.tool()
def find_files_by_name(name_pattern: str, path: str = ".") -> dict:
    """Find files by name pattern (glob).

    Args:
        name_pattern: File name pattern with wildcards (* and ?)
        path: Starting directory (default: ".")

    Returns:
        dict: files (list[str]), total_found (int)
    """
    from context_mcp.tools.search import find_files_by_name as find_files_impl
    return find_files_impl(name_pattern, path)


@mcp.tool()
def find_recently_modified_files(
    hours_ago: int, path: str = ".", file_pattern: str = "*"
) -> dict:
    """Find files modified within the last N hours.

    Args:
        hours_ago: Number of hours to look back (minimum: 1)
        path: Starting directory (default: ".")
        file_pattern: File name pattern (default: "*")

    Returns:
        dict: files (list[dict]), total_found (int)
    """
    from context_mcp.tools.search import find_recently_modified_files as find_recent_impl
    return find_recent_impl(hours_ago, path, file_pattern)


# ============================================================================
# Register Read Tools
# ============================================================================


@mcp.tool()
def read_entire_file(file_path: str) -> dict:
    """Read complete file content.

    Args:
        file_path: File path relative to project root

    Returns:
        dict: content, encoding, line_count, file_path
    """
    from context_mcp.tools.read import read_entire_file as read_file_impl
    return read_file_impl(file_path)


@mcp.tool()
def read_file_lines(file_path: str, start_line: int, end_line: int) -> dict:
    """Read specific line range from file.

    Args:
        file_path: File path relative to project root
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)

    Returns:
        dict: content, encoding, line_count, file_path, is_partial, total_lines
    """
    from context_mcp.tools.read import read_file_lines as read_lines_impl
    return read_lines_impl(file_path, start_line, end_line)


@mcp.tool()
def read_file_tail(file_path: str, num_lines: int = 10) -> dict:
    """Read last N lines of file.

    Args:
        file_path: File path relative to project root
        num_lines: Number of lines to read from end (default: 10)

    Returns:
        dict: content, encoding, line_count, file_path, is_partial, total_lines
    """
    from context_mcp.tools.read import read_file_tail as read_tail_impl
    return read_tail_impl(file_path, num_lines)


@mcp.tool()
def read_files(file_paths: list[str]) -> dict:
    """Batch read multiple files.

    Args:
        file_paths: List of file paths relative to project root

    Returns:
        dict: files (list), success_count (int), error_count (int)
    """
    from context_mcp.tools.read import read_files as read_files_impl
    return read_files_impl(file_paths)


# ============================================================================
# Register Guide Tools
# ============================================================================


@mcp.tool()
async def get_tool_usage_guide(tool_names: list[str] | None = None) -> dict:
    """Returns comprehensive usage documentation for MCP tools.

    Generates Markdown documentation with JSON Schema definitions, descriptions,
    and usage examples. Supports filtering to specific tools.

    Args:
        tool_names: Optional list of tool names to include. If None, returns all tools.

    Returns:
        dict: content (str), metadata (dict), warnings (list, optional)
    """
    from context_mcp.tools.guide import get_tool_usage_guide as _impl

    return await _impl(mcp, tool_names)


# ============================================================================
# Server Entry Point
# ============================================================================


def main():
    """Main entry point for uvx execution."""
    logger_instance = None
    try:
        # Load configuration first to get log level
        cfg = load_config()

        # Setup logging with configured level and file logging
        logger_instance = setup_logging(level=cfg.log_level, enable_file_log=cfg.enable_file_log)

        logger_instance.info("Context MCP Server starting...")
        logger_instance.info(f"Project root: {cfg.root_path}")
        logger_instance.info(f"Search timeout: {cfg.search_timeout}s")
        logger_instance.info(f"Log retention: {cfg.log_retention_days} days")
        logger_instance.info(f"Log level: {logging.getLevelName(cfg.log_level)}")
        logger_instance.info(f"File logging: {'enabled' if cfg.enable_file_log else 'disabled'}")

        # Run MCP server
        mcp.run()

    except ValueError as e:
        if logger_instance:
            logger_instance.error(f"Configuration error: {e}")
        print(f"ERROR: {e}")
        print("\nPlease set the PROJECT_ROOT environment variable.")
        print("Example: export PROJECT_ROOT=/path/to/your/project")
        return 1
    except Exception as e:
        if logger_instance:
            logger_instance.error(f"Server error: {e}", exc_info=True)
        else:
            print(f"Server error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
