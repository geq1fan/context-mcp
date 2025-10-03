# Implementation Plan: Navigation Tool - Project Context Reader

**Branch**: `002-navigation-tool-claude` | **Date**: 2025-10-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `C:\Users\Ge\Documents\github\agent-mcp\specs\002-navigation-tool-claude\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Add a new MCP tool `read_project_context` to the Navigation category that discovers and reads AI agent context files (AGENTS.md and CLAUDE.md) from PROJECT_ROOT. The tool will return file content with metadata in priority order (AGENTS.md first), enabling AI agents to understand project-specific conventions, coding standards, and behavioral guidelines before performing operations.

## Technical Context
**Language/Version**: Python 3.11+ (existing codebase requirement)
**Primary Dependencies**: fastmcp>=0.1.0, pathlib (stdlib), chardet>=5.0.0 (existing)
**Storage**: Filesystem (read-only access to PROJECT_ROOT)
**Testing**: pytest with contract/integration/unit test structure (existing pattern)
**Target Platform**: Cross-platform (Windows/Linux/macOS - MCP server)
**Project Type**: single (MCP server library with CLI entry point)
**Performance Goals**: <1s response time for file discovery and read operations
**Constraints**: Read-only operations, must stay within PROJECT_ROOT, UTF-8 encoding, max file size warning at 1MB
**Scale/Scope**: Small feature - 1 new tool, 2 filenames to check, extends existing navigation tools

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file is a template. Using existing project patterns as constitutional principles.

### Existing Project Patterns (Constitutional)
- ✅ **Library-First**: Feature implemented as library function in `agent_mcp/tools/navigation.py`
- ✅ **MCP Tool Pattern**: Exposed via FastMCP decorator in `server.py`
- ✅ **Three-Layer Testing**: Contract + Integration + Unit tests required
- ✅ **Path Security**: Use existing `PathValidator` from `agent_mcp/validators/`
- ✅ **Error Handling**: Follow existing tool patterns with structured error responses
- ✅ **Config-Based**: Use existing `config.py` for PROJECT_ROOT access

### Constitutional Compliance
| Principle | Status | Notes |
|-----------|--------|-------|
| Extends existing navigation tools | ✅ PASS | Adds to `tools/navigation.py` |
| Uses established security patterns | ✅ PASS | Reuses PathValidator |
| Follows three-layer test structure | ✅ PASS | Contract + Integration + Unit |
| No new external dependencies | ✅ PASS | Uses stdlib pathlib only |
| Read-only operations | ✅ PASS | No file modifications |
| Consistent with existing tools | ✅ PASS | Same patterns as list_directory, show_tree |

**Initial Check**: ✅ PASS - No violations detected

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
agent_mcp/
├── tools/
│   ├── navigation.py        # [MODIFY] Add read_project_context() function
│   ├── search.py            # [NO CHANGE]
│   └── read.py              # [NO CHANGE]
├── validators/
│   └── path_validator.py    # [REUSE] Existing security validation
├── utils/
│   ├── logger.py            # [REUSE] Existing logging
│   └── file_detector.py     # [REUSE] Existing binary detection
├── config.py                # [REUSE] Existing PROJECT_ROOT config
└── server.py                # [MODIFY] Register new MCP tool

tests/
├── contract/
│   └── test_navigation_contract.py    # [MODIFY] Add read_project_context tests
├── integration/
│   ├── test_full_workflow.py          # [MODIFY] Add context file scenarios
│   └── test_edge_cases.py             # [MODIFY] Add edge case tests
└── unit/
    └── test_navigation_unit.py        # [CREATE] Unit tests for helper functions
```

**Structure Decision**: Single project (MCP server library). This feature extends the existing Navigation tools category by adding one new tool function to `agent_mcp/tools/navigation.py` and registering it in `server.py`. All existing infrastructure (validators, config, logging) will be reused. Tests follow the established three-layer pattern (contract/integration/unit).

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. **Contract Tests First** (TDD Principle):
   - Create contract test for read_project_context tool
   - Implement 8 test cases from contract JSON
   - Tests should FAIL initially (no implementation yet)

2. **Unit Tests for Helpers**:
   - Test context file discovery logic
   - Test path validation integration
   - Test error handling scenarios

3. **Implementation Tasks**:
   - Add read_project_context() function to agent_mcp/tools/navigation.py
   - Register MCP tool in server.py
   - Implement security validation using existing PathValidator

4. **Integration Tests**:
   - Add scenarios to test_full_workflow.py
   - Add edge cases to test_edge_cases.py
   - Test tool via MCP client

**Task Dependencies**:
```
Contract Tests [P]
    ↓
Unit Tests [P]
    ↓
Implementation (navigation.py) → Implementation (server.py)
    ↓
Integration Tests
    ↓
Validation (run quickstart scenarios)
```

**Ordering Strategy**:
- TDD order: All tests before implementation
- Mark [P] for parallel execution (independent test files)
- Implementation tasks sequential (navigation.py before server.py)
- Integration tests after implementation complete

**File Modifications**:
- **CREATE**: tests/unit/test_navigation_unit.py (~150 lines)
- **MODIFY**: tests/contract/test_navigation_contract.py (+80 lines)
- **MODIFY**: tests/integration/test_full_workflow.py (+40 lines)
- **MODIFY**: tests/integration/test_edge_cases.py (+60 lines)
- **MODIFY**: agent_mcp/tools/navigation.py (+60 lines)
- **MODIFY**: agent_mcp/server.py (+15 lines)

**Estimated Output**: 12-15 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md generated
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, CLAUDE.md generated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - documented above
- [ ] Phase 3: Tasks generated (/tasks command) - NOT YET EXECUTED
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - No violations, extends existing patterns
- [x] Post-Design Constitution Check: PASS - Design follows established architecture
- [x] All NEEDS CLARIFICATION resolved - No unknowns in Technical Context
- [x] Complexity deviations documented - No deviations, Complexity Tracking section empty

**Generated Artifacts**:
- [x] specs/002-navigation-tool-claude/research.md
- [x] specs/002-navigation-tool-claude/data-model.md
- [x] specs/002-navigation-tool-claude/contracts/read_project_context.json
- [x] specs/002-navigation-tool-claude/contracts/README.md
- [x] specs/002-navigation-tool-claude/quickstart.md
- [x] CLAUDE.md (updated with new feature context)
- [x] specs/002-navigation-tool-claude/plan.md (this file)

**Next Command**: `/tasks` - Generate tasks.md with implementation steps

---
*Based on existing project patterns - Constitution template not yet initialized*
