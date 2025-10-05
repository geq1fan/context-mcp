

def test_generate_tool_section():
    """Test generating Markdown section for a single tool"""
    from context_mcp.utils.doc_generator import generate_tool_section

    tool_metadata = {
        "name": "test_tool",
        "description": "Test description",
        "input_schema": {"type": "object", "properties": {}},
        "examples": ["test_tool(param=1)"],
        "return_format": "Test return"
    }

    section = generate_tool_section(tool_metadata)

    assert "### test_tool" in section
    assert "Test description" in section
    assert "```json" in section
    assert "```python" in section
    assert "test_tool(param=1)" in section


def test_generate_category_section():
    """Test generating section for a tool category"""
    from context_mcp.utils.doc_generator import generate_category_section

    tools = [
        {"name": "tool1", "description": "Desc1", "input_schema": {}, "examples": []},
        {"name": "tool2", "description": "Desc2", "input_schema": {}, "examples": []}
    ]

    section = generate_category_section("Test Category", tools)

    assert "## Test Category Tools (2)" in section
    assert "### tool1" in section
    assert "### tool2" in section


def test_render_full_document():
    """Test rendering complete document using template"""
    from context_mcp.utils.doc_generator import render_document

    tools_by_category = {
        "navigation": [{"name": "nav1", "description": "Nav tool", "input_schema": {}, "examples": []}],
        "search": [{"name": "search1", "description": "Search tool", "input_schema": {}, "examples": []}]
    }

    doc = render_document(tools_by_category, total_tools=2, filtered_count=2)

    assert doc.startswith("# Context MCP Tools Usage Guide")
    assert "## Navigation Tools (1)" in doc or "## navigation Tools (1)" in doc
    assert "## Search Tools (1)" in doc or "## search Tools (1)" in doc


def test_document_size_calculation():
    """Test calculating document size in bytes"""
    from context_mcp.utils.doc_generator import calculate_doc_size

    content = "Test document content"
    size = calculate_doc_size(content)

    assert size == len(content.encode('utf-8'))
    assert isinstance(size, int)


def test_jinja2_template_loading():
    """Test Jinja2 template is loaded correctly"""
    from context_mcp.utils.doc_generator import load_template

    template = load_template()

    assert template is not None
    # Render with sample data
    result = template.render(
        generation_date="2025-10-04",
        tool_count=1,
        tools_by_category={}
    )
    assert "Context MCP Tools Usage Guide" in result
