# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 2025-10-28

### Fixed
- **Critical Bug**: Fixed `UnboundLocalError` in server startup when `PROJECT_ROOT` environment variable is missing
  - The logger instance was not accessible in exception handlers, causing crashes
  - Now properly handles configuration errors with clear error messages

## [0.2.4] - 2025-10-28

### Security
- Version bump for security fixes

## [0.2.3] - 2025-10-28

### Added
- **Configurable Log Levels**: Added `LOG_LEVEL` environment variable support
  - Supports DEBUG, INFO, WARNING, ERROR, CRITICAL levels
  - Default level changed from INFO to WARNING for cleaner output
  - Configurable via environment variable `LOG_LEVEL=DEBUG`

### Changed
- **Default Log Level**: Changed from INFO to WARNING to reduce log noise
- **Architecture**: Improved logging configuration to be configurable at startup

## [0.2.0] - 2025-10-05

### Added
- **New MCP Tool**: `get_tool_usage_guide` for dynamic documentation generation
  - Returns comprehensive usage documentation for all MCP tools
  - Supports optional filtering by tool names
  - Includes JSON Schema definitions, descriptions, and usage examples
  - Performance optimized (<100ms generation time)
  - Template-based rendering using Jinja2
- Development dependencies: `pytest-asyncio`, `ruff`, `mypy` for improved code quality
- Complete async/await support across all new tool implementations

### Changed
- Updated dependency management from deprecated `tool.uv.dev-dependencies` to `dependency-groups.dev`
- Improved type annotations with full mypy compliance
- Enhanced code formatting with ruff auto-formatting

### Technical Improvements
- **Architecture**: Clean dependency injection pattern to avoid circular imports
  - `schema_extractor.py`: Runtime schema extraction from FastMCP
  - `doc_generator.py`: Markdown rendering via Jinja2 templates
  - `guide.py`: Orchestrates documentation generation
- **No data duplication**: Uses FastMCP's `tool.description` directly
- **Full test coverage**: 193 tests passing (contract/integration/unit)
- **Quality gates**: All ruff checks, mypy type checking, and pytest tests passing

### Fixed
- Resolved circular dependency issues in schema extraction
- Fixed async function signatures across test files
- Corrected mypy type checking errors with proper type annotations

## [0.1.0] - 2025-10-03

### Added

#### Core Features
- **Navigation Tools** (3 tools)
  - `list_directory`: List directory contents with sorting (name, size, time) and pagination
  - `show_tree`: Display directory tree structure with configurable depth limits
  - `read_project_context`: Read AI agent context files from PROJECT_ROOT (NEW in unreleased)

- **Search Tools** (4 tools)
  - `search_in_file`: Search for text/regex in a single file
  - `search_in_files`: Multi-file recursive search with glob patterns and timeout control
  - `find_files_by_name`: Find files by name pattern (supports wildcards)
  - `find_recently_modified_files`: Locate files modified within specified timeframe

- **Read Tools** (4 tools)
  - `read_entire_file`: Read complete file with encoding detection
  - `read_file_lines`: Read specific line ranges
  - `read_file_tail`: Read last N lines (useful for logs)
  - `read_files`: Batch read multiple files with error resilience

#### Security Features
- Path validation with security checks (prevents directory traversal attacks)
- Binary file detection and rejection
- Read-only operations (no write/modify/delete capabilities)
- Permission error handling with clear error messages

#### Documentation
- Comprehensive README with quick start guide
- Complete configuration guide (CONFIGURATION.md)
- Detailed troubleshooting section
- API contracts with JSON Schema definitions
- Design documents (spec.md, plan.md, data-model.md, etc.)

#### Testing
- 149 tests across 3 categories:
  - Contract tests (69 tests) - MCP protocol compliance
  - Integration tests (38 tests) - End-to-end workflows
  - Unit tests (42 tests) - Component testing
- >99% test coverage

#### Developer Experience
- FastMCP framework integration
- Environment-based configuration (PROJECT_ROOT, SEARCH_TIMEOUT)
- Automatic log rotation (7-day retention)
- Ripgrep support for high-performance searches (with grep fallback)
- uvx packaging for zero-installation deployment

#### Configuration
- Claude Desktop integration examples
- Multiple project configuration support
- Platform-specific configuration templates (macOS, Windows, Linux)
- Development and production configuration modes

### Technical Details
- Python 3.11+ support
- FastMCP framework for MCP protocol
- Chardet for encoding detection
- Optional ripgrep integration for performance
- TimedRotatingFileHandler for log management

### Project Structure
```
context_mcp/
├── server.py           # FastMCP server entry point
├── config.py           # Environment variable configuration
├── tools/              # 10 MCP tool implementations
│   ├── navigation.py   # Directory listing and tree
│   ├── search.py       # Search and find operations
│   └── read.py         # File reading operations
├── validators/         # Security validators
└── utils/              # Utilities (file detection, logging)

tests/
├── contract/           # MCP contract tests
├── integration/        # End-to-end workflow tests
└── unit/               # Component unit tests
```

### Known Limitations
- Read-only operations only (by design)
- Requires PROJECT_ROOT environment variable
- Binary files are rejected (text files only)
- Search timeout default is 60 seconds (configurable)

### Future Enhancements
See [GitHub Issues](https://github.com/geq1fan/context-mcp/issues) for planned features.

---

## Release Notes

### v0.1.0 - Initial Release
First public release of Context MCP, providing AI agents with secure, read-only access to project codebases through the Model Context Protocol.

**Highlights**:
- ✅ 11 production-ready MCP tools (including read_project_context in unreleased)
- ✅ Comprehensive security features
- ✅ 149 tests with >99% coverage
- ✅ Complete documentation and configuration guides
- ✅ Claude Desktop integration ready

**Installation**:
```bash
# Add to Claude Desktop config
{
  "mcpServers": {
    "context-mcp": {
      "command": "uvx",
      "args": ["context-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

**Contributors**: Context MCP Team

### v0.2.0 - Tool Documentation Generator

**Highlights**:
- ✅ New `get_tool_usage_guide` MCP tool for self-documenting APIs
- ✅ 193 tests passing with full async support
- ✅ Complete type safety with mypy compliance
- ✅ Clean architecture with dependency injection
- ✅ Production-ready code quality (ruff + mypy)

**What's New**:
The 0.2.0 release adds powerful self-documentation capabilities to Context MCP. The new `get_tool_usage_guide` tool dynamically generates comprehensive documentation from FastMCP runtime metadata, making it easy for AI agents to discover and understand available tools.

**Breaking Changes**: None

**Contributors**: Context MCP Team

[0.2.0]: https://github.com/geq1fan/context-mcp/releases/tag/v0.2.0
[0.1.0]: https://github.com/geq1fan/context-mcp/releases/tag/v0.1.0
