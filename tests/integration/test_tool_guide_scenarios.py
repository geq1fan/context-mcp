import pytest
from context_mcp.server import mcp


@pytest.mark.asyncio
async def test_all_tools_documentation():
    """Scenario: Get complete documentation for all 12 tools"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(mcp)

    # Verify all categories present
    assert (
        "## Navigation Tools" in response["content"]
        or "## navigation Tools" in response["content"]
    )
    assert (
        "## Search Tools" in response["content"]
        or "## search Tools" in response["content"]
    )
    assert (
        "## Read Tools" in response["content"] or "## read Tools" in response["content"]
    )
    assert (
        "## Guide Tools" in response["content"]
        or "## guide Tools" in response["content"]
    )

    # Verify all 12 tools mentioned
    all_tools = [
        "list_directory",
        "show_tree",
        "read_project_context",
        "search_in_file",
        "search_in_files",
        "find_files_by_name",
        "find_recently_modified_files",
        "read_entire_file",
        "read_file_lines",
        "read_file_tail",
        "read_files",
        "get_tool_usage_guide",
    ]
    for tool in all_tools:
        assert f"### {tool}" in response["content"]

    # Verify metadata
    assert response["metadata"]["total_tools"] == 12
    assert response["metadata"]["filtered_count"] == 12
    assert len(response.get("warnings", [])) == 0


@pytest.mark.asyncio
async def test_filtered_tools():
    """Scenario: Filter to 2 specific tools"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(
        mcp, tool_names=["list_directory", "read_entire_file"]
    )

    assert "list_directory" in response["content"]
    assert "read_entire_file" in response["content"]
    assert "search_in_files" not in response["content"]
    assert response["metadata"]["filtered_count"] == 2


@pytest.mark.asyncio
async def test_invalid_tool_names_graceful_degradation():
    """Scenario: Handle invalid tool names without breaking"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(
        mcp, tool_names=["list_directory", "fake_tool_123", "read_entire_file"]
    )

    # Valid tools should be included
    assert "list_directory" in response["content"]
    assert "read_entire_file" in response["content"]

    # Invalid tool should be in warnings
    assert len(response["warnings"]) == 1
    assert "fake_tool_123" in response["warnings"][0]
    assert "not found" in response["warnings"][0].lower()

    # Metadata should reflect filtering
    assert response["metadata"]["filtered_count"] == 2
    assert "fake_tool_123" in response["metadata"]["invalid_names"]


@pytest.mark.asyncio
async def test_schema_accuracy():
    """Scenario: Verify Schema matches actual tool definition"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(mcp, tool_names=["list_directory"])

    # Extract schema from guide (crude parsing for test)
    content = response["content"]
    schema_start = content.find("```json")
    schema_end = content.find("```", schema_start + 7)
    schema_text = content[schema_start + 7 : schema_end].strip()

    # Verify schema contains expected fields
    assert '"path"' in schema_text
    assert '"sort_by"' in schema_text
    assert '"limit"' in schema_text


@pytest.mark.asyncio
async def test_performance_benchmark():
    """Scenario: Document generation completes under 100ms"""
    import time
    from context_mcp.tools.guide import get_tool_usage_guide

    start = time.time()
    response = await get_tool_usage_guide(mcp)
    elapsed_ms = (time.time() - start) * 1000

    assert elapsed_ms < 100, f"Generation took {elapsed_ms:.2f}ms (target: <100ms)"
    assert response["metadata"]["generation_time_ms"] < 100


@pytest.mark.asyncio
async def test_markdown_validity():
    """Scenario: Generated Markdown is valid CommonMark"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(mcp)
    content = response["content"]

    # Basic Markdown validation
    assert content.startswith("#")
    assert "```" in content  # Code blocks present

    # No unclosed code blocks
    code_block_count = content.count("```")
    assert code_block_count % 2 == 0, "Unclosed code block detected"


@pytest.mark.asyncio
async def test_document_size_constraint():
    """Scenario: Document stays under 50KB limit"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = await get_tool_usage_guide(mcp)
    size_bytes = len(response["content"].encode("utf-8"))

    assert size_bytes < 50 * 1024, f"Document is {size_bytes} bytes (limit: 50KB)"


