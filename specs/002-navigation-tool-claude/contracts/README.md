# MCP Tool Contracts

This directory contains the contract definitions for MCP tools in JSON Schema format.

## Contract: read_project_context

**File**: `read_project_context.json`
**Category**: Navigation
**Purpose**: Discover and read AI agent context files (AGENTS.md and CLAUDE.md) from PROJECT_ROOT

### Tool Signature

```python
def read_project_context() -> dict:
    """Read project context files from PROJECT_ROOT.

    Checks for AGENTS.md and CLAUDE.md in priority order and returns
    their content with metadata.

    Returns:
        dict: {
            "files": List[dict],      # Context file metadata and content
            "message": str,             # Human-readable result summary
            "total_found": int          # Count of readable files
        }

    Raises:
        ConfigurationError: If PROJECT_ROOT is not set or invalid
    """
```

### Input Schema

No parameters required. Tool automatically checks PROJECT_ROOT for context files.

### Output Schema

See `read_project_context.json` for complete JSON Schema definition.

**Response Structure**:
```json
{
  "files": [
    {
      "filename": "AGENTS.md",
      "exists": true,
      "readable": true,
      "size_bytes": 1234,
      "content": "file content here...",
      "error": null
    },
    {
      "filename": "CLAUDE.md",
      "exists": false,
      "readable": false,
      "size_bytes": null,
      "content": null,
      "error": null
    }
  ],
  "message": "Found 1 of 2 context files",
  "total_found": 1
}
```

### Test Cases

The contract includes 8 test cases:

1. **both_files_exist** - Both context files present and readable
2. **only_agents_md_exists** - Only AGENTS.md present
3. **only_claude_md_exists** - Only CLAUDE.md present
4. **no_files_exist** - Neither file present
5. **empty_file** - File exists but is empty (0 bytes)
6. **permission_denied** - File exists but cannot be read
7. **invalid_encoding** - File contains non-UTF-8 bytes
8. **large_file** - File larger than 1MB (warning logged)

### Error Cases

1. **project_root_not_set** - PROJECT_ROOT environment variable not configured
2. **project_root_invalid** - PROJECT_ROOT points to non-existent directory

### Security Requirements

- ✅ Path traversal protection (hardcoded filenames only)
- ✅ PROJECT_ROOT boundary enforcement via PathValidator
- ✅ Read-only operations (no file modifications)

### Performance Requirements

- ✅ Response time <1s for typical files (<100KB)
- ✅ Handle files up to 5MB without crashing

## Contract Testing

Contract tests are located in `tests/contract/test_navigation_contract.py`.

Run contract tests:
```bash
pytest tests/contract/ -v -m contract
```

Contract tests verify:
- Input/output schema compliance
- All test cases from contract definition
- Error cases produce expected errors
- Security requirements are enforced
- Performance requirements are met

## Usage in Tests

```python
import json
from pathlib import Path

# Load contract
contract_path = Path("specs/002-navigation-tool-claude/contracts/read_project_context.json")
with contract_path.open() as f:
    contract = json.load(f)

# Validate output against contract schema
output_schema = contract["tool"]["output_schema"]
# Use jsonschema.validate(output, output_schema)

# Run test cases from contract
for test_case in contract["test_cases"]:
    # Setup test environment
    # Call tool
    # Assert output matches expected_output
```

## Versioning

Contract version: **1.0.0**

Breaking changes to the contract require a major version bump and migration path documentation.
