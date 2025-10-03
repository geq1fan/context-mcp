# Data Model: Navigation Tool - Project Context Reader

**Feature**: 002-navigation-tool-claude
**Date**: 2025-10-03
**Status**: Complete

## Overview

This feature introduces one primary entity (**ContextFile**) and one response structure (**ContextFilesResponse**) for discovering and reading AI agent context files.

## Entities

### ContextFile

Represents a single AI agent context file (AGENTS.md or CLAUDE.md) with its metadata and content.

**Attributes**:

| Attribute | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| filename | str | Yes | Must be "AGENTS.md" or "CLAUDE.md" | Name of the context file |
| exists | bool | Yes | - | Whether file exists in PROJECT_ROOT |
| readable | bool | Yes | - | Whether file can be read (permissions) |
| size_bytes | int \| None | No | ≥0 if exists, None otherwise | File size in bytes |
| content | str \| None | No | Valid UTF-8 if exists, None otherwise | File content as plain text |
| error | str \| None | No | - | Error message if read failed |

**Validation Rules**:
- `filename` must be exactly "AGENTS.md" or "CLAUDE.md" (case-sensitive)
- If `exists == True`, then `size_bytes` must be ≥0
- If `readable == False`, then `content` must be None and `error` should describe the issue
- If `exists == False`, then `readable` must be False, `size_bytes` must be None, `content` must be None

**State Transitions**:
```
Initial State → Check Existence → exists=True/False
                                    ↓
                              Check Readable → readable=True/False
                                    ↓
                              Read Content → content=str/None, error=str/None
```

**Relationships**:
- Many-to-one: Multiple ContextFile instances belong to one ContextFilesResponse
- One ContextFile per distinct filename (max 2 per response)

### ContextFilesResponse

Response structure returned by the `read_project_context` MCP tool.

**Attributes**:

| Attribute | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| files | List[ContextFile] | Yes | Length 0-2, ordered by priority | List of context files checked |
| message | str | Yes | Non-empty | Human-readable result summary |
| total_found | int | No | 0-2 | Count of files that exist and are readable |

**Validation Rules**:
- `files` list must be ordered: AGENTS.md first, CLAUDE.md second (if both present)
- `files` list must contain at most 2 elements
- `total_found` must equal count of files where `exists == True` and `readable == True`
- `message` must provide context about results (e.g., "Found 1 of 2 context files", "No context files found")

**Example Instances**:

```python
# Case 1: Both files exist and readable
{
    "files": [
        {
            "filename": "AGENTS.md",
            "exists": True,
            "readable": True,
            "size_bytes": 1234,
            "content": "# Project Agent Instructions\n...",
            "error": None
        },
        {
            "filename": "CLAUDE.md",
            "exists": True,
            "readable": True,
            "size_bytes": 567,
            "content": "# Claude-specific Configuration\n...",
            "error": None
        }
    ],
    "message": "Found 2 of 2 context files",
    "total_found": 2
}

# Case 2: Only CLAUDE.md exists
{
    "files": [
        {
            "filename": "AGENTS.md",
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "content": None,
            "error": None
        },
        {
            "filename": "CLAUDE.md",
            "exists": True,
            "readable": True,
            "size_bytes": 890,
            "content": "# Claude Configuration\n...",
            "error": None
        }
    ],
    "message": "Found 1 of 2 context files",
    "total_found": 1
}

# Case 3: No files exist
{
    "files": [
        {
            "filename": "AGENTS.md",
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "content": None,
            "error": None
        },
        {
            "filename": "CLAUDE.md",
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "content": None,
            "error": None
        }
    ],
    "message": "No context files found in PROJECT_ROOT",
    "total_found": 0
}

# Case 4: File exists but not readable (permission error)
{
    "files": [
        {
            "filename": "AGENTS.md",
            "exists": True,
            "readable": False,
            "size_bytes": None,
            "content": None,
            "error": "Permission denied: cannot read file"
        },
        {
            "filename": "CLAUDE.md",
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "content": None,
            "error": None
        }
    ],
    "message": "Found 0 of 2 context files (1 exists but not readable)",
    "total_found": 0
}
```

## Domain Logic

### File Discovery Algorithm

```python
def discover_context_files() -> List[ContextFile]:
    """Discover context files in priority order."""
    filenames = ["AGENTS.md", "CLAUDE.md"]  # Priority order
    results = []

    for filename in filenames:
        file_path = PROJECT_ROOT / filename

        # Initialize ContextFile
        context_file = ContextFile(filename=filename)

        # Check existence
        if not file_path.exists():
            context_file.exists = False
            context_file.readable = False
            results.append(context_file)
            continue

        context_file.exists = True
        context_file.size_bytes = file_path.stat().st_size

        # Check readability and read content
        try:
            context_file.content = file_path.read_text(encoding="utf-8")
            context_file.readable = True
        except PermissionError as e:
            context_file.readable = False
            context_file.error = f"Permission denied: {e}"
        except UnicodeDecodeError as e:
            context_file.readable = False
            context_file.error = f"Invalid UTF-8 encoding: {e}"
        except Exception as e:
            context_file.readable = False
            context_file.error = f"Read error: {e}"

        results.append(context_file)

    return results
```

### Response Generation

```python
def generate_response(files: List[ContextFile]) -> ContextFilesResponse:
    """Generate response from discovered files."""
    total_found = sum(1 for f in files if f.exists and f.readable)

    # Generate message
    if total_found == 0:
        if any(f.exists and not f.readable for f in files):
            message = f"Found 0 of {len(files)} context files (some exist but not readable)"
        else:
            message = "No context files found in PROJECT_ROOT"
    elif total_found == len(files):
        message = f"Found {total_found} of {len(files)} context files"
    else:
        message = f"Found {total_found} of {len(files)} context files"

    return ContextFilesResponse(
        files=files,
        message=message,
        total_found=total_found
    )
```

## Invariants

1. **File Order Invariant**: Files in response must always be in priority order (AGENTS.md before CLAUDE.md)
2. **Existence-Size Invariant**: If `exists == True`, then `size_bytes` must not be None
3. **Readability-Content Invariant**: If `readable == False`, then `content` must be None
4. **Count Invariant**: `total_found` must equal count of files with `exists == True` and `readable == True`
5. **Filename Invariant**: Only "AGENTS.md" and "CLAUDE.md" filenames are valid

## Performance Characteristics

- **Time Complexity**: O(1) - checks exactly 2 files, no loops or recursion
- **Space Complexity**: O(n) where n = total size of readable files (max ~2MB for two 1MB files)
- **File I/O**: Exactly 2 stat() calls + 0-2 read_text() calls
- **Expected Response Time**: <100ms for typical context files (<100KB)

## Data Flow Diagram

```
Input: None (uses PROJECT_ROOT from config)
  ↓
[Discover AGENTS.md] → ContextFile(filename="AGENTS.md", ...)
  ↓
[Discover CLAUDE.md] → ContextFile(filename="CLAUDE.md", ...)
  ↓
[Generate Response] → ContextFilesResponse(files=[...], message=..., total_found=...)
  ↓
Output: JSON response to MCP client
```

## Testing Considerations

### Test Data Setup
- Create test PROJECT_ROOT with various file combinations
- Test files with different sizes (empty, small, large)
- Test files with permission restrictions
- Test files with encoding issues

### Validation Points
- Verify file order in response (AGENTS.md always first)
- Verify count accuracy (total_found matches actual readable files)
- Verify error messages are descriptive
- Verify security (cannot read files outside PROJECT_ROOT)
- Verify performance (response time <1s)

### Edge Cases to Test
- Empty files (0 bytes)
- Large files (>1MB) - verify warning logged
- Non-UTF-8 files - verify error handling
- Missing permission - verify graceful failure
- PROJECT_ROOT not set - verify configuration error

## Status

- [x] Entities defined with attributes and constraints
- [x] Validation rules documented
- [x] State transitions specified
- [x] Relationships identified
- [x] Domain logic algorithms defined
- [x] Invariants established
- [x] Performance characteristics analyzed
- [x] Data flow documented
- [x] Testing considerations outlined

**Next Phase**: Generate API contracts (OpenAPI/JSON Schema)
