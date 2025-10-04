import pytest
from unittest.mock import Mock, patch
from context_mcp.server import mcp


@pytest.mark.asyncio
async def test_extract_all_tool_schemas():
    """Test extracting schemas from all registered tools"""
    from context_mcp.utils.schema_extractor import extract_tool_schemas

    schemas = await extract_tool_schemas(mcp)

    assert isinstance(schemas, dict)
    assert len(schemas) >= 11  # At least 11 existing tools
    assert "mcp_list_directory" in schemas
    assert schemas["mcp_list_directory"]["type"] == "object"
    assert "properties" in schemas["mcp_list_directory"]


@pytest.mark.asyncio
async def test_extract_single_tool_schema():
    """Test extracting schema for a specific tool"""
    from context_mcp.utils.schema_extractor import extract_tool_schema

    schema = await extract_tool_schema(mcp, "mcp_list_directory")

    assert schema is not None
    assert schema["type"] == "object"
    assert "path" in schema["properties"]


@pytest.mark.asyncio
async def test_extract_nonexistent_tool():
    """Test handling of non-existent tool"""
    from context_mcp.utils.schema_extractor import extract_tool_schema

    schema = await extract_tool_schema(mcp, "nonexistent_tool_xyz")

    assert schema is None  # or raises ToolNotFoundError


def test_categorize_tools():
    """Test automatic categorization of tools"""
    from context_mcp.utils.schema_extractor import categorize_tools

    categories = categorize_tools()

    assert "navigation" in categories
    assert "search" in categories
    assert "read" in categories
    assert "guide" in categories

    # Tool names have mcp_ prefix
    assert "mcp_list_directory" in categories["navigation"]
    assert "mcp_search_in_files" in categories["search"]


@pytest.mark.asyncio
async def test_get_tool_description():
    """Test getting tool description from FastMCP"""
    from context_mcp.utils.schema_extractor import get_tool_description_from_mcp

    description = await get_tool_description_from_mcp(mcp, "mcp_list_directory")

    assert isinstance(description, str)
    assert len(description) > 0
    assert description != "[Tool not found]"


@pytest.mark.asyncio
async def test_get_nonexistent_tool_description():
    """Test getting description for non-existent tool"""
    from context_mcp.utils.schema_extractor import get_tool_description_from_mcp

    description = await get_tool_description_from_mcp(mcp, "nonexistent_tool_xyz")

    assert description == "[Tool not found]"
