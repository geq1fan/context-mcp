# Quickstart: Tool Usage Guide Tool

**Feature**: 004-tool-tool-prompt
**Date**: 2025-10-04
**Purpose**: Verify the `get_tool_usage_guide` tool works end-to-end

---

## Prerequisites

- Context MCP server installed (`uvx context-mcp`)
- PROJECT_ROOT environment variable set
- Python 3.11+ runtime
- MCP client (Claude Desktop, mcp-cli, or custom client)

---

## Step 1: Verify Tool Registration

**Action**: List all available tools and confirm `get_tool_usage_guide` is present.

**Command** (using mcp-cli):
```bash
mcp-cli list-tools --server context-mcp
```

**Expected Output**:
```json
{
  "tools": [
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
    "get_tool_usage_guide"  // ← New tool
  ]
}
```

**Validation**:
- [ ] Tool count is 12 (11 existing + 1 new)
- [ ] `get_tool_usage_guide` appears in the list
- [ ] No error messages

---

## Step 2: Call Tool Without Parameters (全量文档)

**Action**: 获取所有工具的完整文档。

**Command**:
```bash
mcp-cli call-tool get_tool_usage_guide --server context-mcp
```

**Expected Output Structure**:
```json
{
  "content": "# Context MCP Tools Usage Guide\n\nGenerated: 2025-10-04 | Tools: 12\n\n## Navigation Tools (3)\n\n### list_directory\n**Purpose**: 列出指定目录下的所有文件和子目录...\n\n**Parameters**:\n```json\n{\n  \"type\": \"object\",\n  ...\n}\n```\n\n**Example**:\n```python\nlist_directory(path=\".\", sort_by=\"mtime\")\n```\n\n**Returns**: 文件列表,包含名称、类型...\n\n---\n...",
  "metadata": {
    "total_tools": 12,
    "filtered_count": 12,
    "invalid_names": [],
    "generation_time_ms": 15.3
  }
}
```

**Validation**:
- [ ] `content` starts with `# Context MCP Tools Usage Guide`
- [ ] `content` contains all 3 categories: Navigation, Search, Read
- [ ] `content` includes 12 tool sections
- [ ] Each tool section has: Purpose, Parameters (JSON), Example (Python), Returns
- [ ] `metadata.total_tools` == 12
- [ ] `metadata.filtered_count` == 12
- [ ] `metadata.generation_time_ms` < 100
- [ ] No `warnings` field (or empty array)
- [ ] Document size < 50KB

---

## Step 3: Filter Specific Tools

**Action**: 仅获取2个指定工具的文档。

**Command**:
```bash
mcp-cli call-tool get_tool_usage_guide \
  --params '{"tool_names": ["list_directory", "read_entire_file"]}' \
  --server context-mcp
```

**Expected Output Structure**:
```json
{
  "content": "# Context MCP Tools Usage Guide\n\nGenerated: 2025-10-04 | Tools: 2 | Filter: list_directory, read_entire_file\n\n## Navigation Tools (1)\n\n### list_directory\n...\n\n## Read Tools (1)\n\n### read_entire_file\n...",
  "metadata": {
    "total_tools": 12,
    "filtered_count": 2,
    "invalid_names": []
  }
}
```

**Validation**:
- [ ] `content` contains ONLY `list_directory` and `read_entire_file`
- [ ] `content` does NOT contain `search_in_files` or other tools
- [ ] `metadata.filtered_count` == 2
- [ ] Category headers show correct counts (e.g., "Navigation Tools (1)")
- [ ] No warnings

---

## Step 4: Handle Invalid Tool Names

**Action**: 请求一个不存在的工具,验证优雅降级。

**Command**:
```bash
mcp-cli call-tool get_tool_usage_guide \
  --params '{"tool_names": ["list_directory", "fake_tool", "read_entire_file"]}' \
  --server context-mcp
```

**Expected Output Structure**:
```json
{
  "content": "# Context MCP Tools Usage Guide\n...\n### list_directory\n...\n### read_entire_file\n...",
  "warnings": [
    "Tool 'fake_tool' not found. Available tools: list_directory, show_tree, read_project_context, search_in_file, search_in_files, find_files_by_name, find_recently_modified_files, read_entire_file, read_file_lines, read_file_tail, read_files, get_tool_usage_guide"
  ],
  "metadata": {
    "total_tools": 12,
    "filtered_count": 2,
    "invalid_names": ["fake_tool"]
  }
}
```

**Validation**:
- [ ] `content` contains valid tools (list_directory, read_entire_file)
- [ ] `content` does NOT contain `fake_tool`
- [ ] `warnings` array has 1 item
- [ ] Warning message includes "not found" and lists all available tools
- [ ] `metadata.invalid_names` == ["fake_tool"]
- [ ] `metadata.filtered_count` == 2 (excludes invalid)

---

## Step 5: Verify JSON Schema Accuracy

**Action**: 检查生成的Schema是否与实际工具定义一致。

**Command**:
```bash
# 1. Get schema from usage guide
mcp-cli call-tool get_tool_usage_guide \
  --params '{"tool_names": ["list_directory"]}' \
  --server context-mcp | jq -r '.content' > guide_schema.txt

# 2. Get schema directly from MCP
mcp-cli describe-tool list_directory --server context-mcp > direct_schema.json

# 3. Compare (manual verification)
```

**Validation**:
- [ ] Parameters in guide_schema.txt match direct_schema.json
- [ ] Required fields match exactly
- [ ] Parameter types match (string/number/boolean/array/object)
- [ ] Default values match (if any)
- [ ] No extra or missing parameters

---

## Step 6: Verify Markdown Format

**Action**: 确认生成的文档是有效的CommonMark。

**Command**:
```bash
mcp-cli call-tool get_tool_usage_guide \
  --server context-mcp | jq -r '.content' > guide.md

# Validate with CommonMark parser (e.g., cmark)
cmark guide.md > /dev/null && echo "Valid Markdown" || echo "Invalid Markdown"
```

**Expected Output**:
```
Valid Markdown
```

**Validation**:
- [ ] No parsing errors from CommonMark validator
- [ ] All JSON code blocks are properly closed (```)
- [ ] All Python code blocks are properly closed (```)
- [ ] Headers use correct levels (#, ##, ###)
- [ ] No malformed lists or tables

---

## Step 7: Verify Usage Examples

**Action**: 复制一个示例代码,验证其可执行性。

**Command**:
```bash
# Extract example from guide
mcp-cli call-tool get_tool_usage_guide \
  --params '{"tool_names": ["list_directory"]}' \
  --server context-mcp | jq -r '.content' | grep -A 2 '**Example**:' | tail -1 > example.py

# Execute example (assuming MCP client library available)
python -c "
from mcp_client import call_tool
result = call_tool('list_directory', path='.', sort_by='mtime')
print(f'Success: {len(result)} items')
"
```

**Expected Output**:
```
Success: 15 items
```

**Validation**:
- [ ] Example code is syntactically valid Python
- [ ] Example code executes without errors
- [ ] Example parameters match tool's input_schema
- [ ] Example demonstrates a realistic use case

---

## Step 8: Performance Benchmark

**Action**: 测量文档生成性能。

**Command**:
```bash
# Run 10 iterations and measure average time
for i in {1..10}; do
  mcp-cli call-tool get_tool_usage_guide --server context-mcp | jq '.metadata.generation_time_ms'
done | awk '{sum+=$1; count++} END {print "Average:", sum/count, "ms"}'
```

**Expected Output**:
```
Average: 12.4 ms
```

**Validation**:
- [ ] Average generation time < 50ms
- [ ] p95 generation time < 100ms
- [ ] No outliers > 200ms
- [ ] Memory usage stable (no leaks on repeated calls)

---

## Step 9: Verify YAML File Structure

**Action**: 检查手动维护的YAML文件是否存在且格式正确。

**Command**:
```bash
# Check descriptions file
cat context_mcp/data/tool_descriptions.yaml | head -20

# Check examples file
cat context_mcp/data/tool_examples.yaml | head -20

# Validate YAML syntax
python -c "
import yaml
with open('context_mcp/data/tool_descriptions.yaml') as f:
    descriptions = yaml.safe_load(f)
    print(f'Descriptions for {len(descriptions)} tools loaded')

with open('context_mcp/data/tool_examples.yaml') as f:
    examples = yaml.safe_load(f)
    print(f'Examples for {len(examples)} tools loaded')
"
```

**Expected Output**:
```
Descriptions for 12 tools loaded
Examples for 12 tools loaded
```

**Validation**:
- [ ] tool_descriptions.yaml contains 12 entries (one per tool)
- [ ] tool_examples.yaml contains 12 entries
- [ ] All tool names match FastMCP registered names
- [ ] No placeholder text `[Description pending]` remains
- [ ] All examples are valid Python syntax

---

## Step 10: End-to-End Integration Test

**Action**: 模拟真实LLM Agent使用场景。

**Scenario**:
1. LLM Agent 连接到 Context MCP
2. 调用 `get_tool_usage_guide` 学习所有工具
3. 基于文档,正确调用 `search_in_files` 工具

**Command**:
```bash
# Step 1: Get documentation
GUIDE=$(mcp-cli call-tool get_tool_usage_guide --server context-mcp | jq -r '.content')

# Step 2: Extract search_in_files parameters from guide
echo "$GUIDE" | grep -A 50 '### search_in_files'

# Step 3: Use extracted knowledge to call search_in_files
mcp-cli call-tool search_in_files \
  --params '{"pattern": "TODO", "include_pattern": "*.py", "case_sensitive": false}' \
  --server context-mcp
```

**Expected Output**:
```json
{
  "results": [
    {"file": "context_mcp/tools/guide.py", "line": 42, "match": "# TODO: Add caching"},
    ...
  ]
}
```

**Validation**:
- [ ] Guide contains complete search_in_files documentation
- [ ] Parameters in guide match actual tool signature
- [ ] LLM can construct valid call based on guide alone
- [ ] Call succeeds and returns expected results

---

## Success Criteria

**All Steps Must Pass**:
- ✅ Tool registered and discoverable (Step 1)
- ✅ Full documentation generation works (Step 2)
- ✅ Filtering works correctly (Step 3)
- ✅ Error handling is graceful (Step 4)
- ✅ Schema accuracy is 100% (Step 5)
- ✅ Markdown format is valid (Step 6)
- ✅ Examples are executable (Step 7)
- ✅ Performance meets targets (Step 8)
- ✅ YAML files are properly structured (Step 9)
- ✅ End-to-end usage succeeds (Step 10)

**Performance Targets**:
- Document generation: < 100ms (p95)
- Document size: < 50KB
- No memory leaks on repeated calls

**Quality Targets**:
- Schema accuracy: 100% match with actual tools
- Markdown validity: 100% CommonMark compliance
- Example correctness: 100% executable without errors

---

## Troubleshooting

### Issue: Tool not found in list
**Symptom**: `get_tool_usage_guide` missing from `mcp-cli list-tools`
**Fix**:
1. Verify `context_mcp/tools/guide.py` exists
2. Check `context_mcp/server.py` imports guide module
3. Restart MCP server

### Issue: Schema mismatch
**Symptom**: Generated schema differs from actual tool
**Fix**:
1. Clear FastMCP cache: `rm -rf ~/.cache/fastmcp`
2. Verify tool registration uses `@mcp.tool()` decorator
3. Check `inspect.signature()` extraction logic

### Issue: Missing descriptions/examples
**Symptom**: Placeholder text `[Description pending]` appears
**Fix**:
1. Edit `context_mcp/data/tool_descriptions.yaml`
2. Add missing tool entries
3. Follow YAML format: `tool_name: | multiline description`

### Issue: Performance degradation
**Symptom**: Generation time > 100ms
**Fix**:
1. Check YAML file size (should be < 100KB combined)
2. Verify caching is enabled (`functools.lru_cache`)
3. Profile with `cProfile` to identify bottlenecks

---

**Quickstart Complete**: If all steps pass, the feature is production-ready! 🎉
