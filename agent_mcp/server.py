"""FastMCP server entry point for Context MCP.

Registers all 11 MCP tools and starts the server.
"""
from fastmcp import FastMCP
from agent_mcp.config import load_config
from agent_mcp.utils.logger import setup_logging, logger
from agent_mcp.tools.navigation import list_directory, show_tree, read_project_context
from agent_mcp.tools.search import (
    search_in_file,
    search_in_files,
    find_files_by_name,
    find_recently_modified_files
)
from agent_mcp.tools.read import (
    read_entire_file,
    read_file_lines,
    read_file_tail,
    read_files
)


# Initialize FastMCP server
mcp = FastMCP("context-mcp")


# ============================================================================
# Register Navigation Tools
# ============================================================================

@mcp.tool()
def mcp_list_directory(
    path: str = ".",
    sort_by: str = "name",
    order: str = "asc",
    limit: int = -1
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
    return list_directory(path, sort_by, order, limit)


@mcp.tool()
def mcp_show_tree(path: str = ".", max_depth: int = 3) -> dict:
    """Show directory tree structure.

    Args:
        path: Starting directory path (default: ".")
        max_depth: Maximum depth to traverse, 1-10 (default: 3)

    Returns:
        dict: tree (TreeNode), max_depth_reached (bool)
    """
    return show_tree(path, max_depth)


@mcp.tool()
def mcp_read_project_context() -> dict:
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
    return read_project_context()


# ============================================================================
# Register Search Tools
# ============================================================================

@mcp.tool()
def mcp_search_in_file(
    query: str,
    file_path: str,
    use_regex: bool = False
) -> dict:
    """Search for text in a single file.

    Args:
        query: Search text or regex pattern
        file_path: File path relative to project root
        use_regex: Whether to treat query as regex (default: False)

    Returns:
        dict: matches (list), total_matches (int)
    """
    return search_in_file(query, file_path, use_regex)


@mcp.tool()
def mcp_search_in_files(
    query: str,
    file_pattern: str = "*",
    path: str = ".",
    use_regex: bool = False,
    exclude_query: str = "",
    timeout: int = 60
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
        dict: matches (list), total_matches (int), files_searched (int), timed_out (bool)
    """
    return search_in_files(query, file_pattern, path, use_regex, exclude_query, timeout)


@mcp.tool()
def mcp_find_files_by_name(name_pattern: str, path: str = ".") -> dict:
    """Find files by name pattern (glob).

    Args:
        name_pattern: File name pattern with wildcards (* and ?)
        path: Starting directory (default: ".")

    Returns:
        dict: files (list[str]), total_found (int)
    """
    return find_files_by_name(name_pattern, path)


@mcp.tool()
def mcp_find_recently_modified_files(
    hours_ago: int,
    path: str = ".",
    file_pattern: str = "*"
) -> dict:
    """Find files modified within the last N hours.

    Args:
        hours_ago: Number of hours to look back (minimum: 1)
        path: Starting directory (default: ".")
        file_pattern: File name pattern (default: "*")

    Returns:
        dict: files (list[dict]), total_found (int)
    """
    return find_recently_modified_files(hours_ago, path, file_pattern)


# ============================================================================
# Register Read Tools
# ============================================================================

@mcp.tool()
def mcp_read_entire_file(file_path: str) -> dict:
    """Read complete file content.

    Args:
        file_path: File path relative to project root

    Returns:
        dict: content, encoding, line_count, file_path
    """
    return read_entire_file(file_path)


@mcp.tool()
def mcp_read_file_lines(file_path: str, start_line: int, end_line: int) -> dict:
    """Read specific line range from file.

    Args:
        file_path: File path relative to project root
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)

    Returns:
        dict: content, encoding, line_count, file_path, is_partial, total_lines
    """
    return read_file_lines(file_path, start_line, end_line)


@mcp.tool()
def mcp_read_file_tail(file_path: str, num_lines: int = 10) -> dict:
    """Read last N lines of file.

    Args:
        file_path: File path relative to project root
        num_lines: Number of lines to read from end (default: 10)

    Returns:
        dict: content, encoding, line_count, file_path, is_partial, total_lines
    """
    return read_file_tail(file_path, num_lines)


@mcp.tool()
def mcp_read_files(file_paths: list[str]) -> dict:
    """Batch read multiple files.

    Args:
        file_paths: List of file paths relative to project root

    Returns:
        dict: files (list), success_count (int), error_count (int)
    """
    return read_files(file_paths)


# ============================================================================
# Server Entry Point
# ============================================================================

def main():
    """Main entry point for uvx execution."""
    # Setup logging
    logger_instance = setup_logging()

    try:
        # Load configuration
        cfg = load_config()
        logger_instance.info(f"Context MCP Server starting...")
        logger_instance.info(f"Project root: {cfg.root_path}")
        logger_instance.info(f"Search timeout: {cfg.search_timeout}s")
        logger_instance.info(f"Log retention: {cfg.log_retention_days} days")

        # Run MCP server
        mcp.run()

    except ValueError as e:
        logger_instance.error(f"Configuration error: {e}")
        print(f"ERROR: {e}")
        print("\nPlease set the PROJECT_ROOT environment variable.")
        print("Example: export PROJECT_ROOT=/path/to/your/project")
        return 1
    except Exception as e:
        logger_instance.error(f"Server error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
