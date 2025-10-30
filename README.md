# Context MCP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/geq1fan/context-mcp/workflows/Tests/badge.svg)](https://github.com/geq1fan/context-mcp/actions)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **项目上下文集成的 MCP 服务器**
>
> 为 AI Agent 提供安全的只读文件系统操作，用于分析和理解项目代码库，并兼容所有系统。
>
> 核心价值：
>
> - 轻量级项目检索，无需预先构建索引或部署额外服务。
> - 多仓库/多项目上下文聚合，通过 MCP 与 Agent 工作流顺畅衔接。

## 为什么选择 Context MCP？

**核心价值**：跨项目上下文聚合 — 在分析 A 项目时，一键获取 B 服务的接口实现、依赖库的源码逻辑。

### 多项目配置（一次配置，永久可用）

```json
{
  "mcpServers": {
    "frontend-project": {
      "command": "uvx",
      "args": ["context-mcp@0.2.5"],
      "env": { "PROJECT_ROOT": "/path/to/frontend" }
    },
    "backend-api": {
      "command": "uvx",
      "args": ["context-mcp@0.2.5"],
      "env": { "PROJECT_ROOT": "/path/to/backend" }
    }
  }
}
```

### 典型场景：微服务接口调用链分析

**问题**：前端调用 `POST /api/users/login` 返回 500 错误，需要排查后端实现

| 步骤          | 传统方案                               | Context MCP                                   |
| ------------- | -------------------------------------- | --------------------------------------------- |
| 1. 定位接口   | 手动打开后端项目 → 搜索路由文件        | 一句话："分析 login 接口的实现逻辑和错误处理" |
| 2. 追踪调用链 | 手动跟踪 routes → controller → service | Agent 自动跨项目搜索并追踪完整调用链          |
| 3. 理解逻辑   | 逐个打开文件查看参数验证、错误码       | 自动返回：参数规则、错误码含义、调用栈        |
| **总耗时**    | **≈10 分钟**（需切换目录、多次搜索）   | **≈30 秒**（Agent 自动化完成）                |

**实际输出示例**：

```
🤖 已分析login接口完整调用链：
   → routes/users.js:12 定义POST /api/users/login
   → controllers/UserController.js:45 调用AuthService.login(email, password)
   → services/AuthService.js:78 参数验证：email必填且格式正确、密码8-20位
   → services/AuthService.js:92 错误码：401未授权、500数据库连接失败

   当前500错误原因：数据库连接池配置过小，建议检查DB_POOL_SIZE环境变量
```

**价值**：将跨仓库代码追踪从"手动体力活"变为"AI 自动化"，团队协作效率提升 20 倍。

---

## 快速开始

### MCP 配置

```json
{
  "mcpServers": {
    "context-mcp": {
      "command": "uvx",
      "args": ["context-mcp@0.2.5"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

或者：

```bash
claude mcp add context-mcp --env PROJECT_ROOT="/absolute/path/to/your/project"  -- uvx context-mcp@0.2.5
```

> **⚠️ 注意**：`PROJECT_ROOT`变量必须配置，否则服务无法启动。

### 可选：日志配置

Context MCP 支持灵活的日志配置，通过环境变量控制日志级别和输出方式：

#### 日志级别 (LOG_LEVEL)

控制日志详细程度，可选值：`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`（默认：`WARNING`）

**使用场景：**

```json
{
  "mcpServers": {
    "context-mcp": {
      "command": "uvx",
      "args": ["context-mcp@0.2.5"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 文件日志 (ENABLE_FILE_LOG)

控制是否将日志输出到文件（默认：`false`，仅输出到 stderr）

**启用文件日志：**

```json
{
  "mcpServers": {
    "context-mcp": {
      "command": "uvx",
      "args": ["context-mcp@0.2.5"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/your/project",
        "ENABLE_FILE_LOG": "true"
      }
    }
  }
}
```

**日志配置说明：**

- **默认行为**：日志仅输出到 stderr（控制台），不会创建 `context-mcp.log` 文件
- **启用文件日志后**：日志同时输出到 stderr 和 `context-mcp.log`，按天自动轮转，保留 7 天
- **推荐配置**：
  - 开发调试：`LOG_LEVEL=DEBUG`
  - 生产环境：`LOG_LEVEL=WARNING`（默认），`ENABLE_FILE_LOG=false`（默认）
  - 问题排查：`LOG_LEVEL=INFO` + `ENABLE_FILE_LOG=true`


### 可选：安装性能优化工具

Context MCP 可以利用高性能命令行工具大幅提升搜索速度（**13 倍加速**），推荐安装：

**ripgrep（推荐）** - 文件内容搜索加速

```bash
# macOS
brew install ripgrep

# Windows (Scoop)
scoop install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep
```

**fd（推荐）** - 文件名查找加速

```bash
# macOS
brew install fd

# Windows (Scoop)
scoop install fd

# Ubuntu/Debian
sudo apt install fd-find
```

> 💡 **提示**：这些工具是可选的。未安装时会自动降级到系统自带工具（grep/find），功能不受影响，只是速度稍慢。详细性能对比见[性能优化](#性能优化)章节。

### MCP Prompt

配置完成后，建议使用以下 Prompt 让 AI Agent **自主选择最合适的工具**，而非手动指定：

```
请先通过 get_tool_usage_guide 了解 context-mcp 提供的所有工具及其用途。
然后根据我的需求，自主选择最合适的工具组合来完成任务。

我的需求：[在此描述你的具体需求]
```

**这样做的优势：**

- ✅ **Agent 自主决策**：由 AI 判断用哪个工具最高效
- ✅ **工具组合优化**：自动串联多个工具完成复杂任务
- ✅ **适应性强**：即使工具升级或新增，无需修改 Prompt

---

## 核心能力

Context MCP 提供 **12 个 MCP 工具**，让 AI Agent 通过只读方式深入分析任何项目的代码库。

> **使用场景示例**：假设你已配置 `PROJECT_ROOT=/path/to/my-web-app`，以下是实际使用方式。

### 📁 导航工具（3 个）

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

### 🔍 搜索工具（4 个）

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

### 📋 指南工具（1 个）

- **`get_tool_usage_guide`** - 获取所有 MCP 工具的完整使用文档
  - **场景**：AI Agent 自主了解和选择最合适的工具
  - **对话示例**：
    ```
    👤 "请先通过 get_tool_usage_guide 了解 context-mcp 提供的所有工具及其用途"
    🤖 [使用 get_tool_usage_guide] 返回11个工具的完整文档：参数说明、返回格式、使用示例
    ```

### 📖 读取工具（4 个）

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

## 性能优化

Context MCP 会优先使用高性能的命令行工具,当这些工具不可用时自动降级到标准工具或 Python 实现,确保在任何环境下都能正常工作。

### 性能对比

**基准测试环境**: 中型项目 (1000-10000 文件, 10MB-100MB)

| 操作         | 高性能工具        | 标准工具    | Python 实现   | 加速比    |
| ------------ | ----------------- | ----------- | ------------- | --------- |
| 文件内容搜索 | **ripgrep** 180ms | grep 2400ms | Python 4200ms | **13.3x** |
| 文件名查找   | **fd** 50ms       | find 450ms  | Python 680ms  | **9.0x**  |

### 推荐工具安装

为获得最佳性能,建议安装以下高性能工具:

#### ripgrep (rg) - 高性能搜索

**Windows**:

```powershell
# Chocolatey
choco install ripgrep

# Scoop
scoop install ripgrep
```

**Linux**:

```bash
# Ubuntu/Debian
sudo apt install ripgrep

# Fedora
sudo dnf install ripgrep
```

**macOS**:

```bash
brew install ripgrep
```

**官方下载**: https://github.com/BurntSushi/ripgrep#installation

#### fd - 高性能文件查找

**Windows**:

```powershell
# Chocolatey
choco install fd

# Scoop
scoop install fd
```

**Linux**:

```bash
# Ubuntu/Debian (需要 Ubuntu 19.04+ 或手动安装)
sudo apt install fd-find

# Fedora
sudo dnf install fd-find
```

**macOS**:

```bash
brew install fd
```

**官方下载**: https://github.com/sharkdp/fd#installation

> 📝 **说明**: 这些工具是可选的。Context MCP 在没有这些工具的环境下会自动降级到系统自带的 grep/find 或 Python 实现,功能完全不受影响,只是性能会有所降低。服务启动时会在日志中显示工具检测结果。

## 安全性

- **只读操作**：不提供写入、修改或删除功能
- **路径验证**：所有路径严格限制在配置的 PROJECT_ROOT 内
- **二进制文件保护**：拒绝将二进制文件作为文本读取
- **权限处理**：优雅处理权限错误

## 常见问题

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
PROJECT_ROOT=$(pwd) uv run pytest --cov=context_mcp
```

**测试覆盖率**：240 个测试，覆盖率 77%（运行 `$env:PROJECT_ROOT = (Get-Location).Path; python -m pytest --cov=context_mcp`）

## 文档

- **[README.md](README.md)** - 本文件，快速开始和概览
- **[SECURITY.md](SECURITY.md)** - 安全政策和漏洞报告
- **[CHANGELOG.md](CHANGELOG.md)** - 版本历史和变更记录
- **[LICENSE](LICENSE)** - MIT 许可证文本

## 系统要求

- Python 3.11 或更高版本

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

## 支持与社区

- **问题反馈**：[GitHub Issues](https://github.com/geq1fan/context-mcp/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/geq1fan/context-mcp/discussions)
- **安全漏洞**：参考 [SECURITY.md](SECURITY.md) 报告安全问题

---

**构建工具** [FastMCP](https://github.com/jlowin/fastmcp) • **适配平台** [Claude Desktop](https://claude.ai/desktop) • **基于协议** [MCP](https://modelcontextprotocol.io/)
