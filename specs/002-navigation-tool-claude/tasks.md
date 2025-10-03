# Tasks: Navigation Tool - Project Context Reader

**Feature**: 002-navigation-tool-claude
**Branch**: `002-navigation-tool-claude`
**Input**: Design documents from `C:\Users\Ge\Documents\github\agent-mcp\specs\002-navigation-tool-claude\`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Summary

This feature adds the `read_project_context` MCP tool to discover and read AI agent context files (AGENTS.md and CLAUDE.md) from PROJECT_ROOT. Implementation follows TDD principles with contract tests first, then implementation, then integration tests.

**Tech Stack**: Python 3.11+, fastmcp, pytest
**Files Modified**: 6 (2 new, 4 modified)
**Estimated Time**: 2-3 hours including tests

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths are absolute from repository root

---

## Phase 3.1: Setup & Environment

- [x] **T001** Verify Python 3.11+ and dependencies installed
  - Run: `python --version` (must be ≥3.11)
  - Run: `uv sync` to install dependencies (fastmcp, pytest, pytest-mock)
  - Verify: `pytest --version` works
  - Verify: PROJECT_ROOT environment variable is set

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE PHASE 3.3

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation in Phase 3.3

### Contract Tests

- [x] **T002 [P]** Create contract test for `read_project_context` in `tests/contract/test_navigation_contract.py`
  - Add import: `from agent_mcp.tools.navigation import read_project_context`
  - Implement test class: `TestReadProjectContextContract`
  - Load contract from: `specs/002-navigation-tool-claude/contracts/read_project_context.json`
  - Implement 8 test cases from contract:
    1. `test_both_files_exist` - Both AGENTS.md and CLAUDE.md present
    2. `test_only_agents_md_exists` - Only AGENTS.md present
    3. `test_only_claude_md_exists` - Only CLAUDE.md present
    4. `test_no_files_exist` - Neither file present
    5. `test_empty_file` - AGENTS.md exists but empty
    6. `test_permission_denied` - File exists but not readable
    7. `test_invalid_encoding` - File has non-UTF-8 bytes
    8. `test_large_file` - File >1MB (warning logged)
  - Use `tmp_path` fixture for test PROJECT_ROOT
  - Use `monkeypatch` to override config.PROJECT_ROOT
  - Verify output matches JSON Schema from contract
  - **Expected**: All tests FAIL with ImportError or AttributeError (read_project_context doesn't exist yet)
  - Mark test with `@pytest.mark.contract`
  - Approximate size: 250 lines

### Unit Tests

- [x] **T003 [P]** Create unit tests in `tests/unit/test_navigation_unit.py` (NEW FILE)
  - Test helper function: `_discover_context_file(filename: str, project_root: Path) -> dict`
  - Test cases:
    1. `test_discover_file_exists_and_readable` - Happy path
    2. `test_discover_file_not_exists` - File missing
    3. `test_discover_file_permission_denied` - PermissionError handling
    4. `test_discover_file_invalid_utf8` - UnicodeDecodeError handling
    5. `test_discover_file_path_validation` - PathValidator integration
    6. `test_discover_file_size_warning` - Large file warning logged
  - Test response generation: `_generate_response(files: List[dict]) -> dict`
  - Test cases:
    1. `test_generate_response_all_found` - total_found=2
    2. `test_generate_response_partial` - total_found=1
    3. `test_generate_response_none_found` - total_found=0
    4. `test_generate_response_exists_not_readable` - Special message
  - Use pytest fixtures and mocks
  - **Expected**: All tests FAIL (helper functions don't exist yet)
  - Mark test with `@pytest.mark.unit`
  - Approximate size: 200 lines

### Integration Test Setup

- [x] **T004 [P]** Add context file scenarios to `tests/integration/test_full_workflow.py`
  - Add test class: `TestContextFileWorkflow`
  - Test case: `test_read_context_files_full_workflow`
    - Setup: Create test AGENTS.md and CLAUDE.md
    - Call: `read_project_context()` via MCP client
    - Assert: Response has both files with correct content
    - Verify: Files ordered by priority (AGENTS.md first)
  - Test case: `test_context_files_missing_graceful_handling`
    - Setup: No context files in PROJECT_ROOT
    - Call: `read_project_context()`
    - Assert: Returns empty result with helpful message
  - **Expected**: Tests FAIL (read_project_context doesn't exist)
  - Mark test with `@pytest.mark.integration`
  - Approximate addition: 80 lines

- [x] **T005 [P]** Add edge cases to `tests/integration/test_edge_cases.py`
  - Add test class: `TestContextFileEdgeCases`
  - Test case: `test_context_file_permission_error`
    - Setup: Create AGENTS.md with no read permissions (chmod 000)
    - Call: `read_project_context()`
    - Assert: Returns error message, readable=False
  - Test case: `test_context_file_large_size_warning`
    - Setup: Create AGENTS.md >1MB
    - Call: `read_project_context()`
    - Assert: Content returned, warning logged
  - Test case: `test_context_file_invalid_encoding`
    - Setup: Create CLAUDE.md with invalid UTF-8 bytes
    - Call: `read_project_context()`
    - Assert: Returns encoding error message
  - **Expected**: Tests FAIL (read_project_context doesn't exist)
  - Mark test with `@pytest.mark.integration`
  - Approximate addition: 100 lines

### Verify All Tests Fail

- [x] **T006** Run all new tests and confirm they FAIL
  - Run: `pytest tests/contract/test_navigation_contract.py -v`
  - Run: `pytest tests/unit/test_navigation_unit.py -v`
  - Run: `pytest tests/integration/test_full_workflow.py::TestContextFileWorkflow -v`
  - Run: `pytest tests/integration/test_edge_cases.py::TestContextFileEdgeCases -v`
  - **Expected**: All tests FAIL with ImportError or AttributeError
  - **Outcome**: Red phase of Red-Green-Refactor confirmed ✅
  - **DO NOT PROCEED** to Phase 3.3 until all tests are failing

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

**Prerequisites**: Phase 3.2 complete, all tests failing

### Implementation

- [x] **T007** Implement `read_project_context()` function in `agent_mcp/tools/navigation.py`
  - Add import: `from pathlib import Path`
  - Add import: `from agent_mcp.config import config`
  - Add import: `from agent_mcp.validators.path_validator import PathValidator`
  - Add import: `from agent_mcp.utils.logger import logger`
  - Define helper: `_discover_context_file(filename: str, project_root: Path) -> dict`
    - Check file exists: `file_path = project_root / filename`
    - Validate path: `PathValidator.validate_path(file_path, project_root)`
    - Return dict with: filename, exists, readable, size_bytes, content, error
    - Handle exceptions: PermissionError, UnicodeDecodeError, Exception
    - Log warning if file >1MB: `logger.warning(f"Context file {filename} is large ({size_mb:.1f} MB)")`
  - Define helper: `_generate_response(files: List[dict]) -> dict`
    - Calculate: `total_found = sum(1 for f in files if f["exists"] and f["readable"])`
    - Generate message based on total_found
    - Return: `{"files": files, "message": message, "total_found": total_found}`
  - Define main function: `read_project_context() -> dict`
    - Get PROJECT_ROOT: `project_root = config.project_root`
    - Check PROJECT_ROOT is set: raise ConfigurationError if None
    - Discover files in priority order: `["AGENTS.md", "CLAUDE.md"]`
    - Call `_discover_context_file()` for each filename
    - Generate and return response
  - Add docstring with type hints
  - Approximate addition: 80 lines
  - **Expected**: Unit tests pass, contract tests pass, integration tests pass

- [x] **T008** Register MCP tool in `agent_mcp/server.py`
  - Add import: `from agent_mcp.tools.navigation import read_project_context`
  - Add MCP tool registration after existing navigation tools:
    ```python
    @mcp.tool()
    def mcp_read_project_context() -> dict:
        """Read project context files (AGENTS.md, CLAUDE.md) from PROJECT_ROOT.

        Discovers and reads AI agent context files to understand project-specific
        conventions, coding standards, and behavioral guidelines.

        Returns:
            dict: {
                "files": List[dict],    # Context file metadata and content
                "message": str,          # Human-readable result summary
                "total_found": int       # Count of readable files
            }

        Raises:
            ConfigurationError: If PROJECT_ROOT is not set or invalid
        """
        return read_project_context()
    ```
  - Approximate addition: 20 lines
  - **Expected**: Tool can be called via MCP client

### Verify Implementation

- [x] **T009** Run all tests and verify they PASS
  - Run: `pytest tests/unit/test_navigation_unit.py -v`
  - **Expected**: All unit tests PASS ✅
  - Run: `pytest tests/contract/test_navigation_contract.py::TestReadProjectContextContract -v`
  - **Expected**: All 8 contract tests PASS ✅
  - Run: `pytest tests/integration/ -v -k context`
  - **Expected**: All integration tests PASS ✅
  - **Outcome**: Green phase of Red-Green-Refactor achieved ✅

---

## Phase 3.4: Integration & Validation

- [x] **T010** Run full test suite
  - Run: `pytest tests/ -v`
  - **Expected**: All tests PASS including existing tests (no regressions)
  - Check coverage: `pytest tests/ --cov=agent_mcp --cov-report=term-missing`
  - **Expected**: New code has >80% coverage

- [x] **T011** Manual validation with quickstart scenarios
  - Follow: `specs/002-navigation-tool-claude/quickstart.md`
  - Test Scenario 1: Project with both AGENTS.md and CLAUDE.md
    - Create test files as per quickstart
    - Start MCP server: `uvx agent-mcp`
    - Call tool via MCP client
    - Verify: Response matches expected output from quickstart
  - Test Scenario 2: Project with only AGENTS.md
    - Remove CLAUDE.md
    - Call tool
    - Verify: Response shows 1 found, 1 missing
  - Test Scenario 3: Project with no context files
    - Remove both files
    - Call tool
    - Verify: Response shows "No context files found"
  - **Expected**: All scenarios work as documented

- [x] **T012** Performance validation
  - Create test file: 50KB (typical size)
  - Measure: Tool response time
  - **Expected**: <100ms response time
  - Create test file: 1.5MB (large size)
  - Measure: Tool response time
  - Verify: Warning logged but file returned
  - **Expected**: <1s response time

---

## Phase 3.5: Polish & Documentation

- [x] **T013 [P]** Add inline documentation
  - Review: `agent_mcp/tools/navigation.py`
  - Add: Docstrings for helper functions
  - Add: Type hints for all parameters and returns
  - Add: Comments explaining security validations
  - Verify: Docstrings follow existing tool patterns

- [x] **T014 [P]** Update CHANGELOG.md
  - Add entry under "## [Unreleased]":
    ```markdown
    ### Added
    - New MCP tool `read_project_context` to discover and read AI agent context files (AGENTS.md and CLAUDE.md)
    - Support for project-specific agent instructions with priority ordering (AGENTS.md first, then CLAUDE.md)
    - Comprehensive error handling for missing files, permission errors, and encoding issues
    ```
  - Reference: Feature 002-navigation-tool-claude

- [x] **T015** Verify code quality
  - Run linter (if configured): Check for style violations
  - Run type checker (if configured): Check for type errors
  - Review: Code follows existing patterns in navigation.py
  - Verify: No code duplication
  - Verify: Consistent error handling style

- [x] **T016** Final integration test
  - Start MCP server with actual project CLAUDE.md
  - Call: `read_project_context()` via MCP client
  - Verify: Returns actual project context
  - Test: Tool works in real environment (not just tests)

---

## Dependencies

```
T001 (Setup)
  ↓
T002, T003, T004, T005 (Tests - parallel [P])
  ↓
T006 (Verify tests fail)
  ↓
T007 (Implement navigation.py)
  ↓
T008 (Register in server.py)
  ↓
T009 (Verify tests pass)
  ↓
T010, T011, T012 (Validation - sequential)
  ↓
T013, T014, T015 (Polish - parallel [P])
  ↓
T016 (Final verification)
```

## Parallel Execution Examples

### Phase 3.2: Write All Tests in Parallel
```bash
# Launch T002-T005 together (different files, no dependencies):
Task: "Create contract test in tests/contract/test_navigation_contract.py"
Task: "Create unit tests in tests/unit/test_navigation_unit.py"
Task: "Add scenarios to tests/integration/test_full_workflow.py"
Task: "Add edge cases to tests/integration/test_edge_cases.py"
```

### Phase 3.5: Polish Tasks in Parallel
```bash
# Launch T013-T015 together:
Task: "Add inline documentation to agent_mcp/tools/navigation.py"
Task: "Update CHANGELOG.md with new feature entry"
Task: "Verify code quality and style compliance"
```

---

## File Modification Summary

### New Files (2)
- `tests/unit/test_navigation_unit.py` (~200 lines) - Unit tests for helper functions

### Modified Files (4)
- `tests/contract/test_navigation_contract.py` (+250 lines) - Contract tests for new tool
- `tests/integration/test_full_workflow.py` (+80 lines) - Workflow scenarios
- `tests/integration/test_edge_cases.py` (+100 lines) - Edge case testing
- `agent_mcp/tools/navigation.py` (+80 lines) - Core implementation
- `agent_mcp/server.py` (+20 lines) - MCP tool registration

### Documentation Updated (1)
- `CHANGELOG.md` (+5 lines) - Feature announcement

**Total**: ~730 lines added/modified across 6 files

---

## Validation Checklist

Before marking tasks complete, verify:

### Test Coverage
- [x] Contract test covers all 8 test cases from contract JSON
- [x] Unit tests cover all helper functions with mocks
- [x] Integration tests cover full workflow and edge cases
- [x] All tests follow TDD (written before implementation)

### Implementation Quality
- [x] Function follows existing navigation tool patterns
- [x] Security validation via PathValidator
- [x] Error handling for all edge cases
- [x] Performance meets requirements (<1s response time)
- [x] Logging for warnings (large files)

### Integration
- [x] Tool registered correctly in server.py
- [x] Tool callable via MCP client
- [x] No regressions in existing tests
- [x] Works in real environment (not just tests)

### Documentation
- [x] Inline docstrings with type hints
- [x] CHANGELOG.md updated
- [x] Code quality verified (linting, typing)
- [x] Follows project conventions

---

## Notes

- **TDD Discipline**: Phase 3.2 MUST complete before Phase 3.3. Tests must fail first.
- **Parallel Tasks**: Tasks marked [P] can run concurrently (different files, no dependencies)
- **Security**: All file paths validated via PathValidator to prevent traversal attacks
- **Performance**: File I/O is minimal (2 stat calls + 0-2 read calls), response time <1s
- **Error Handling**: All exceptions caught and returned as structured error messages
- **Testing**: Three-layer testing (contract + integration + unit) ensures comprehensive coverage

---

**Status**: ✅ COMPLETED
**Completion Date**: 2025-10-04
**All Tasks**: 16/16 completed (100%)
**Total Tests**: 149 passed, 5 skipped (platform limitations)
**Code Coverage**: >99%
