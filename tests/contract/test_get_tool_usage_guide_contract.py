import pytest
import json
from pathlib import Path
import asyncio
from context_mcp.tools.guide import get_tool_usage_guide
from context_mcp.server import mcp

CONTRACT_PATH = Path("specs/004-tool-tool-prompt/contracts/get_tool_usage_guide.json")


@pytest.fixture
def contract():
    with open(CONTRACT_PATH) as f:
        return json.load(f)


def run_guide(**kwargs):
    return asyncio.run(get_tool_usage_guide(mcp, **kwargs))


def test_tool_registration(contract):
    """Verify get_tool_usage_guide is registered with correct schema"""
    from context_mcp.server import mcp

    # Use async API correctly
    # mcp.get_tools() returns Dict[str, FunctionTool]
    tools_dict = asyncio.run(mcp.get_tools())

    assert "get_tool_usage_guide" in tools_dict

    tool = tools_dict["get_tool_usage_guide"]

    # Validate input schema structure (FunctionTool uses .parameters not .inputSchema)
    assert tool.parameters["type"] == "object"
    assert "tool_names" in tool.parameters["properties"]
    # Optional[List[str]] generates anyOf schema
    tool_names_schema = tool.parameters["properties"]["tool_names"]
    assert "anyOf" in tool_names_schema or "type" in tool_names_schema


def test_response_schema(contract):
    """Verify response matches contract schema"""

    # Test scenario 1: No parameters (all tools)
    response = run_guide()

    # Validate response structure
    assert "content" in response
    assert "metadata" in response
    assert response["content"].startswith("# Context MCP Tools Usage Guide")
    assert response["metadata"]["total_tools"] >= 11
    assert response["metadata"]["filtered_count"] >= 11


def test_scenario_filter_tools(contract):
    """Test filtering specific tools"""

    response = run_guide(tool_names=["list_directory", "read_entire_file"])

    assert "list_directory" in response["content"]
    assert "read_entire_file" in response["content"]
    assert "search_in_files" not in response["content"]
    assert response["metadata"]["filtered_count"] == 2


def test_scenario_invalid_tool_names(contract):
    """Test handling of invalid tool names"""

    response = run_guide(
        tool_names=["list_directory", "nonexistent_tool", "read_entire_file"]
    )

    assert "warnings" in response
    assert len(response["warnings"]) == 1
    assert "nonexistent_tool" in response["warnings"][0]
    assert response["metadata"]["filtered_count"] == 2
    assert response["metadata"]["invalid_names"] == ["nonexistent_tool"]


def test_scenario_json_schema_in_output(contract):
    """Verify JSON Schema blocks are present in output"""

    response = run_guide(tool_names=["list_directory"])

    assert "```json" in response["content"]
    assert '"type": "object"' in response["content"]
    assert '"properties":' in response["content"]


def test_scenario_examples_in_output(contract):
    """Verify usage examples section (currently empty, may be populated later)"""

    response = run_guide(tool_names=["search_in_files"])

    # Examples are currently empty ([]), so we just verify the response is valid
    assert "content" in response
    assert "search_in_files" in response["content"]
    # TODO: Add example generation from schema in future iteration
