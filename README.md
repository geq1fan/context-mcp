# Context MCP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/geq1fan/context-mcp/workflows/Tests/badge.svg)](https://github.com/geq1fan/context-mcp/actions)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **MCP Server for Project Context Integration**
>
> Provide AI agents with secure, read-only filesystem operations to analyze and understand project codebases.

**Quick Links**: 📖 [Configuration Guide](CONFIGURATION.md) | 🚀 [Quick Start](#quick-start) | 🐛 [Troubleshooting](CONFIGURATION.md#troubleshooting-configuration) | 🤝 [Contributing](CONTRIBUTING.md)

## Quick Start

### 1. Install context-mcp
```bash
# No installation needed with uvx!
# Just configure in Claude Desktop (see step 2)
```

### 2. Configure Claude Desktop

Edit your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:
```json
{
  "mcpServers": {
    "context-mcp": {
      "command": "uvx",
      "args": ["context-mcp"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Look for the 🔌 icon to confirm the server is connected.

### 4. Try it out!

In Claude Desktop, try:
```
Please list the files in my project root directory
```

or

```
Search for "TODO" comments in Python files
```

**Need more details?** See the [Complete Configuration Guide](CONFIGURATION.md)

## Features

**10 MCP Tools** organized in 3 categories:

- **Navigation** (2): `list_directory`, `show_tree`
- **Search** (4): `search_in_file`, `search_in_files`, `find_files_by_name`, `find_recently_modified_files`
- **Read** (4): `read_entire_file`, `read_file_lines`, `read_file_tail`, `read_files`

For detailed tool documentation, see [CONFIGURATION.md](CONFIGURATION.md).

## Installation & Configuration

**Simple 3-step setup:**

1. **No installation needed** - uses `uvx` to run directly
2. **Configure Claude Desktop** - add to `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "context-mcp": {
         "command": "uvx",
         "args": ["context-mcp"],
         "env": {
           "PROJECT_ROOT": "/absolute/path/to/your/project"
         }
       }
     }
   }
   ```
3. **Restart Claude Desktop** - look for 🔌 icon

📖 **Detailed configuration**: See [CONFIGURATION.md](CONFIGURATION.md) for:
- Platform-specific setup (macOS/Windows/Linux)
- Multiple project configuration
- Local development setup
- Troubleshooting guide

## Security

- **Read-Only Operations**: No write, modify, or delete capabilities
- **Path Validation**: All paths restricted to configured PROJECT_ROOT
- **Binary File Protection**: Refuses to read binary files as text
- **Permission Handling**: Graceful handling of permission errors

## Common Issues

**Quick fixes for common problems:**

| Issue | Solution |
|-------|----------|
| Server not showing in Claude | Verify JSON syntax, check `uvx context-mcp` works, restart Claude Desktop |
| `PROJECT_ROOT not set` | Add `PROJECT_ROOT` to env config (must be absolute path) |
| Search timeouts | Increase `SEARCH_TIMEOUT` or install `ripgrep` |
| Permission denied | Check file permissions, grant necessary access |
| Binary file errors | Expected behavior - only text files supported |

📖 **Full troubleshooting guide**: See [CONFIGURATION.md#troubleshooting-configuration](CONFIGURATION.md#troubleshooting-configuration)

## Development

**Quick start for contributors:**

```bash
# Clone and setup
git clone https://github.com/geq1fan/context-mcp.git
cd context-mcp
uv sync

# Run tests
PROJECT_ROOT=$(pwd) uv run pytest

# Run with coverage
PROJECT_ROOT=$(pwd) uv run pytest --cov=agent_mcp
```

**Test coverage**: 121 tests (61 contract + 28 integration + 32 unit) with 99.2% coverage

📖 **Full development guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Documentation

- **[README.md](README.md)** - This file, quick start and overview
- **[CONFIGURATION.md](CONFIGURATION.md)** - Detailed configuration and troubleshooting
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and guidelines
- **[SECURITY.md](SECURITY.md)** - Security policy and reporting
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[LICENSE](LICENSE)** - MIT License text

## Requirements

- Python 3.11 or higher
- (Optional) ripgrep for faster searches

## License

**MIT License** - Copyright (c) 2025 Context MCP Team

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ No warranty provided
- ⚠️ No liability accepted

## Contributing

We welcome contributions! 🎉

**Quick contribution guide:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`PROJECT_ROOT=$(pwd) uv run pytest`)
5. Submit a pull request

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)

## Support & Community

- **Issues**: [GitHub Issues](https://github.com/geq1fan/context-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/geq1fan/context-mcp/discussions)
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

---

**Built with** [FastMCP](https://github.com/jlowin/fastmcp) • **Made for** [Claude Desktop](https://claude.ai/desktop) • **Powered by** [MCP](https://modelcontextprotocol.io/)
