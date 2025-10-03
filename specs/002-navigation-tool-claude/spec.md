# Feature Specification: Navigation Tool - Project Context Reader

**Feature Branch**: `002-navigation-tool-claude`
**Created**: 2025-10-03
**Status**: Draft
**Input**: User description: "Navigation新增tool：查看项目的CLAUDE.md或AGENT.md(需要调研主流的agent使用的文件分别叫什么)"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature: Add MCP tool to read project context files
2. Extract key concepts from description
   → Actors: AI Agents, MCP Server
   → Actions: Find, Read, Return context files
   → Data: AGENTS.md, CLAUDE.md file contents
   → Constraints: Read-only, PROJECT_ROOT scope
3. For each unclear aspect:
   → ✅ File naming confirmed via research (AGENTS.md, CLAUDE.md)
   → ✅ Priority order determined (AGENTS.md first)
4. Fill User Scenarios & Testing section
   → SUCCESS: Clear user flows identified
5. Generate Functional Requirements
   → SUCCESS: All requirements testable
6. Identify Key Entities
   → SUCCESS: Context File entity defined
7. Run Review Checklist
   → SUCCESS: No implementation details, business-focused
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
As an AI Agent using the MCP server, I need to access project-specific context and configuration instructions stored in standardized files (AGENTS.md or CLAUDE.md), so that I can understand project conventions, coding standards, and behavioral guidelines before performing any operations.

**Context**: Different AI coding assistants use different convention files:
- AGENTS.md: Universal standard adopted by 20,000+ projects (August 2025)
- CLAUDE.md: Claude Code specific configuration file

The MCP server should provide a unified way to discover and read these files.

### Acceptance Scenarios

1. **Given** PROJECT_ROOT contains AGENTS.md file, **When** agent calls read_project_context tool, **Then** system returns AGENTS.md content with metadata
2. **Given** PROJECT_ROOT contains only CLAUDE.md file, **When** agent calls read_project_context tool, **Then** system returns CLAUDE.md content with metadata
3. **Given** PROJECT_ROOT contains both files, **When** agent calls read_project_context tool, **Then** system returns both files with AGENTS.md listed first (priority order)
4. **Given** PROJECT_ROOT contains neither file, **When** agent calls read_project_context tool, **Then** system returns empty result with helpful message indicating no context files found
5. **Given** context file exists but is empty, **When** agent calls read_project_context tool, **Then** system returns file metadata with empty content (not an error)

### Edge Cases

- **What happens when** context file exists but is not readable due to permissions?
  → System returns error indicating file exists but cannot be read

- **What happens when** context file is extremely large (>1MB)?
  → System reads and returns entire file (no truncation), but logs warning about size

- **What happens when** context file contains non-UTF-8 characters?
  → System attempts to read with UTF-8, returns encoding error if fails

- **What happens when** PROJECT_ROOT is not set or invalid?
  → System returns error indicating PROJECT_ROOT configuration issue (this is existing behavior)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a new MCP tool named `read_project_context` in the Navigation category
- **FR-002**: System MUST search for exactly two filenames: `AGENTS.md` and `CLAUDE.md` (case-sensitive)
- **FR-003**: System MUST search only in the PROJECT_ROOT directory (not subdirectories)
- **FR-004**: System MUST return results in priority order: AGENTS.md first, then CLAUDE.md
- **FR-005**: System MUST return both files if both exist in PROJECT_ROOT
- **FR-006**: System MUST return file content as plain text without modification
- **FR-007**: System MUST include metadata for each file: filename, existence status, file size (if exists)
- **FR-008**: System MUST return a clear message when no context files are found
- **FR-009**: System MUST perform read-only operations (no file modification or creation)
- **FR-010**: System MUST validate that returned files are within PROJECT_ROOT path (security check)
- **FR-011**: System MUST handle file permission errors gracefully with descriptive messages
- **FR-012**: Tool MUST complete within standard timeout (60 seconds, consistent with other navigation tools)

### Key Entities

- **Context File**: A markdown file containing project-specific instructions for AI agents
  - Attributes: filename (AGENTS.md or CLAUDE.md), content (text), size (bytes), exists (boolean), readable (boolean)
  - Location: Must be in PROJECT_ROOT directory
  - Format: Plain text markdown, UTF-8 encoded
  - Purpose: Provide project conventions, coding standards, and behavioral guidelines to AI agents
  - Relationships: One PROJECT_ROOT can have zero, one, or two context files

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (file found/not found, content returned)
- [x] Scope is clearly bounded (only 2 filenames, only PROJECT_ROOT)
- [x] Dependencies identified (requires PROJECT_ROOT configuration)

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted (actors, actions, data, constraints)
- [x] Ambiguities resolved via research
- [x] User scenarios defined (5 acceptance scenarios + 4 edge cases)
- [x] Requirements generated (12 functional requirements)
- [x] Entities identified (Context File entity)
- [x] Review checklist passed (business-focused, testable, bounded)

---
