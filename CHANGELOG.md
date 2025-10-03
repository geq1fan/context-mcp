# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New MCP tool `read_project_context` to discover and read AI agent context files (AGENTS.md and CLAUDE.md)
- Support for project-specific agent instructions with priority ordering (AGENTS.md first, then CLAUDE.md)
- Comprehensive error handling for missing files, permission errors, and encoding issues in context file reading
- Warning logging for large context files (>1MB) to improve performance awareness

### Changed
- Package renamed to `context-mcp` (PyPI package name `agent-mcp` was unavailable)
- Executable script is now `context-mcp`
- All documentation and configuration updated to use `uvx context-mcp`

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
agent_mcp/
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

[0.1.0]: https://github.com/geq1fan/context-mcp/releases/tag/v0.1.0
