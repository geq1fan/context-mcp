# Context MCP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/geq1fan/context-mcp/workflows/Tests/badge.svg)](https://github.com/geq1fan/context-mcp/actions)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **MCP Server for Project Context Integration**
>
> Provide AI agents with secure, read-only filesystem operations to analyze and understand project codebases.

**Quick Links**: 📖 [Configuration Guide](CONFIGURATION.md) | 🚀 [Quick Start](#quick-start) | 🐛 [Troubleshooting](CONFIGURATION.md#troubleshooting-configuration) | 🤝 [Contributing](CONTRIBUTING.md)

## 快速开始

### 方式一：Claude Desktop 配置

**1. 编辑配置文件**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**2. 添加配置**（使用 uvx，无需安装）

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

**3. 重启应用**

重启 Claude Desktop，查看 🔌 图标确认连接成功。

**4. 试用**

```
列出项目根目录的所有文件
```

```
在 Python 文件中搜索所有 TODO 注释
```

### 方式二：Claude Code 配置

**1. 添加 MCP 服务器**

```bash
claude mcp add context-mcp -- uvx context-mcp
```

**2. 设置环境变量**

编辑 `~/.claude/mcp.json` 添加：

```json
{
  "mcpServers": {
    "context-mcp": {
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

**3. 重启 Claude Code**

重启后工具会自动加载。

**4. 试用**

```
显示项目的树状结构
```

```
查找最近 3 天修改的所有文件
```

---

**需要更多配置选项？** 查看 [完整配置指南](CONFIGURATION.md)

## 核心能力

Context MCP 提供 **10 个 MCP 工具**，让 AI Agent 能够高效地浏览、搜索和读取项目代码。

### 📁 导航工具（2个）

- **`list_directory`** - 列出目录内容，支持排序和限制数量
  - **用例**：快速查看项目结构、定位文件位置、了解模块组织
  - **示例**：`列出 src/ 目录下的所有文件`

- **`show_tree`** - 以树状结构展示目录层次，支持深度限制
  - **用例**：可视化项目架构、理解代码层次关系、生成目录文档
  - **示例**：`显示项目根目录的树状结构，深度为3层`

### 🔍 搜索工具（4个）

- **`search_in_file`** - 在单个文件中搜索文本或正则表达式
  - **用例**：快速定位函数定义、查找特定配置项、分析代码片段
  - **示例**：`在 config.py 中搜索 "DATABASE"`

- **`search_in_files`** - 跨多个文件递归搜索，支持正则表达式和排除模式
  - **用例**：查找所有 TODO 注释、定位 API 调用、追踪变量使用、代码审计
  - **示例**：`在所有 Python 文件中搜索 "TODO" 注释，排除测试文件`

- **`find_files_by_name`** - 按文件名查找（支持通配符）
  - **用例**：快速定位特定文件、查找同名文件、批量文件操作
  - **示例**：`查找所有名为 config.py 的文件` 或 `查找所有 *.test.ts 文件`

- **`find_recently_modified_files`** - 按最近修改时间查找文件
  - **用例**：追踪最近改动、快速定位最新代码、回顾开发进展
  - **示例**：`查找最近 7 天内修改的所有文件`

### 📖 读取工具（4个）

- **`read_entire_file`** - 读取完整文件内容
  - **用例**：分析源代码、理解配置文件、检查文档内容
  - **示例**：`读取 README.md 的完整内容`

- **`read_file_lines`** - 读取文件的指定行范围
  - **用例**：精确查看代码片段、分析特定函数、提取配置项
  - **示例**：`读取 server.py 的第 50-100 行`

- **`read_file_tail`** - 读取文件末尾 N 行
  - **用例**：查看日志文件、检查最新添加的内容、快速浏览文件结尾
  - **示例**：`读取 application.log 的最后 50 行`

- **`read_files`** - 批量读取多个文件
  - **用例**：对比多个文件、批量分析代码、生成综合报告
  - **示例**：`同时读取 package.json 和 requirements.txt`

> 💡 **提示**：所有工具都经过安全加固，只支持只读操作，路径严格限制在配置的 PROJECT_ROOT 内。

详细工具文档请参考 [CONFIGURATION.md](CONFIGURATION.md)。


## Security

- **Read-Only Operations**: No write, modify, or delete capabilities
- **Path Validation**: All paths restricted to configured PROJECT_ROOT
- **Binary File Protection**: Refuses to read binary files as text
- **Permission Handling**: Graceful handling of permission errors

## 常见问题

遇到问题？查看 [完整故障排查指南](CONFIGURATION.md#troubleshooting-configuration)

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

MIT License - 完整内容请查看 [LICENSE](LICENSE) 文件。

- ✅ 允许商业使用、修改和分发
- ⚠️ 不提供任何担保

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
