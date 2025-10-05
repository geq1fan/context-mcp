"""
Schema extraction utility for MCP tools.

Extracts input schemas from FastMCP registered tools using runtime reflection.
"""

from typing import Dict, Optional, List, TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - type checking helper
    from fastmcp.tools.tool import FunctionTool
    from fastmcp import FastMCP


async def get_registered_tools(mcp_instance: "FastMCP") -> Dict[str, Any]:
    """
    Return the currently registered FastMCP tools keyed by name.

    Args:
        mcp_instance: FastMCP server instance

    Returns:
        Dict mapping tool names to FunctionTool instances
    """
    return await mcp_instance.get_tools()


async def extract_tool_schemas(
    mcp_instance: "FastMCP",
    tools: Optional[Dict[str, Any]] = None,
) -> Dict[str, dict]:
    """
    Extract input schemas for all registered MCP tools.

    Args:
        mcp_instance: FastMCP server instance
        tools: Optional pre-fetched mapping of tool name to FunctionTool

    Returns:
        Dict mapping tool names to their input schema dictionaries

    Example:
        >>> from context_mcp.server import mcp
        >>> tools = await get_registered_tools(mcp)
        >>> schemas = await extract_tool_schemas(mcp, tools)
        >>> schemas["mcp_list_directory"]["properties"]["path"]
        {'type': 'string', 'description': '...'}
    """
    tools = tools or await get_registered_tools(mcp_instance)
    return {name: tool.parameters for name, tool in tools.items()}


async def extract_tool_schema(
    mcp_instance: "FastMCP",
    tool_name: str,
    tools: Optional[Dict[str, Any]] = None,
) -> Optional[dict]:
    """
    Extract schema for a single tool.

    Args:
        mcp_instance: FastMCP server instance
        tool_name: Name of the tool
        tools: Optional pre-fetched mapping of tool name to FunctionTool

    Returns:
        Input schema dict, or None if tool not found
    """
    tools = tools or await get_registered_tools(mcp_instance)
    tool = tools.get(tool_name)
    return tool.parameters if tool else None


def categorize_tools() -> Dict[str, List[str]]:
    """
    Categorize tools into navigation/search/read/guide groups.

    Returns:
        Dict mapping category names to lists of tool names

    Example:
        >>> cats = categorize_tools()
        >>> cats["navigation"]
        ['list_directory', 'show_tree', 'read_project_context']
    """
    navigation = ["list_directory", "show_tree", "read_project_context"]
    search = [
        "search_in_file",
        "search_in_files",
        "find_files_by_name",
        "find_recently_modified_files",
    ]
    read = [
        "read_entire_file",
        "read_file_lines",
        "read_file_tail",
        "read_files",
    ]
    guide = ["get_tool_usage_guide"]

    return {
        "navigation": navigation,
        "search": search,
        "read": read,
        "guide": guide,
    }


async def get_tool_description_from_mcp(
    mcp_instance: "FastMCP",
    tool_name: str,
    tools: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Get tool description from FastMCP metadata.

    Args:
        mcp_instance: FastMCP server instance
        tool_name: Name of the tool
        tools: Optional pre-fetched mapping of tool name to FunctionTool

    Returns:
        Tool description string
    """
    tools = tools or await get_registered_tools(mcp_instance)
    tool = tools.get(tool_name)
    if tool:
        return tool.description or "[No description]"
    return "[Tool not found]"
