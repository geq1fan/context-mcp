# Quickstart: read_project_context Tool

**Feature**: 002-navigation-tool-claude
**Tool**: `read_project_context`
**Category**: Navigation
**Date**: 2025-10-03

## Overview

This quickstart guide demonstrates how to use the `read_project_context` MCP tool to discover and read AI agent context files (AGENTS.md and CLAUDE.md) from a project.

## Prerequisites

- Context MCP server installed and configured
- PROJECT_ROOT environment variable set
- (Optional) AGENTS.md and/or CLAUDE.md in your project root

## Quick Example

### Setup Test Project

```bash
# Create test project structure
mkdir -p /tmp/test-project
cd /tmp/test-project

# Create AGENTS.md
cat > AGENTS.md << 'EOF'
# Universal Agent Instructions

## Code Style
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Follow PEP 8 for Python code

## Testing Requirements
- All new features must have unit tests
- Test coverage must be >80%
- Run tests before committing
EOF

# Create CLAUDE.md
cat > CLAUDE.md << 'EOF'
# Claude-Specific Configuration

## Response Style
- Be concise and direct
- Include code examples
- Explain complex concepts

## Project Context
This is a Python MCP server project using fastmcp framework.
EOF

# Set PROJECT_ROOT
export PROJECT_ROOT=/tmp/test-project
```

### Use the Tool

```python
# Start agent-mcp server with PROJECT_ROOT set
# Then call the tool via MCP client

import json

# MCP tool call (no parameters needed)
response = mcp_client.call_tool("read_project_context")

print(json.dumps(response, indent=2))
```

### Expected Output

```json
{
  "files": [
    {
      "filename": "AGENTS.md",
      "exists": true,
      "readable": true,
      "size_bytes": 245,
      "content": "# Universal Agent Instructions\n\n## Code Style\n- Use 4 spaces for indentation\n- Maximum line length: 100 characters\n- Follow PEP 8 for Python code\n\n## Testing Requirements\n- All new features must have unit tests\n- Test coverage must be >80%\n- Run tests before committing\n",
      "error": null
    },
    {
      "filename": "CLAUDE.md",
      "exists": true,
      "readable": true,
      "size_bytes": 184,
      "content": "# Claude-Specific Configuration\n\n## Response Style\n- Be concise and direct\n- Include code examples\n- Explain complex concepts\n\n## Project Context\nThis is a Python MCP server project using fastmcp framework.\n",
      "error": null
    }
  ],
  "message": "Found 2 of 2 context files",
  "total_found": 2
}
```

## Usage Scenarios

### Scenario 1: Project with Only AGENTS.md

```bash
# Setup
cd /tmp/test-project
rm CLAUDE.md  # Remove CLAUDE.md

# Call tool
response = mcp_client.call_tool("read_project_context")
```

**Expected Result**:
```json
{
  "files": [
    {
      "filename": "AGENTS.md",
      "exists": true,
      "readable": true,
      "size_bytes": 245,
      "content": "...",
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

### Scenario 2: Project with No Context Files

```bash
# Setup
cd /tmp/test-project
rm -f AGENTS.md CLAUDE.md

# Call tool
response = mcp_client.call_tool("read_project_context")
```

**Expected Result**:
```json
{
  "files": [
    {
      "filename": "AGENTS.md",
      "exists": false,
      "readable": false,
      "size_bytes": null,
      "content": null,
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
  "message": "No context files found in PROJECT_ROOT",
  "total_found": 0
}
```

### Scenario 3: File Exists but Not Readable

```bash
# Setup
cd /tmp/test-project
echo "# Protected Instructions" > AGENTS.md
chmod 000 AGENTS.md  # Remove all permissions

# Call tool
response = mcp_client.call_tool("read_project_context")
```

**Expected Result**:
```json
{
  "files": [
    {
      "filename": "AGENTS.md",
      "exists": true,
      "readable": false,
      "size_bytes": null,
      "content": null,
      "error": "Permission denied: [Errno 13] Permission denied: '.../AGENTS.md'"
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
  "message": "Found 0 of 2 context files (1 exists but not readable)",
  "total_found": 0
}
```

## Integration with AI Agents

### Example: Claude Code Agent Workflow

```python
# AI Agent startup workflow
def initialize_project_context():
    """Read project context before starting agent tasks."""

    # Step 1: Read context files
    context_response = mcp_client.call_tool("read_project_context")

    # Step 2: Parse results
    context_content = ""
    for file in context_response["files"]:
        if file["exists"] and file["readable"]:
            context_content += f"\n--- {file['filename']} ---\n"
            context_content += file["content"]

    # Step 3: Use context in agent prompts
    if context_content:
        print(f"Loaded project context ({context_response['total_found']} files)")
        # Inject context into agent's system prompt
        agent.set_context(context_content)
    else:
        print("No project context files found, using default behavior")

    return context_response

# Use in agent
context = initialize_project_context()
```

## Testing the Tool

### Manual Testing

```bash
# Set up test environment
export PROJECT_ROOT=/tmp/test-project
cd /tmp/test-project

# Create test files
echo "# Test AGENTS.md" > AGENTS.md
echo "# Test CLAUDE.md" > CLAUDE.md

# Run MCP server
uvx context-mcp

# In another terminal, call the tool via MCP client
# (Use your MCP client library or tool)
```

### Automated Testing

```bash
# Run contract tests
cd /path/to/agent-mcp
pytest tests/contract/test_navigation_contract.py::test_read_project_context -v

# Run integration tests
pytest tests/integration/ -v -k "context"

# Run all tests
pytest tests/ -v
```

## Troubleshooting

### Error: "PROJECT_ROOT is not configured"

**Cause**: PROJECT_ROOT environment variable is not set

**Solution**:
```bash
export PROJECT_ROOT=/path/to/your/project
# Or set in your shell profile (~/.bashrc, ~/.zshrc)
```

### Error: "PROJECT_ROOT does not exist"

**Cause**: PROJECT_ROOT points to non-existent directory

**Solution**:
```bash
# Verify path exists
ls -ld $PROJECT_ROOT

# Update to correct path
export PROJECT_ROOT=/correct/path
```

### No Files Found (Expected Behavior)

**Cause**: Neither AGENTS.md nor CLAUDE.md exists in PROJECT_ROOT

**Solution**: This is not an error. The tool returns:
```json
{
  "message": "No context files found in PROJECT_ROOT",
  "total_found": 0
}
```

To add context files:
```bash
cd $PROJECT_ROOT
echo "# Project Instructions" > AGENTS.md
```

### File Exists but Not Readable

**Cause**: Permission denied or encoding error

**Solution**:
```bash
# Check permissions
ls -l AGENTS.md

# Fix permissions
chmod 644 AGENTS.md

# Check encoding (must be UTF-8)
file -i AGENTS.md
```

## Performance Characteristics

- **Response Time**: <100ms for typical files (<100KB)
- **Large Files**: Files >1MB trigger warning log but are still returned
- **File I/O**: Exactly 2 stat() calls + 0-2 read_text() calls
- **Memory Usage**: O(n) where n = total size of readable files

## Best Practices

1. **Keep Context Files Small**: Aim for <100KB per file for optimal performance
2. **Use UTF-8 Encoding**: Ensure files are UTF-8 encoded to avoid read errors
3. **Set Appropriate Permissions**: Files should be readable (644 permissions)
4. **Check total_found**: Use this field to determine if context was loaded successfully
5. **Handle Missing Files Gracefully**: It's normal for projects to not have context files

## Next Steps

- See [data-model.md](./data-model.md) for detailed response structure
- See [contracts/](./contracts/) for JSON Schema and test cases
- See [plan.md](./plan.md) for implementation architecture
- Run `/tasks` to generate implementation tasks

## Validation Checklist

Use this checklist to validate the tool works correctly:

- [ ] Tool can be called with no parameters
- [ ] Returns both AGENTS.md and CLAUDE.md metadata in response
- [ ] Files are ordered by priority (AGENTS.md first)
- [ ] Handles missing files gracefully (no exceptions)
- [ ] Reports correct count in `total_found` field
- [ ] Returns file content when files exist and are readable
- [ ] Returns null content when files don't exist or aren't readable
- [ ] Provides descriptive error messages for permission/encoding issues
- [ ] Enforces PROJECT_ROOT boundary (security check)
- [ ] Completes within 1 second for typical files
- [ ] Logs warning for files >1MB but still returns content
- [ ] Works across platforms (Windows/Linux/macOS)

---

**Status**: Ready for implementation
**Contract Version**: 1.0.0
**Last Updated**: 2025-10-03
