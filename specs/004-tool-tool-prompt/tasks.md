# Tasks: Tool Usage Guide Tool

**Feature**: 004-tool-tool-prompt
**Input**: Design documents from `C:\Users\Ge\Documents\github\context-mcp\specs\004-tool-tool-prompt\`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, FastMCP, inspect, pathlib, PyYAML, Jinja2
   → Structure: Single project (context_mcp/ + tests/)
2. Load design documents:
   → data-model.md: 6 entities (ToolMetadata, ToolSchema, etc.)
   → contracts/: get_tool_usage_guide.json (1 contract)
   → research.md: 6 technical decisions
   → quickstart.md: 10 validation steps
3. Generate tasks by category:
   → Setup: YAML data files, Jinja2 template
   → Tests: 1 contract test, 1 integration test, 2 unit tests
   → Core: schema_extractor, doc_generator, guide tool
   → Integration: server.py registration
   → Polish: quickstart validation, performance test
4. Apply TDD: All tests before implementation
5. Mark [P] for independent files
6. Number tasks T001-T014
7. Generate dependency graph
✓ Validation: All entities/contracts covered
```

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- All paths relative to repository root: `C:\Users\Ge\Documents\github\context-mcp\`

---

## Phase 3.1: Setup & Data Preparation

### T001 [X] [P] [X] [X] Create YAML data directory and template files
**File**: `context_mcp/data/tool_descriptions.yaml`, `context_mcp/data/tool_examples.yaml`

**Action**:
1. Create directory: `mkdir -p context_mcp/data/`
2. Create `tool_descriptions.yaml` with 12 tool entries (placeholders for now):
```yaml
list_directory: |
  [Description pending - to be filled in T002]
show_tree: |
  [Description pending]
read_project_context: |
  [Description pending]
# ... (9 more tools)
get_tool_usage_guide: |
  [Description pending]
```
3. Create `tool_examples.yaml` with same 12 tool entries:
```yaml
list_directory:
  - |
    # Example pending
    list_directory(path=".")
# ... (11 more tools)
```

**Success Criteria**:
- Both YAML files exist and parse without errors (`yaml.safe_load()`)
- Each file contains exactly 12 top-level keys matching MCP tool names
- No syntax errors when running `python -c "import yaml; yaml.safe_load(open('context_mcp/data/tool_descriptions.yaml'))"`

**Dependencies**: None

---

### T002 [X] [P] [X] Populate tool_descriptions.yaml with actual descriptions
**File**: `context_mcp/data/tool_descriptions.yaml`

**Action**:
填充11个现有工具的详细描述(每个20-500字符,参考现有工具的docstrings):

```yaml
list_directory: |
  列出指定目录下的所有文件和子目录。
  支持按名称(name)或修改时间(mtime)排序,可限制返回数量。
  常用于项目结构探索和文件导航。

search_in_files: |
  在多个文件中递归搜索匹配的文本模式。
  支持正则表达式、忽略大小写、排除路径。
  优先使用ripgrep(13x faster),回退grep保证兼容性。

# ... (继续填充其余10个工具)

get_tool_usage_guide: |
  返回所有MCP工具的详细使用文档,包含参数Schema、描述和示例。
  支持通过tool_names数组过滤特定工具。
  文档采用Markdown+JSON Schema混合格式,优化LLM理解。
```

**Success Criteria**:
- 所有12个工具都有实际描述(无`[Description pending]`)
- 每个描述长度在20-500字符之间
- 描述清晰说明工具用途、关键参数、使用场景
- YAML格式有效,无语法错误

**Dependencies**: T001

---

### T003 [X] [P] [X] Populate tool_examples.yaml with code examples
**File**: `context_mcp/data/tool_examples.yaml`

**Action**:
为每个工具提供1-3个实际使用示例(参考contracts/中的测试场景):

```yaml
list_directory:
  - |
    # 列出当前目录,按修改时间排序
    list_directory(path=".", sort_by="mtime", limit=10)
  - |
    # 列出src/目录
    list_directory(path="src")

search_in_files:
  - |
    # 在Python文件中搜索"class"关键字
    search_in_files(pattern="class ", include_pattern="*.py")
  - |
    # 搜索TODO注释,忽略大小写
    search_in_files(pattern="todo", case_sensitive=False)

# ... (继续其余10个工具)

get_tool_usage_guide:
  - |
    # 获取所有工具的文档
    get_tool_usage_guide()
  - |
    # 仅获取导航工具的文档
    get_tool_usage_guide(tool_names=["list_directory", "show_tree"])
```

**Success Criteria**:
- 所有12个工具都有至少1个示例
- 示例代码是有效的Python语法
- 示例参数与工具的实际input_schema匹配
- 每个示例包含注释说明用途

**Dependencies**: T001

---

### T004 [X] [P] [X] Create Jinja2 documentation template
**File**: `context_mcp/templates/tool_guide.md.j2`

**Action**:
创建Markdown模板文件,用于渲染工具文档:

```jinja2
# Context MCP Tools Usage Guide

Generated: {{ generation_date }} | Tools: {{ tool_count }}{% if filter_applied %} | Filter: {{ filtered_tools }}{% endif %}

{% for category, tools in tools_by_category.items() %}
## {{ category }} Tools ({{ tools|length }})

{% for tool in tools %}
### {{ tool.name }}
**Purpose**: {{ tool.description }}

**Parameters**:
```json
{{ tool.input_schema | tojson(indent=2) }}
```

{% if tool.examples %}
**Examples**:
{% for example in tool.examples %}
```python
{{ example }}
```
{% endfor %}
{% endif %}

{% if tool.return_format %}
**Returns**: {{ tool.return_format }}
{% endif %}

---
{% endfor %}
{% endfor %}
```

**Success Criteria**:
- 模板文件存在于`context_mcp/templates/`目录
- Jinja2语法有效(可用`jinja2.Template()`解析)
- 模板包含所有必需字段:工具名、描述、参数Schema、示例、返回值
- 支持分类展示(Navigation/Search/Read/Guide)

**Dependencies**: None

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### T005 [X] [P] [X] Contract test for get_tool_usage_guide
**File**: `tests/contract/test_get_tool_usage_guide_contract.py`

**Action**:
基于`contracts/get_tool_usage_guide.json`创建契约测试:

```python
import pytest
from jsonschema import validate, ValidationError
import json

CONTRACT_PATH = "specs/004-tool-tool-prompt/contracts/get_tool_usage_guide.json"

@pytest.fixture
def contract():
    with open(CONTRACT_PATH) as f:
        return json.load(f)

def test_tool_registration(contract):
    """Verify get_tool_usage_guide is registered with correct schema"""
    from context_mcp.server import mcp

    tools = {t.name: t for t in mcp.list_tools()}
    assert "get_tool_usage_guide" in tools

    tool = tools["get_tool_usage_guide"]
    expected_schema = contract["tool"]["inputSchema"]

    # Validate input schema structure
    assert tool.input_schema["type"] == "object"
    assert "tool_names" in tool.input_schema["properties"]
    assert tool.input_schema["properties"]["tool_names"]["type"] == "array"

def test_response_schema(contract):
    """Verify response matches contract schema"""
    from context_mcp.tools.guide import get_tool_usage_guide

    # Test scenario 1: No parameters (all tools)
    response = get_tool_usage_guide()

    # Validate response structure
    assert "content" in response
    assert "metadata" in response
    assert response["content"].startswith("# Context MCP Tools Usage Guide")
    assert response["metadata"]["total_tools"] >= 11
    assert response["metadata"]["filtered_count"] >= 11

def test_scenario_filter_tools(contract):
    """Test filtering specific tools"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(tool_names=["list_directory", "read_entire_file"])

    assert "list_directory" in response["content"]
    assert "read_entire_file" in response["content"]
    assert "search_in_files" not in response["content"]
    assert response["metadata"]["filtered_count"] == 2

def test_scenario_invalid_tool_names(contract):
    """Test handling of invalid tool names"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(
        tool_names=["list_directory", "nonexistent_tool", "read_entire_file"]
    )

    assert "warnings" in response
    assert len(response["warnings"]) == 1
    assert "nonexistent_tool" in response["warnings"][0]
    assert response["metadata"]["filtered_count"] == 2
    assert response["metadata"]["invalid_names"] == ["nonexistent_tool"]

def test_scenario_json_schema_in_output(contract):
    """Verify JSON Schema blocks are present in output"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(tool_names=["list_directory"])

    assert "```json" in response["content"]
    assert '"type": "object"' in response["content"]
    assert '"properties":' in response["content"]

def test_scenario_examples_in_output(contract):
    """Verify usage examples are present"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(tool_names=["search_in_files"])

    assert "**Example**:" in response["content"] or "**Examples**:" in response["content"]
    assert "```python" in response["content"]
    assert "search_in_files(" in response["content"]
```

**Success Criteria**:
- Test file exists in `tests/contract/`
- All 6 test functions are defined
- Tests FAIL initially (implementation does not exist yet)
- Running `pytest tests/contract/test_get_tool_usage_guide_contract.py` shows 6 failures

**Dependencies**: T001, T002, T003

---

### T006 [X] [P] [X] Integration test for tool guide scenarios
**File**: `tests/integration/test_tool_guide_scenarios.py`

**Action**:
基于`quickstart.md`的acceptance scenarios创建集成测试:

```python
import pytest
from context_mcp.server import mcp

def test_all_tools_documentation():
    """Scenario: Get complete documentation for all 12 tools"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide()

    # Verify all categories present
    assert "## Navigation Tools" in response["content"]
    assert "## Search Tools" in response["content"]
    assert "## Read Tools" in response["content"]
    assert "## Guide Tools" in response["content"]  # New category

    # Verify all 12 tools mentioned
    all_tools = [
        "list_directory", "show_tree", "read_project_context",
        "search_in_file", "search_in_files", "find_files_by_name",
        "find_recently_modified_files",
        "read_entire_file", "read_file_lines", "read_file_tail", "read_files",
        "get_tool_usage_guide"
    ]
    for tool in all_tools:
        assert f"### {tool}" in response["content"]

    # Verify metadata
    assert response["metadata"]["total_tools"] == 12
    assert response["metadata"]["filtered_count"] == 12
    assert len(response.get("warnings", [])) == 0

def test_filtered_tools():
    """Scenario: Filter to 2 specific tools"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(tool_names=["list_directory", "read_entire_file"])

    assert "list_directory" in response["content"]
    assert "read_entire_file" in response["content"]
    assert "search_in_files" not in response["content"]
    assert response["metadata"]["filtered_count"] == 2

def test_invalid_tool_names_graceful_degradation():
    """Scenario: Handle invalid tool names without breaking"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(
        tool_names=["list_directory", "fake_tool_123", "read_entire_file"]
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

def test_schema_accuracy():
    """Scenario: Verify Schema matches actual tool definition"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide(tool_names=["list_directory"])

    # Extract schema from guide (crude parsing for test)
    content = response["content"]
    schema_start = content.find("```json")
    schema_end = content.find("```", schema_start + 7)
    schema_text = content[schema_start+7:schema_end].strip()

    # Verify schema contains expected fields
    assert '"path"' in schema_text
    assert '"sort_by"' in schema_text
    assert '"limit"' in schema_text

def test_performance_benchmark():
    """Scenario: Document generation completes under 100ms"""
    import time
    from context_mcp.tools.guide import get_tool_usage_guide

    start = time.time()
    response = get_tool_usage_guide()
    elapsed_ms = (time.time() - start) * 1000

    assert elapsed_ms < 100, f"Generation took {elapsed_ms:.2f}ms (target: <100ms)"
    assert response["metadata"]["generation_time_ms"] < 100

def test_markdown_validity():
    """Scenario: Generated Markdown is valid CommonMark"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide()
    content = response["content"]

    # Basic Markdown validation
    assert content.startswith("#")
    assert "```" in content  # Code blocks present
    assert content.count("```json") == content.count("```python")  # Balanced

    # No unclosed code blocks
    code_block_count = content.count("```")
    assert code_block_count % 2 == 0, "Unclosed code block detected"

def test_document_size_constraint():
    """Scenario: Document stays under 50KB limit"""
    from context_mcp.tools.guide import get_tool_usage_guide

    response = get_tool_usage_guide()
    size_bytes = len(response["content"].encode('utf-8'))

    assert size_bytes < 50 * 1024, f"Document is {size_bytes} bytes (limit: 50KB)"
```

**Success Criteria**:
- Test file exists in `tests/integration/`
- All 7 test functions are defined
- Tests FAIL initially
- Running `pytest tests/integration/test_tool_guide_scenarios.py` shows 7 failures

**Dependencies**: T001, T002, T003

---

### T007 [X] [P] [X] Unit test for SchemaExtractor
**File**: `tests/unit/test_schema_extractor.py`

**Action**:
测试Schema提取逻辑的单元测试:

```python
import pytest
from unittest.mock import Mock, patch

def test_extract_all_tool_schemas():
    """Test extracting schemas from all registered tools"""
    from context_mcp.utils.schema_extractor import extract_tool_schemas

    schemas = extract_tool_schemas()

    assert isinstance(schemas, dict)
    assert len(schemas) >= 11  # At least 11 existing tools
    assert "list_directory" in schemas
    assert schemas["list_directory"]["type"] == "object"
    assert "properties" in schemas["list_directory"]

def test_extract_single_tool_schema():
    """Test extracting schema for a specific tool"""
    from context_mcp.utils.schema_extractor import extract_tool_schema

    schema = extract_tool_schema("list_directory")

    assert schema is not None
    assert schema["type"] == "object"
    assert "path" in schema["properties"]

def test_extract_nonexistent_tool():
    """Test handling of non-existent tool"""
    from context_mcp.utils.schema_extractor import extract_tool_schema

    schema = extract_tool_schema("nonexistent_tool_xyz")

    assert schema is None  # or raises ToolNotFoundError

def test_schema_caching():
    """Test that schema extraction results are cached"""
    from context_mcp.utils.schema_extractor import extract_tool_schemas

    # First call
    schemas1 = extract_tool_schemas()

    # Second call (should use cache)
    schemas2 = extract_tool_schemas()

    assert schemas1 is schemas2  # Same object reference (cached)

def test_categorize_tools():
    """Test automatic categorization of tools"""
    from context_mcp.utils.schema_extractor import categorize_tools

    categories = categorize_tools()

    assert "navigation" in categories
    assert "search" in categories
    assert "read" in categories
    assert "guide" in categories

    assert "list_directory" in categories["navigation"]
    assert "search_in_files" in categories["search"]
```

**Success Criteria**:
- Test file exists in `tests/unit/`
- All 5 test functions are defined
- Tests FAIL initially (schema_extractor.py does not exist)
- Clear test coverage for caching, categorization, edge cases

**Dependencies**: None (unit tests can be written before implementation)

---

### T008 [X] [P] [X] Unit test for DocGenerator
**File**: `tests/unit/test_doc_generator.py`

**Action**:
测试Markdown文档生成逻辑:

```python
import pytest
from unittest.mock import Mock

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
    assert "## navigation Tools (1)" in doc
    assert "## search Tools (1)" in doc

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
```

**Success Criteria**:
- Test file exists in `tests/unit/`
- All 5 test functions are defined
- Tests FAIL initially (doc_generator.py does not exist)
- Tests cover template loading, section generation, size calculation

**Dependencies**: T004 (template file must exist)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### T009 [X] Implement SchemaExtractor utility
**File**: `context_mcp/utils/schema_extractor.py`

**Action**:
实现从FastMCP提取Schema的逻辑:

```python
"""
Schema extraction utility for MCP tools.

Extracts input schemas from FastMCP registered tools using runtime reflection.
"""
from typing import Dict, Optional, List
from functools import lru_cache
from context_mcp.server import mcp

@lru_cache(maxsize=1)
def extract_tool_schemas() -> Dict[str, dict]:
    """
    Extract input schemas for all registered MCP tools.

    Returns:
        Dict mapping tool names to their input_schema dicts

    Example:
        >>> schemas = extract_tool_schemas()
        >>> schemas["list_directory"]["properties"]["path"]
        {'type': 'string', 'description': '...'}
    """
    tools = mcp.list_tools()
    return {tool.name: tool.input_schema for tool in tools}

def extract_tool_schema(tool_name: str) -> Optional[dict]:
    """
    Extract schema for a single tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Input schema dict, or None if tool not found
    """
    schemas = extract_tool_schemas()
    return schemas.get(tool_name)

@lru_cache(maxsize=1)
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
    search = ["search_in_file", "search_in_files", "find_files_by_name",
              "find_recently_modified_files"]
    read = ["read_entire_file", "read_file_lines", "read_file_tail", "read_files"]
    guide = ["get_tool_usage_guide"]

    return {
        "navigation": navigation,
        "search": search,
        "read": read,
        "guide": guide
    }

def get_tool_description(tool_name: str) -> str:
    """
    Get tool description from FastMCP metadata.

    Args:
        tool_name: Name of the tool

    Returns:
        Tool description string
    """
    tools = mcp.list_tools()
    for tool in tools:
        if tool.name == tool_name:
            return tool.description or "[No description]"
    return "[Tool not found]"
```

**Success Criteria**:
- File exists at `context_mcp/utils/schema_extractor.py`
- All 5 functions implemented with type hints and docstrings
- Tests in T007 now PASS
- Caching works (verified by test_schema_caching)
- Coverage: 100%

**Dependencies**: T007 (tests must exist and be failing)

---

### T010 [X] Implement DocGenerator utility
**File**: `context_mcp/utils/doc_generator.py`

**Action**:
实现Markdown文档生成逻辑:

```python
"""
Documentation generator for MCP tools.

Generates Markdown documentation with embedded JSON Schema blocks.
"""
from typing import Dict, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json
from datetime import datetime

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

def load_template():
    """Load Jinja2 template for tool documentation."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)
    return env.get_template("tool_guide.md.j2")

def generate_tool_section(tool_metadata: dict) -> str:
    """
    Generate Markdown section for a single tool.

    Args:
        tool_metadata: Dict with name, description, input_schema, examples, return_format

    Returns:
        Markdown string for the tool section
    """
    section = f"### {tool_metadata['name']}\n"
    section += f"**Purpose**: {tool_metadata['description']}\n\n"

    section += "**Parameters**:\n"
    section += "```json\n"
    section += json.dumps(tool_metadata['input_schema'], indent=2)
    section += "\n```\n\n"

    if tool_metadata.get('examples'):
        section += "**Examples**:\n"
        for example in tool_metadata['examples']:
            section += "```python\n"
            section += example.strip()
            section += "\n```\n"
        section += "\n"

    if tool_metadata.get('return_format'):
        section += f"**Returns**: {tool_metadata['return_format']}\n"

    section += "\n---\n"
    return section

def generate_category_section(category_name: str, tools: List[dict]) -> str:
    """
    Generate Markdown section for a tool category.

    Args:
        category_name: Category name (e.g., "Navigation")
        tools: List of tool metadata dicts

    Returns:
        Markdown string for the category section
    """
    section = f"## {category_name} Tools ({len(tools)})\n\n"
    for tool in tools:
        section += generate_tool_section(tool)
    return section

def render_document(tools_by_category: Dict[str, List[dict]],
                   total_tools: int,
                   filtered_count: int,
                   filter_applied: bool = False,
                   filtered_tools: str = "") -> str:
    """
    Render complete documentation using Jinja2 template.

    Args:
        tools_by_category: Dict mapping category names to tool lists
        total_tools: Total number of tools in the system
        filtered_count: Number of tools after filtering
        filter_applied: Whether filtering was applied
        filtered_tools: Comma-separated list of filtered tool names

    Returns:
        Complete Markdown document string
    """
    template = load_template()
    return template.render(
        generation_date=datetime.now().strftime("%Y-%m-%d"),
        tool_count=filtered_count,
        total_tools=total_tools,
        filter_applied=filter_applied,
        filtered_tools=filtered_tools,
        tools_by_category=tools_by_category
    )

def calculate_doc_size(content: str) -> int:
    """Calculate document size in bytes (UTF-8 encoded)."""
    return len(content.encode('utf-8'))
```

**Success Criteria**:
- File exists at `context_mcp/utils/doc_generator.py`
- All 5 functions implemented with type hints and docstrings
- Tests in T008 now PASS
- Jinja2 template loaded successfully
- Coverage: 100%

**Dependencies**: T004 (template), T008 (tests must exist and be failing)

---

### T011 [X] Implement YAML data loaders
**File**: `context_mcp/utils/yaml_loader.py`

**Action**:
实现YAML文件加载和缓存逻辑:

```python
"""
YAML data loader for tool descriptions and examples.

Loads manually-maintained YAML files with caching.
"""
from typing import Dict, List
from pathlib import Path
from functools import lru_cache
import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
DESCRIPTIONS_FILE = DATA_DIR / "tool_descriptions.yaml"
EXAMPLES_FILE = DATA_DIR / "tool_examples.yaml"

@lru_cache(maxsize=1)
def load_descriptions() -> Dict[str, str]:
    """
    Load tool descriptions from YAML file.

    Returns:
        Dict mapping tool names to description strings

    Raises:
        FileNotFoundError: If tool_descriptions.yaml missing
        yaml.YAMLError: If YAML syntax invalid
    """
    if not DESCRIPTIONS_FILE.exists():
        raise FileNotFoundError(f"Missing {DESCRIPTIONS_FILE}")

    with open(DESCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

@lru_cache(maxsize=1)
def load_examples() -> Dict[str, List[str]]:
    """
    Load tool examples from YAML file.

    Returns:
        Dict mapping tool names to lists of example code strings

    Raises:
        FileNotFoundError: If tool_examples.yaml missing
        yaml.YAMLError: If YAML syntax invalid
    """
    if not EXAMPLES_FILE.exists():
        raise FileNotFoundError(f"Missing {EXAMPLES_FILE}")

    with open(EXAMPLES_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def get_tool_description(tool_name: str) -> str:
    """Get description for a single tool (with fallback)."""
    descriptions = load_descriptions()
    return descriptions.get(tool_name, "[Description pending]")

def get_tool_examples(tool_name: str) -> List[str]:
    """Get examples for a single tool (with fallback)."""
    examples = load_examples()
    return examples.get(tool_name, [])
```

**Success Criteria**:
- File exists at `context_mcp/utils/yaml_loader.py`
- All 4 functions implemented with error handling
- Caching works (verified by lru_cache)
- Handles missing files gracefully
- Coverage: 100%

**Dependencies**: T001, T002, T003 (YAML files must exist)

---

### T012 [X] Implement get_tool_usage_guide tool
**File**: `context_mcp/tools/guide.py`

**Action**:
实现主工具函数,协调所有模块:

```python
"""
Tool usage guide generator.

MCP tool that returns comprehensive documentation for all registered tools.
"""
from typing import Optional, List
import time
from context_mcp.server import mcp
from context_mcp.utils.schema_extractor import (
    extract_tool_schemas,
    categorize_tools,
    get_tool_description as get_tool_desc_from_mcp
)
from context_mcp.utils.yaml_loader import get_tool_description, get_tool_examples
from context_mcp.utils.doc_generator import render_document, calculate_doc_size

@mcp.tool()
def get_tool_usage_guide(tool_names: Optional[List[str]] = None) -> dict:
    """
    Returns comprehensive usage documentation for MCP tools.

    Generates Markdown documentation with JSON Schema definitions, descriptions,
    and usage examples. Supports filtering to specific tools.

    Args:
        tool_names: Optional list of tool names to include. If None, returns all tools.

    Returns:
        Dictionary with:
        - content: Markdown documentation string
        - metadata: Dict with total_tools, filtered_count, generation_time_ms
        - warnings: List of warning messages (if any invalid tool names)

    Example:
        >>> guide = get_tool_usage_guide()
        >>> print(guide["content"][:50])
        # Context MCP Tools Usage Guide

        >>> guide = get_tool_usage_guide(tool_names=["list_directory"])
        >>> guide["metadata"]["filtered_count"]
        1
    """
    start_time = time.time()

    # Get all tool schemas
    all_schemas = extract_tool_schemas()
    categories = categorize_tools()

    # Filter tools if requested
    warnings = []
    invalid_names = []

    if tool_names is not None:
        # Validate tool names
        valid_names = set(all_schemas.keys())
        requested = set(tool_names)
        invalid = requested - valid_names

        if invalid:
            invalid_names = sorted(invalid)
            warnings.append(
                f"Tool{'s' if len(invalid) > 1 else ''} {', '.join(f\"'{n}\"' for n in invalid)} "
                f"not found. Available tools: {', '.join(sorted(valid_names))}"
            )

        # Filter to valid names only
        tools_to_include = requested & valid_names
    else:
        tools_to_include = set(all_schemas.keys())

    # Build tool metadata for each category
    tools_by_category = {}
    total_included = 0

    for category, tool_list in categories.items():
        category_tools = []
        for tool_name in tool_list:
            if tool_name in tools_to_include:
                tool_meta = {
                    "name": tool_name,
                    "description": get_tool_description(tool_name),
                    "input_schema": all_schemas[tool_name],
                    "examples": get_tool_examples(tool_name),
                    "return_format": None  # Could be added to YAML later
                }
                category_tools.append(tool_meta)
                total_included += 1

        if category_tools:  # Only include non-empty categories
            tools_by_category[category] = category_tools

    # Render document
    filter_applied = tool_names is not None
    filtered_tools_str = ", ".join(sorted(tools_to_include)) if filter_applied else ""

    content = render_document(
        tools_by_category=tools_by_category,
        total_tools=len(all_schemas),
        filtered_count=total_included,
        filter_applied=filter_applied,
        filtered_tools=filtered_tools_str
    )

    # Calculate metrics
    generation_time_ms = (time.time() - start_time) * 1000
    doc_size = calculate_doc_size(content)

    # Build response
    response = {
        "content": content,
        "metadata": {
            "total_tools": len(all_schemas),
            "filtered_count": total_included,
            "generation_time_ms": round(generation_time_ms, 2),
            "document_size_bytes": doc_size
        }
    }

    if invalid_names:
        response["metadata"]["invalid_names"] = invalid_names

    if warnings:
        response["warnings"] = warnings

    return response
```

**Success Criteria**:
- File exists at `context_mcp/tools/guide.py`
- Tool function decorated with `@mcp.tool()`
- All tests in T005 and T006 now PASS
- Function handles all 5 test scenarios from contract
- Type hints and docstring complete
- Coverage: 100%

**Dependencies**: T009 (schema_extractor), T010 (doc_generator), T011 (yaml_loader), T005, T006 (tests)

---

### T013 [X] Register tool in server.py
**File**: `context_mcp/server.py`

**Action**:
在MCP服务器入口注册新工具:

1. 在文件顶部导入guide模块:
```python
from context_mcp.tools import navigation, search, read, guide
```

2. 确认工具自动注册(FastMCP的`@mcp.tool()`装饰器会自动注册)

3. 验证:运行`mcp-cli list-tools`应看到`get_tool_usage_guide`

**Success Criteria**:
- `server.py`包含`import guide`语句
- 运行服务器后,`mcp.list_tools()`返回12个工具
- 新工具出现在工具列表中

**Dependencies**: T012 (guide.py must exist)

---

## Phase 3.4: Integration & Validation

### T014 [X] Execute quickstart validation
**File**: `specs/004-tool-tool-prompt/quickstart.md`

**Action**:
按照quickstart.md的10个步骤逐一验证:

1. **Step 1**: 验证工具注册 - `mcp-cli list-tools` 包含 `get_tool_usage_guide`
2. **Step 2**: 调用无参数 - 返回所有12个工具的文档
3. **Step 3**: 过滤特定工具 - 仅返回2个指定工具
4. **Step 4**: 处理无效工具名 - 返回警告但继续
5. **Step 5**: 验证Schema准确性 - 与`mcp-cli describe-tool`输出一致
6. **Step 6**: 验证Markdown格式 - 通过CommonMark验证
7. **Step 7**: 验证示例可执行性 - 提取示例并执行成功
8. **Step 8**: 性能基准 - 平均生成时间<50ms
9. **Step 9**: 验证YAML文件 - 加载无错误,12个工具全覆盖
10. **Step 10**: 端到端集成 - LLM获取文档→调用其他工具成功

**Success Criteria**:
- 所有10个步骤PASS
- 无回归(现有11个工具仍正常工作)
- 性能满足目标(<100ms p95)
- 文档大小<50KB

**Dependencies**: T001-T013 (所有实现任务完成)

---

## Dependencies

```
Setup Phase:
T001 (YAML dir) ─┬─> T002 (descriptions) ─┐
                  └─> T003 (examples) ─────┤
T004 (template) ────────────────────────────┤
                                            │
Test Phase (all parallel):                  │
T005 (contract test) [P] ───────────────────┤
T006 (integration test) [P] ────────────────┤
T007 (unit test schema_extractor) [P] ──────┤
T008 (unit test doc_generator) [P] ─────────┤
                                            │
Implementation Phase:                       │
T009 (schema_extractor) <─── T007 ──────────┤
T010 (doc_generator) <─── T008, T004 ───────┤
T011 (yaml_loader) <─── T001, T002, T003 ───┤
                                            │
T012 (guide.py) <─── T009, T010, T011, T005, T006
    │
    v
T013 (server.py) <─── T012
    │
    v
T014 (quickstart) <─── T001-T013 (all complete)
```

---

## Parallel Execution Examples

### Batch 1: Setup (可并行)
```bash
# Run T001, T002, T003, T004 together
Task: "Create YAML data directory and template files"
Task: "Populate tool_descriptions.yaml with actual descriptions"
Task: "Populate tool_examples.yaml with code examples"
Task: "Create Jinja2 documentation template"
```

### Batch 2: Tests (可并行)
```bash
# Run T005-T008 together (all tests, different files)
Task: "Contract test for get_tool_usage_guide in tests/contract/"
Task: "Integration test for tool guide scenarios in tests/integration/"
Task: "Unit test for SchemaExtractor in tests/unit/"
Task: "Unit test for DocGenerator in tests/unit/"
```

### Batch 3: Implementation (串行,有依赖)
```bash
# T009 first
Task: "Implement SchemaExtractor utility"

# T010 and T011 can run after T009 (parallel)
Task: "Implement DocGenerator utility"
Task: "Implement YAML data loaders"

# T012 waits for T009, T010, T011
Task: "Implement get_tool_usage_guide tool"

# T013 waits for T012
Task: "Register tool in server.py"
```

---

## Validation Checklist

**GATE: All items must be checked before marking feature complete**

- [x] Contract `get_tool_usage_guide.json` has corresponding test (T005)
- [x] All 6 entities from data-model.md covered by implementation
- [x] All tests (T005-T008) come before implementation (T009-T012)
- [x] Parallel tasks ([P]) are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD order maintained: Red (T005-T008) → Green (T009-T012) → Refactor
- [x] All tests PASS after implementation
- [x] Quickstart validation (T014) covers all acceptance scenarios
- [x] Performance targets met (<100ms generation, <50KB doc size)
- [x] Coverage maintained at 99.2%+

---

## Notes

**TDD Discipline**:
- Tasks T005-T008 MUST be completed and FAIL before starting T009-T012
- Verify test failures with `pytest tests/contract tests/integration tests/unit`
- Implementation tasks (T009-T012) should make tests PASS one by one

**Parallel Execution**:
- [P] marked tasks have no dependencies on each other
- Can be executed simultaneously by multiple agents/developers
- Example: T002 and T003 edit different files, safe to run in parallel

**Commit Strategy**:
- Commit after each task completion
- Use conventional commits: `feat(guide): implement SchemaExtractor (T009)`

**Rollback Plan**:
- If T014 fails, revert to last passing commit
- Debug failing quickstart step before proceeding
- Do not skip validation steps

---

**Total Tasks**: 14
**Estimated Time**: 6-8 hours (with parallel execution)
**Risk Level**: Low (well-defined requirements, existing patterns)
