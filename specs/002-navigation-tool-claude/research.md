# Research: Navigation Tool - Project Context Reader

**Feature**: 002-navigation-tool-claude
**Date**: 2025-10-03
**Status**: Complete

## Research Summary

All technical decisions were resolved during specification phase through market research on AI agent context file standards. No additional research required as feature extends existing, well-established navigation tools.

## Decision 1: Supported Context File Names

**Decision**: Support exactly two files - AGENTS.md and CLAUDE.md

**Rationale**:
- **AGENTS.md**: Universal standard formalized in August 2025, adopted by 20,000+ open-source projects
- **CLAUDE.md**: Claude Code specific configuration file, well-documented and widely used
- These two files cover the majority of AI agent use cases
- Limiting to 2 files keeps implementation simple and maintainable

**Alternatives Considered**:
- **.cursorrules** / **.cursor/rules/*.mdc** - Cursor AI specific, different format (not markdown)
- **.github/copilot-instructions.md** - GitHub Copilot specific, different location pattern
- **.aider.conf.yml** - Aider AI specific, YAML format instead of markdown
- **.windsurfrules.md** - Windsurf IDE specific, less adoption
- **AI.md / AI_INSTRUCTIONS.md** - Generic but no standard adoption

**Why Alternatives Rejected**:
- Non-markdown formats (YAML, JSON) require different parsing
- IDE-specific files in subdirectories (.github/, .cursor/) would complicate discovery logic
- User explicitly requested to limit scope to AGENTS.md and CLAUDE.md after initial research

## Decision 2: File Priority Order

**Decision**: AGENTS.md (priority 1) → CLAUDE.md (priority 2)

**Rationale**:
- AGENTS.md is the newer universal standard (2025) designed for cross-agent compatibility
- CLAUDE.md is tool-specific, should defer to universal standard when both exist
- Priority order allows agents to prefer universal instructions while falling back to tool-specific

**Alternatives Considered**:
- CLAUDE.md first (tool-specific priority)
- No priority (alphabetical)
- Merge contents of both files

**Why Alternatives Rejected**:
- Tool-specific priority contradicts industry trend toward universal AGENTS.md
- No priority order provides no guidance when both exist
- Merging contents adds complexity and may create conflicting instructions

## Decision 3: Search Location

**Decision**: Check only PROJECT_ROOT directory (no subdirectory traversal)

**Rationale**:
- AGENTS.md and CLAUDE.md conventions specify root location
- Matches existing navigation tools (list_directory, show_tree) behavior
- Reduces security risk and performance cost
- Aligns with how AI agents actually use these files

**Alternatives Considered**:
- Recursive search through all subdirectories
- Check specific subdirectories (.github/, .claude/)
- Support custom path configuration

**Why Alternatives Rejected**:
- Recursive search violates convention (these files belong in root)
- Specific subdirectories only needed for other file types (.github/copilot-instructions.md)
- Custom paths add configuration complexity for no clear benefit

## Decision 4: Response Format

**Decision**: Return structured metadata + file content

**Response Structure**:
```python
{
    "files": [
        {
            "filename": "AGENTS.md",
            "exists": True,
            "readable": True,
            "size_bytes": 1234,
            "content": "# Project Instructions\n..."
        },
        {
            "filename": "CLAUDE.md",
            "exists": False,
            "readable": False,
            "size_bytes": None,
            "content": None
        }
    ],
    "message": "Found 1 of 2 context files"
}
```

**Rationale**:
- Metadata helps agents understand file state without guessing
- Consistent with existing tool response patterns
- Supports partial results (one file found, one missing)
- Clear error messaging when neither file exists

**Alternatives Considered**:
- Return only content (no metadata)
- Return first found file only
- Separate tool calls for each file

**Why Alternatives Rejected**:
- No metadata requires agents to make assumptions about missing files
- First-only approach loses information when both exist
- Separate tools unnecessarily complicate the interface

## Decision 5: Error Handling Strategy

**Decision**: Non-existence is not an error; return structured empty result

**Behavior**:
- No files found → `{"files": [...], "message": "No context files found"}`
- Permission denied → `{"error": "Cannot read AGENTS.md: permission denied"}`
- Encoding error → `{"error": "Cannot decode AGENTS.md: invalid UTF-8"}`

**Rationale**:
- Projects without context files are valid (not all projects have them)
- Non-error response for missing files reduces noise in agent logs
- Actual errors (permissions, encoding) should be clearly reported

**Alternatives Considered**:
- Throw exception when no files found
- Return null/empty string for missing files
- Log warnings instead of returning messages

**Why Alternatives Rejected**:
- Exceptions for missing files would treat valid state as error
- Null responses provide no helpful information to agents
- Log warnings aren't visible to calling agents

## Technical Implementation Notes

### Reuse Existing Components
- **PathValidator** (agent_mcp/validators/path_validator.py): Security checks
- **config.PROJECT_ROOT** (agent_mcp/config.py): Base directory
- **logger** (agent_mcp/utils/logger.py): Structured logging
- **FastMCP decorator** (server.py): MCP tool registration

### Implementation Pattern
Follow existing navigation tools pattern from `list_directory()` and `show_tree()`:

1. Validate PROJECT_ROOT is configured
2. Construct absolute paths for each filename
3. Use PathValidator to ensure paths are within PROJECT_ROOT
4. Check file existence with pathlib.Path.exists()
5. Read files with UTF-8 encoding, handle errors gracefully
6. Return structured dict response

### Security Considerations
- ✅ Path traversal protection via PathValidator.validate_path()
- ✅ Read-only operations (no file writing)
- ✅ PROJECT_ROOT boundary enforcement
- ✅ No arbitrary filename input (hardcoded to AGENTS.md and CLAUDE.md)

## Research Status

- [x] Market research on AI agent context files completed
- [x] File naming conventions documented
- [x] Priority order established
- [x] Response format designed
- [x] Error handling strategy defined
- [x] Security approach validated
- [x] Implementation pattern identified

**Outcome**: All unknowns resolved. Ready for Phase 1 (Design & Contracts).
