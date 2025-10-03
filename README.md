# Context MCP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/geq1fan/context-mcp/workflows/Tests/badge.svg)](https://github.com/geq1fan/context-mcp/actions)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **项目上下文集成的 MCP 服务器**
>
> 为 AI Agent 提供安全的只读文件系统操作，用于分析和理解项目代码库。

**快速链接**：📖 [配置指南](CONFIGURATION.md) | 🚀 [快速开始](#快速开始) | 🐛 [故障排查](CONFIGURATION.md#troubleshooting-configuration) | 🤝 [贡献指南](CONTRIBUTING.md)

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

**4. 开始分析项目**

现在 Claude 可以访问你配置的项目了：

```
👤 "列出这个项目的根目录文件，帮我了解项目结构"
```

```
👤 "搜索项目中所有 TODO 注释，整理成待办清单"
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

**4. 开始分析项目**

现在可以通过对话分析目标项目：

```
👤 "显示这个项目的目录树，深度3层"
```

```
👤 "找出最近3天修改的文件，看看最新进展"
```

---

**需要更多配置选项？** 查看 [完整配置指南](CONFIGURATION.md)

## 核心能力

Context MCP 提供 **11 个 MCP 工具**，让 AI Agent 通过只读方式深入分析任何项目的代码库。

> **使用场景示例**：假设你已配置 `PROJECT_ROOT=/path/to/my-web-app`，以下是实际使用方式。

### 📁 导航工具（3个）

- **`list_directory`** - 列出目录内容，支持排序和限制数量
  - **场景**：初次接触项目，想了解整体结构
  - **对话示例**：
    ```
    👤 "列出这个 Web 项目的根目录文件"
    🤖 [使用 list_directory] 显示：package.json, src/, public/, README.md...
    ```

- **`show_tree`** - 以树状结构展示目录层次，支持深度限制
  - **场景**：可视化项目架构，生成文档
  - **对话示例**：
    ```
    👤 "显示 src/ 目录的完整结构，深度3层"
    🤖 [使用 show_tree] 展示树状图，快速了解模块划分
    ```

- **`read_project_context`** - 读取项目的 AI 上下文文件（AGENTS.md, CLAUDE.md）
  - **场景**：自动发现项目的 AI 协作规范和编码约定
  - **对话示例**：
    ```
    👤 "这个项目有配置 AI 协作规范吗？"
    🤖 [使用 read_project_context] 发现 CLAUDE.md，包含代码风格、测试要求...
    ```

### 🔍 搜索工具（4个）

- **`search_in_file`** - 在单个文件中搜索文本或正则表达式
  - **场景**：已知文件，需要定位特定代码
  - **对话示例**：
    ```
    👤 "在 src/config/database.js 中搜索数据库连接配置"
    🤖 [使用 search_in_file] 找到第23行的 DB_HOST 配置
    ```

- **`search_in_files`** - 跨多个文件递归搜索，支持正则表达式和排除模式
  - **场景**：代码审计、追踪 API 调用、查找技术债务
  - **对话示例**：
    ```
    👤 "在整个项目中搜索所有 TODO 注释，排除 node_modules"
    🤖 [使用 search_in_files] 发现15处待办事项，分布在8个文件中

    👤 "查找项目中所有调用 fetch() 的地方"
    🤖 [使用 search_in_files] 定位到23处 API 调用点
    ```

- **`find_files_by_name`** - 按文件名查找（支持通配符）
  - **场景**：快速定位配置文件、测试文件
  - **对话示例**：
    ```
    👤 "找出这个 React 项目中所有的测试文件"
    🤖 [使用 find_files_by_name "*.test.jsx"] 找到32个测试文件

    👤 "项目里有几个 config.json 文件？"
    🤖 [使用 find_files_by_name] 发现3个：根目录、src/config、tests/
    ```

- **`find_recently_modified_files`** - 按最近修改时间查找文件
  - **场景**：了解项目最新进展、快速定位活跃代码
  - **对话示例**：
    ```
    👤 "这个项目最近一周改了哪些文件？"
    🤖 [使用 find_recently_modified_files] 显示12个文件，主要集中在 auth 模块
    ```

### 📖 读取工具（4个）

- **`read_entire_file`** - 读取完整文件内容
  - **场景**：理解核心逻辑、分析配置
  - **对话示例**：
    ```
    👤 "读取这个项目的 package.json，告诉我用了哪些主要依赖"
    🤖 [使用 read_entire_file] 分析依赖：React 18, Express 4.x, MongoDB...
    ```

- **`read_file_lines`** - 读取文件的指定行范围
  - **场景**：精确查看函数实现
  - **对话示例**：
    ```
    👤 "src/utils/auth.js 的第 50-80 行是什么逻辑？"
    🤖 [使用 read_file_lines] 这是 JWT token 验证函数...
    ```

- **`read_file_tail`** - 读取文件末尾 N 行
  - **场景**：查看日志、检查文件最新内容
  - **对话示例**：
    ```
    👤 "看看 CHANGELOG.md 的最后20行，了解最新版本的改动"
    🤖 [使用 read_file_tail] 最新版本 v2.1.0 增加了 OAuth 支持...
    ```

- **`read_files`** - 批量读取多个文件
  - **场景**：对比分析、生成报告
  - **对话示例**：
    ```
    👤 "同时读取前端和后端的配置文件，对比环境变量设置"
    🤖 [使用 read_files] 读取 client/.env 和 server/.env，发现不一致...
    ```

> 💡 **提示**：所有工具都经过安全加固，只支持只读操作，路径严格限制在配置的 PROJECT_ROOT 内。

详细工具文档请参考 [CONFIGURATION.md](CONFIGURATION.md)。


## 安全性

- **只读操作**：不提供写入、修改或删除功能
- **路径验证**：所有路径严格限制在配置的 PROJECT_ROOT 内
- **二进制文件保护**：拒绝将二进制文件作为文本读取
- **权限处理**：优雅处理权限错误

## 常见问题

遇到问题？查看 [完整故障排查指南](CONFIGURATION.md#troubleshooting-configuration)

## 开发指南

**贡献者快速开始：**

```bash
# 克隆并设置
git clone https://github.com/geq1fan/context-mcp.git
cd context-mcp
uv sync

# 运行测试
PROJECT_ROOT=$(pwd) uv run pytest

# 运行测试并生成覆盖率报告
PROJECT_ROOT=$(pwd) uv run pytest --cov=agent_mcp
```

**测试覆盖率**：121 个测试（61 契约 + 28 集成 + 32 单元），覆盖率 99.2%

📖 **完整开发指南**：参考 [CONTRIBUTING.md](CONTRIBUTING.md)

## 文档

- **[README.md](README.md)** - 本文件，快速开始和概览
- **[CONFIGURATION.md](CONFIGURATION.md)** - 详细配置和故障排查
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 开发设置和贡献指南
- **[SECURITY.md](SECURITY.md)** - 安全政策和漏洞报告
- **[CHANGELOG.md](CHANGELOG.md)** - 版本历史和变更记录
- **[LICENSE](LICENSE)** - MIT 许可证文本

## 系统要求

- Python 3.11 或更高版本
- （可选）ripgrep 用于加速搜索

## 开源许可

MIT License - 完整内容请查看 [LICENSE](LICENSE) 文件。

- ✅ 允许商业使用、修改和分发
- ⚠️ 不提供任何担保

## 参与贡献

欢迎贡献！🎉

**快速贡献指南：**
1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交你的修改并添加测试
4. 确保所有测试通过（`PROJECT_ROOT=$(pwd) uv run pytest`）
5. 提交 Pull Request

详细指南请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

## 支持与社区

- **问题反馈**：[GitHub Issues](https://github.com/geq1fan/context-mcp/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/geq1fan/context-mcp/discussions)
- **安全漏洞**：参考 [SECURITY.md](SECURITY.md) 报告安全问题

---

**构建工具** [FastMCP](https://github.com/jlowin/fastmcp) • **适配平台** [Claude Desktop](https://claude.ai/desktop) • **基于协议** [MCP](https://modelcontextprotocol.io/)
