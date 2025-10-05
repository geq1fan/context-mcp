"""
Tool usage guide generator.

MCP tool that returns comprehensive documentation for all registered tools.
"""

from typing import Optional, List, TYPE_CHECKING
import time

from context_mcp.utils.schema_extractor import (
    categorize_tools,
    extract_tool_schemas,
    get_registered_tools,
)
from context_mcp.utils.doc_generator import render_document, calculate_doc_size

if TYPE_CHECKING:  # pragma: no cover - type checking helper
    from fastmcp import FastMCP
    from fastmcp.tools.tool import FunctionTool


def _validate_and_filter_tools(
    tool_names: Optional[List[str]], all_schemas: dict
) -> tuple[set, list, list]:
    """
    Validate requested tool names and filter to valid ones.

    Supports both prefixed (mcp_*) and unprefixed tool names.

    Args:
        tool_names: Optional list of requested tool names
        all_schemas: Dict of all available tool schemas

    Returns:
        Tuple of (tools_to_include, warnings, invalid_names)
    """
    if tool_names is None:
        return set(all_schemas.keys()), [], []

    valid_names = set(all_schemas.keys())

    # Normalize tool names: add mcp_ prefix if missing
    normalized_requested = set()
    for name in tool_names:
        if name in valid_names:
            normalized_requested.add(name)
        elif f"mcp_{name}" in valid_names:
            normalized_requested.add(f"mcp_{name}")
        else:
            normalized_requested.add(name)  # Keep original for error reporting

    invalid = normalized_requested - valid_names

    warnings = []
    invalid_names = []

    if invalid:
        invalid_names = sorted(invalid)
        tool_word = "Tools" if len(invalid) > 1 else "Tool"
        invalid_quoted = ", ".join(f"'{n}'" for n in invalid)
        warnings.append(
            f"{tool_word} {invalid_quoted} "
            f"not found. Available tools: {', '.join(sorted(valid_names))}"
        )

    tools_to_include = normalized_requested & valid_names
    return tools_to_include, warnings, invalid_names


def _build_tools_metadata(
    tools_to_include: set,
    categories: dict,
    all_schemas: dict,
    all_tools: dict["str", "FunctionTool"],
) -> dict:
    """
    Build tool metadata organized by category.

    Args:
        tools_to_include: Set of tool names to include (with mcp_ prefix)
        categories: Dict mapping category names to tool lists
        all_schemas: Dict of all tool schemas
        all_tools: Dict of all FunctionTool instances

    Returns:
        Dict mapping category names to lists of tool metadata
    """
    tools_by_category = {}

    for category, tool_list in categories.items():
        category_tools = []
        for tool_name in tool_list:
            if tool_name in tools_to_include:
                # Remove mcp_ prefix for user-friendly display
                display_name = tool_name.removeprefix("mcp_")

                # Get description from FastMCP tool instance
                tool = all_tools.get(tool_name)
                description = (
                    tool.description
                    if tool and tool.description
                    else "[No description]"
                )

                tool_meta = {
                    "name": display_name,
                    "description": description,
                    "input_schema": all_schemas[tool_name],
                    "examples": [],  # Examples can be added later if needed
                    "return_format": None,
                }
                category_tools.append(tool_meta)

        if category_tools:
            tools_by_category[category] = category_tools

    return tools_by_category


async def get_tool_usage_guide(
    mcp_instance: "FastMCP", tool_names: Optional[List[str]] = None
) -> dict:
    """
    Returns comprehensive usage documentation for MCP tools.

    Generates Markdown documentation with JSON Schema definitions, descriptions,
    and usage examples. Supports filtering to specific tools.

    Args:
        mcp_instance: FastMCP server instance
        tool_names: Optional list of tool names to include. If None, returns all tools.

    Returns:
        Dictionary with:
        - content: Markdown documentation string
        - metadata: Dict with total_tools, filtered_count, generation_time_ms
        - warnings: List of warning messages (if any invalid tool names)

    Example:
        >>> from context_mcp.server import mcp
        >>> guide = await get_tool_usage_guide(mcp)
        >>> print(guide["content"][:50])
        # Context MCP Tools Usage Guide

        >>> guide = await get_tool_usage_guide(mcp, tool_names=["list_directory"])
        >>> guide["metadata"]["filtered_count"]
        1
    """
    start_time = time.time()

    # Extract schemas and categories
    tools = await get_registered_tools(mcp_instance)
    all_schemas = await extract_tool_schemas(mcp_instance, tools)
    categories = categorize_tools()

    # Validate and filter tool names
    tools_to_include, warnings, invalid_names = _validate_and_filter_tools(
        tool_names, all_schemas
    )

    # Build tool metadata by category
    tools_by_category = _build_tools_metadata(
        tools_to_include, categories, all_schemas, tools
    )

    # Render document
    filter_applied = tool_names is not None
    filtered_tools_str = ", ".join(sorted(tools_to_include)) if filter_applied else ""
    total_included = sum(len(tools) for tools in tools_by_category.values())

    content = render_document(
        tools_by_category=tools_by_category,
        total_tools=len(all_schemas),
        filtered_count=total_included,
        filter_applied=filter_applied,
        filtered_tools=filtered_tools_str,
    )

    # Calculate metrics and build response
    generation_time_ms = (time.time() - start_time) * 1000
    doc_size = calculate_doc_size(content)

    response = {
        "content": content,
        "metadata": {
            "total_tools": len(all_schemas),
            "filtered_count": total_included,
            "generation_time_ms": round(generation_time_ms, 2),
            "document_size_bytes": doc_size,
        },
    }

    if invalid_names:
        response["metadata"]["invalid_names"] = invalid_names

    if warnings:
        response["warnings"] = warnings

    return response
