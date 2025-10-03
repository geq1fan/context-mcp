# Agent MCP Configuration Guide

## Quick Start Configuration

### 1. Claude Desktop Configuration

**Step 1**: Locate your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Step 2**: Add agent-mcp configuration:

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project",
        "SEARCH_TIMEOUT": "60"
      }
    }
  }
}
```

**Step 3**: Restart Claude Desktop

**Step 4**: Verify connection by looking for the 🔌 icon

## Configuration Templates

### Template 1: Basic Configuration (Recommended)

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/project"
      }
    }
  }
}
```

### Template 2: With Custom Timeout

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/project",
        "SEARCH_TIMEOUT": "120"
      }
    }
  }
}
```

### Template 3: Local Development

```json
{
  "mcpServers": {
    "agent-mcp-dev": {
      "command": "uv",
      "args": ["run", "python", "-m", "agent_mcp.server"],
      "cwd": "/path/to/agent-mcp-repo",
      "env": {
        "PROJECT_ROOT": "/path/to/test/project",
        "SEARCH_TIMEOUT": "60"
      }
    }
  }
}
```

### Template 4: Multiple Projects

```json
{
  "mcpServers": {
    "my-backend": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/projects/backend-api"
      }
    },
    "my-frontend": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/projects/frontend-app"
      }
    },
    "my-docs": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/projects/documentation",
        "SEARCH_TIMEOUT": "30"
      }
    }
  }
}
```

## Platform-Specific Examples

### macOS Configuration

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/Users/username/Projects/my-project"
      }
    }
  }
}
```

### Windows Configuration

**Option 1: Forward slashes (recommended)**
```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "C:/Users/username/Projects/my-project"
      }
    }
  }
}
```

**Option 2: Escaped backslashes**
```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "C:\\Users\\username\\Projects\\my-project"
      }
    }
  }
}
```

### Linux Configuration

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/home/username/projects/my-project"
      }
    }
  }
}
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROJECT_ROOT` | ✅ Yes | None | Absolute path to the project directory |
| `SEARCH_TIMEOUT` | ❌ No | 60 | Search operation timeout in seconds |

## Verification Steps

### 1. Test Server Independently

```bash
# Set environment variable
export PROJECT_ROOT=/path/to/project

# Test with uvx
uvx agent-mcp

# Or test with uv (local development)
cd /path/to/agent-mcp
uv run python -m agent_mcp.server
```

### 2. Check Logs

**Claude Desktop logs**:
- macOS: `~/Library/Logs/Claude/mcp*.log`
- Windows: `%APPDATA%\Claude\logs\mcp*.log`

**Server logs**:
- Location: `agent_mcp.log` (in working directory)

### 3. Test MCP Tools

After configuration, try these commands in Claude:

```
# List root directory
Please use agent-mcp to list files in the root directory

# Search for text
Please use agent-mcp to search for "import" in Python files

# Read a file
Please use agent-mcp to read the README.md file
```

## Common Configuration Mistakes

### ❌ Relative Paths
```json
// WRONG - Relative paths not allowed
"PROJECT_ROOT": "./my-project"
"PROJECT_ROOT": "../projects/app"
```

### ✅ Absolute Paths
```json
// CORRECT - Use absolute paths
"PROJECT_ROOT": "/Users/username/projects/my-project"
"PROJECT_ROOT": "C:/Users/username/projects/my-project"
```

### ❌ Missing Quotes
```json
// WRONG - Timeout must be a string in env
"SEARCH_TIMEOUT": 60
```

### ✅ Quoted Values
```json
// CORRECT - All env values are strings
"SEARCH_TIMEOUT": "60"
```

### ❌ Invalid JSON Syntax
```json
// WRONG - Trailing comma
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],  // Trailing comma not allowed
    }
  }
}
```

### ✅ Valid JSON
```json
// CORRECT - No trailing commas
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"]
    }
  }
}
```

## Advanced Configurations

### With Custom Python Path

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "/usr/local/bin/python3.11",
      "args": ["-m", "agent_mcp.server"],
      "env": {
        "PROJECT_ROOT": "/path/to/project",
        "PYTHONPATH": "/path/to/agent-mcp"
      }
    }
  }
}
```

### With Additional Debugging

```json
{
  "mcpServers": {
    "agent-mcp": {
      "command": "uvx",
      "args": ["agent-mcp"],
      "env": {
        "PROJECT_ROOT": "/path/to/project",
        "SEARCH_TIMEOUT": "60",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Troubleshooting Configuration

### Issue: Server Not Starting

1. Validate JSON syntax: Use [jsonlint.com](https://jsonlint.com)
2. Check file permissions: Ensure config file is readable
3. Verify paths: Use absolute paths, not relative
4. Test command: Run `uvx agent-mcp` in terminal

### Issue: Cannot Read Files

1. Check PROJECT_ROOT is correct
2. Verify user has read permissions
3. Ensure path is within PROJECT_ROOT
4. Check file is not binary

### Issue: Slow Performance

1. Install ripgrep: `brew install ripgrep` (macOS)
2. Increase timeout: Set `SEARCH_TIMEOUT` to higher value
3. Use more specific search patterns
4. Limit search scope with `file_pattern`

## Migration from Development to Production

**Development** (using local repository):
```json
{
  "command": "uv",
  "args": ["run", "python", "-m", "agent_mcp.server"],
  "cwd": "/path/to/agent-mcp-dev"
}
```

**Production** (using published package):
```json
{
  "command": "uvx",
  "args": ["agent-mcp"]
}
```

## Configuration Best Practices

1. ✅ Use absolute paths for `PROJECT_ROOT`
2. ✅ Keep timeout values reasonable (30-120 seconds)
3. ✅ Use descriptive server names for multiple projects
4. ✅ Test configuration before deploying to team
5. ✅ Document custom timeout values
6. ✅ Use version control for shared configurations
7. ✅ Sanitize paths before sharing (remove usernames)

## Support

For configuration issues:
1. Check this guide thoroughly
2. Review [README.md](README.md) Troubleshooting section
3. Examine log files
4. Test server independently
5. Report issues with full configuration (sanitized)
