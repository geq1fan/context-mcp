<!--
SYNC IMPACT REPORT - Constitution v1.0.0
Version: NEW → 1.0.0 (Initial constitution)
Ratified: 2025-10-03 | Last Amended: 2025-10-04

Changes:
- Created initial constitution with 5 core principles
- Established Security First, TDD, Three-Layer Testing, Simplicity, Performance principles
- Added Technical Standards and Development Workflow sections
- Defined governance and amendment procedures

Templates Status:
✅ plan-template.md - Constitution Check section compatible
✅ spec-template.md - No changes required (no direct dependencies)
✅ tasks-template.md - TDD principles align with Principle II
⚠️ Follow-up: Ensure all future plans reference this constitution version

Deferred Items: None
-->

# Context MCP Constitution

## Core Principles

### I. Security First (NON-NEGOTIABLE)

**All operations MUST be read-only and secure**

- MCP server MUST NOT provide write, modify, or delete capabilities
- All file paths MUST be validated and restricted to PROJECT_ROOT using `Path.resolve()`
- Binary file detection MUST use NULL byte checking before text operations
- Permission errors MUST be handled gracefully with clear error messages
- Directory traversal attacks MUST be prevented through path normalization

**Rationale**: As an MCP server providing AI agents access to codebases, security is paramount.
Any breach could compromise user projects. Read-only operations with strict path validation
ensure the server cannot be exploited to modify or exfiltrate data outside intended boundaries.

### II. Test-Driven Development (NON-NEGOTIABLE)

**TDD cycle is mandatory for all feature development**

- Tests MUST be written BEFORE implementation
- Tests MUST fail initially (Red phase)
- Implementation MUST make tests pass (Green phase)
- Code MUST be refactored while keeping tests green (Refactor phase)
- No production code without corresponding tests
- Test coverage MUST be maintained at 95%+ (current: 99.2%)

**Rationale**: TDD ensures correctness by design, prevents regression, and serves as living
documentation. For an MCP server where AI agents depend on consistent behavior, failing tests
immediately reveal breaking changes before they reach production.

### III. Three-Layer Testing

**Testing strategy MUST follow contract → integration → unit hierarchy**

- **Contract Tests** (`tests/contract/`): Verify MCP protocol compliance
  - JSON Schema validation for all tool inputs/outputs
  - Error code consistency
  - Protocol specification adherence
- **Integration Tests** (`tests/integration/`): End-to-end workflows
  - Complete user scenarios (e.g., search → read → analyze)
  - Tool interaction patterns
  - Cross-platform compatibility (Windows/Linux/macOS)
- **Unit Tests** (`tests/unit/`): Component isolation
  - Individual function correctness
  - Edge case handling
  - Mock external dependencies

**Rationale**: Three-layer testing provides defense in depth. Contract tests ensure MCP
clients can rely on stable interfaces. Integration tests verify real-world usage patterns.
Unit tests catch logic errors early. This structure supports confident refactoring.

### IV. Simplicity & Maintainability

**Code MUST be simple, clear, and maintainable**

- Functions MUST do one thing well
- Maximum nesting depth: 3 levels
- Prefer explicit over clever code
- Use type hints for all public APIs
- Write docstrings (Google style) for all public functions
- Maximum line length: 100 characters (flexible for readability)
- No premature optimization - clarity first, then optimize if needed

**Rationale**: Simple code reduces bugs, eases onboarding, and enables AI agents to understand
and suggest improvements. Complex abstractions make maintenance costly and error-prone.

### V. Performance with Fallback Strategy

**Optimize for performance while ensuring universal compatibility**

- High-performance tools (ripgrep, fd) MUST be preferred when available
- MUST provide automatic fallback to standard tools (grep, find)
- MUST provide Python implementation as final fallback
- Tool detection MUST be transparent (logged at startup)
- Timeout controls MUST prevent hanging operations (default: 60s)
- Performance degradation MUST be acceptable, not failure

**Fallback Hierarchy**:
1. High-performance tools (ripgrep: 13x faster, fd: 9x faster)
2. Standard Unix tools (grep, find)
3. Python native implementation (guaranteed to work)

**Rationale**: Performance matters for large codebases (1000+ files), but compatibility
matters more. The fallback strategy ensures the MCP server works everywhere while being
fast where possible. Users get best performance without installation friction.

## Technical Standards

### Language & Runtime
- **Python Version**: 3.11+ (required for modern type hints and performance)
- **Dependency Management**: uv for development, uvx for distribution
- **Package Distribution**: PyPI with uvx zero-install deployment
- **Framework**: FastMCP for MCP protocol implementation

### Code Quality Tools
- **Linter**: ruff (replaces flake8, black, isort)
- **Type Checker**: mypy (strict mode for new code)
- **Test Runner**: pytest with coverage reporting
- **Format**: ruff format (compatible with Black)

### MCP Tool Design
- All tools MUST use `@mcp.tool()` decorator
- Input parameters MUST have type hints and descriptions
- Return values MUST match documented schemas in `contracts/`
- Error handling MUST use specific exception types from `context_mcp/__init__.py`
- Tool names MUST be snake_case and descriptive (e.g., `search_in_files`)

### Security Requirements
- Path validation MUST use `PathValidator.validate()`
- Binary detection MUST use `FileDetector.is_binary()`
- Subprocess execution MUST use `timeout` parameter
- Environment variables MUST be validated in `config.py`
- No shell=True in subprocess calls (prevents injection)

## Development Workflow

### Git & Branching
- Main branch: `main` (protected)
- Feature branches: `NNN-feature-name` (e.g., `001-agent-mcp-md`, `003-rg-fd-eza`)
- Commit messages: Conventional Commits (feat, fix, docs, style, refactor, test, chore)
- All commits MUST pass CI before merge

### Pull Request Requirements
- All tests MUST pass (contract + integration + unit)
- Code coverage MUST not decrease
- Ruff linting MUST pass (both check and format)
- At least one approval required from maintainers
- PR title MUST follow Conventional Commits format
- PR description MUST include:
  - What changed and why
  - Testing performed
  - Breaking changes (if any)

### Code Review Focus
- **Security**: Path handling, binary detection, subprocess usage
- **Testing**: Coverage, edge cases, contract compliance
- **Simplicity**: Unnecessary complexity, deep nesting
- **Performance**: Fallback strategy, timeout handling
- **Documentation**: Docstrings, README updates, CHANGELOG.md

### Release Process
- Version bumping: Semantic Versioning (MAJOR.MINOR.PATCH)
- CHANGELOG.md MUST be updated before release
- Git tags: `vX.Y.Z` format
- PyPI publishing: Automated via GitHub Actions
- GitHub Release: Include changelog excerpt and migration notes

## Governance

### Amendment Procedure
1. **Proposal**: Open GitHub Issue with `constitution` label
   - Describe principle change or addition
   - Provide rationale and examples
   - Identify affected templates and code
2. **Discussion**: Community review (minimum 7 days)
3. **Vote**: Maintainers approve/reject with justification
4. **Implementation**:
   - Update constitution.md with version bump
   - Update affected templates (plan, spec, tasks)
   - Update agent-specific files (CLAUDE.md, etc.)
   - Document in Sync Impact Report (HTML comment at top)
5. **Migration**: Create migration guide if breaking changes

### Version Bumping Rules
- **MAJOR**: Principle removal, backward-incompatible governance changes
- **MINOR**: New principle added, section materially expanded
- **PATCH**: Clarifications, wording improvements, typo fixes, examples added

### Compliance Review
- All `/plan` executions MUST check Constitution compliance
- All PRs MUST verify adherence to core principles
- Complexity deviations MUST be documented in `plan.md` Complexity Tracking
- Violations without justification MUST block merge

### Living Document
This constitution is a living document. Amendments follow the procedure above. When in doubt:
1. Prioritize security over convenience
2. Prioritize simplicity over cleverness
3. Prioritize compatibility over performance
4. Prioritize tests over features

**Reference this document in**:
- `.specify/templates/plan-template.md` → Constitution Check section
- `.specify/templates/tasks-template.md` → Task generation rules
- `CLAUDE.md` and other agent guidance files → Core principles reminder

**Version**: 1.0.0 | **Ratified**: 2025-10-03 | **Last Amended**: 2025-10-04
