# Agent MCP

**MCP Server for Project Context Integration**

A Model Context Protocol (MCP) server that provides AI agents with read-only filesystem operations to analyze and understand project codebases. Built with FastMCP framework and designed for secure, efficient code exploration.

📖 **[Complete Configuration Guide](CONFIGURATION.md)** | 🚀 **[Quick Start](#quick-start)** | 🔧 **[Troubleshooting](#troubleshooting)**

## Quick Start

### 1. Install agent-mcp
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
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
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

### Navigation Tools (2)
- **list_directory**: List directory contents with sorting (by name, size, time) and pagination
- **show_tree**: Display directory tree structure with configurable depth limits

### Search Tools (4)
- **search_in_file**: Search for text/regex in a single file
- **search_in_files**: Multi-file recursive search with glob patterns and timeout control
- **find_files_by_name**: Find files by name pattern (supports wildcards)
- **find_recently_modified_files**: Locate files modified within specified timeframe

### Read Tools (4)
- **read_entire_file**: Read complete file with encoding detection
- **read_file_lines**: Read specific line ranges
- **read_file_tail**: Read last N lines (useful for logs)
- **read_files**: Batch read multiple files with error resilience

## Installation

### Using uvx (Recommended)
```bash
uvx agent-mcp
```

### Local Development
```bash
# Clone repository
git clone <repository-url>
cd agent-mcp

# Install dependencies with uv
uv sync

# Run server
uv run python -m agent_mcp.server
```

## Configuration

### Required Environment Variables

```bash
# Set project root directory (required)
export PROJECT_ROOT=/path/to/your/project

# Optional: Configure search timeout (default: 60 seconds)
export SEARCH_TIMEOUT=30
```

### Using .env File

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

## MCP Server Configuration

### For Claude Desktop

Add this server configuration to your Claude Desktop config file:

**Location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration**:

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/your/project",
        "SEARCH_TIMEOUT": "60"
      }
    }
  }
}
```

**For local development**:
```json
{
  "mcpServers": {
    "agent-mcp-dev": {
      "command": "uv",
      "args": ["run", "python", "-m", "agent_mcp.server"],
      "cwd": "/path/to/agent-mcp",
      "env": {
        "PROJECT_ROOT": "/path/to/your/project",
        "SEARCH_TIMEOUT": "60"
      }
    }
  }
}
```

### For Other MCP Clients

#### Using stdio transport:
```bash
# Start server in stdio mode (default for FastMCP)
PROJECT_ROOT=/path/to/project uv run python -m agent_mcp.server
```

#### Using SSE transport:
```bash
# Add to server.py if needed:
# mcp.run(transport="sse")
```

### Multiple Project Configuration

You can configure multiple instances for different projects:

```json
{
  "mcpServers": {
    "project-a": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/project-a"
      }
    },
    "project-b": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/project-b",
        "SEARCH_TIMEOUT": "120"
      }
    }
  }
}
```

### Verification

After configuration, restart Claude Desktop and verify:

1. Open Claude Desktop
2. Look for the 🔌 icon indicating MCP servers are connected
3. Try a simple request:
   ```
   Please list the files in the root directory using agent-mcp
   ```

## Usage

### Starting the Server

```bash
# With uvx
PROJECT_ROOT=/path/to/project uvx agent-mcp

# Local development
PROJECT_ROOT=/path/to/project uv run python -m agent_mcp.server
```

### Example MCP Requests

#### List Directory
```json
{
  "tool": "mcp_list_directory",
  "arguments": {
    "path": ".",
    "sort_by": "time",
    "order": "desc",
    "limit": 10
  }
}
```

#### Search in Files
```json
{
  "tool": "mcp_search_in_files",
  "arguments": {
    "query": "def main",
    "file_pattern": "*.py",
    "path": "src",
    "use_regex": false
  }
}
```

#### Read File
```json
{
  "tool": "mcp_read_entire_file",
  "arguments": {
    "file_path": "README.md"
  }
}
```

## Security

- **Read-Only Operations**: No write, modify, or delete capabilities
- **Path Validation**: All paths restricted to configured PROJECT_ROOT
- **Binary File Protection**: Refuses to read binary files as text
- **Permission Handling**: Graceful handling of permission errors

## Troubleshooting

### Common Issues

#### 1. Server Not Showing in Claude Desktop

**Symptoms**: No 🔌 icon or agent-mcp not listed in available servers

**Solutions**:
- Verify config file path is correct
- Check JSON syntax (use a JSON validator)
- Ensure `uvx agent-mcp` works in terminal
- Check Claude Desktop logs:
  - macOS: `~/Library/Logs/Claude/`
  - Windows: `%APPDATA%\Claude\logs\`
- Restart Claude Desktop completely

#### 2. PROJECT_ROOT Error

**Symptoms**: `ValueError: PROJECT_ROOT environment variable not set`

**Solutions**:
```json
// Ensure PROJECT_ROOT is set in config
{
  "mcpServers": {
    "agent-mcp": {
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/project"  // Must be absolute path
      }
    }
  }
}
```

**Windows users**: Use forward slashes or escaped backslashes:
```json
"PROJECT_ROOT": "C:/Users/YourName/Projects/myproject"
// or
"PROJECT_ROOT": "C:\\Users\\YourName\\Projects\\myproject"
```

#### 3. Search Timeout Issues

**Symptoms**: Searches frequently timeout in large projects

**Solutions**:
- Increase timeout in config:
```json
"env": {
  "PROJECT_ROOT": "/path/to/project",
  "SEARCH_TIMEOUT": "120"  // Increase from default 60s
}
```
- Install ripgrep for faster searches:
```bash
# macOS
brew install ripgrep

# Windows
scoop install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep
```

#### 4. Permission Denied Errors

**Symptoms**: Cannot read certain files or directories

**Solutions**:
- Ensure the user running Claude Desktop has read permissions
- Check file/directory permissions: `ls -la /path/to/file`
- On macOS, grant Full Disk Access to Claude in System Preferences → Security & Privacy

#### 5. Binary File Errors

**Symptoms**: `BINARY_FILE_ERROR: Cannot read binary file`

**Explanation**: This is expected behavior - the server refuses to read binary files as text

**Solutions**:
- Use file type detection before attempting to read
- Only request text files (.txt, .md, .py, .json, etc.)

#### 6. Local Development Not Working

**Symptoms**: Server fails to start in development mode

**Solutions**:
```bash
# Ensure dependencies are installed
uv sync

# Check Python version (must be 3.11+)
python --version

# Run with explicit PROJECT_ROOT
PROJECT_ROOT=$(pwd) uv run python -m agent_mcp.server

# Check for errors in agent_mcp.log
cat agent_mcp.log
```

### Debug Mode

Enable verbose logging for troubleshooting:

```python
# In agent_mcp/utils/logger.py, change level to DEBUG
logging.basicConfig(
    handlers=[handler],
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Getting Help

If issues persist:

1. Check the log file: `agent_mcp.log`
2. Verify configuration: `cat ~/.config/Claude/claude_desktop_config.json`
3. Test server independently: `PROJECT_ROOT=/path uvx agent-mcp`
4. Report issues with:
   - Operating system and version
   - Python version (`python --version`)
   - Error messages from logs
   - Configuration (sanitize paths)

## Development

### Running Tests

```bash
# Install dev dependencies
uv sync

# Run all tests
PROJECT_ROOT=$(pwd) uv run pytest

# Run specific test suites
PROJECT_ROOT=$(pwd) uv run pytest tests/contract/
PROJECT_ROOT=$(pwd) uv run pytest tests/integration/
PROJECT_ROOT=$(pwd) uv run pytest tests/unit/

# With coverage
PROJECT_ROOT=$(pwd) uv run pytest --cov=agent_mcp --cov-report=term-missing
```

### Test Structure

- **Contract Tests** (`tests/contract/`): Validate MCP tool interface contracts
- **Integration Tests** (`tests/integration/`): End-to-end workflow validation
- **Unit Tests** (`tests/unit/`): Individual component testing

## Architecture

```
agent_mcp/
├── __init__.py          # Data models and exceptions
├── config.py            # Environment variable configuration
├── server.py            # FastMCP server entry point
├── tools/               # MCP tool implementations
│   ├── navigation.py    # Directory listing and tree tools
│   ├── search.py        # Search and find tools
│   └── read.py          # File reading tools
├── validators/          # Security validators
│   └── path_validator.py
└── utils/               # Utilities
    ├── file_detector.py # Binary file detection
    └── logger.py        # Logging configuration

tests/
├── contract/            # MCP contract tests
├── integration/         # Full workflow tests
└── unit/                # Component unit tests
```

## Requirements

- **Python**: 3.11 or higher
- **Optional**: ripgrep (`rg`) for faster searching (falls back to Python implementation)

## Logging

Logs are automatically rotated daily with 7-day retention:
- **Location**: `agent_mcp.log` (in current directory)
- **Format**: Timestamp, level, message
- **Retention**: 7 days

## License

[Your License Here]

## Contributing

[Contributing guidelines if applicable]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
