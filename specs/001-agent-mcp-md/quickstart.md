# Quickstart Guide

**Feature**: MCP 项目上下文集成服务
**Date**: 2025-10-03

## 目标

通过一个完整的工作流程验证所有核心功能,确保:
1. ✅ 环境配置正确
2. ✅ 所有MCP工具可正常调用
3. ✅ 路径安全验证生效
4. ✅ 边界情况正确处理

---

## 前置条件

### 1. 安装依赖
```bash
# 使用uvx直接运行(推荐)
uvx context-mcp

# 或本地开发安装
cd context-mcp
uv sync
```

### 2. 安装ripgrep(推荐)
```bash
# macOS
brew install ripgrep

# Ubuntu/Debian
sudo apt install ripgrep

# Windows
scoop install ripgrep
```

### 3. 配置环境变量
```bash
# 设置项目根目录(必须)
export PROJECT_ROOT=/path/to/your/project

# 可选: 配置搜索超时(默认60秒)
export SEARCH_TIMEOUT=30
```

---

## 快速验证流程

### 步骤1: 启动MCP服务器

```bash
# 使用uvx运行
uvx agent-mcp

# 或本地开发模式
uv run python -m agent_mcp.server
```

**预期输出**:
```
INFO: MCP Server 'agent-mcp' started
INFO: Project root: /path/to/your/project
INFO: Search timeout: 60s
INFO: Listening for MCP requests...
```

---

### 步骤2: 验证导航功能

#### 2.1 列出根目录
**MCP请求**:
```json
{
  "tool": "list_directory",
  "arguments": {
    "path": ".",
    "limit": 10
  }
}
```

**预期响应**:
```json
{
  "entries": [
    {
      "name": "README.md",
      "type": "file",
      "size": 1024,
      "mtime": 1727900000.0,
      "path": "./README.md"
    },
    ...
  ],
  "total": 25,
  "truncated": true
}
```

**验证点**:
- [x] `entries`数组包含文件和目录
- [x] `truncated=true`(因为limit=10)
- [x] 每个entry包含所有必填字段

#### 2.2 按大小排序
**MCP请求**:
```json
{
  "tool": "list_directory",
  "arguments": {
    "path": ".",
    "sort_by": "size",
    "order": "desc",
    "limit": 5
  }
}
```

**验证点**:
- [x] 返回的文件按size降序排列
- [x] 第一个文件size最大

#### 2.3 展示目录树
**MCP请求**:
```json
{
  "tool": "show_tree",
  "arguments": {
    "path": ".",
    "max_depth": 2
  }
}
```

**预期响应**:
```json
{
  "tree": {
    "name": ".",
    "type": "dir",
    "depth": 0,
    "children": [
      {
        "name": "src",
        "type": "dir",
        "depth": 1,
        "children": [...]
      },
      {
        "name": "README.md",
        "type": "file",
        "depth": 1
      }
    ]
  },
  "max_depth_reached": true
}
```

**验证点**:
- [x] 树结构正确展开到depth=2
- [x] `max_depth_reached=true`

---

### 步骤3: 验证搜索功能

#### 3.1 单文件搜索
**MCP请求**:
```json
{
  "tool": "search_in_file",
  "arguments": {
    "query": "import",
    "file_path": "src/main.py"
  }
}
```

**预期响应**:
```json
{
  "matches": [
    {
      "line_number": 1,
      "line_content": "import os",
      "match_start": 0,
      "match_end": 6
    },
    ...
  ],
  "total_matches": 5
}
```

**验证点**:
- [x] 找到所有包含"import"的行
- [x] `line_number`从1开始
- [x] `line_content`完整保留

#### 3.2 多文件搜索(正则表达式)
**MCP请求**:
```json
{
  "tool": "search_in_files",
  "arguments": {
    "query": "def \\w+\\(",
    "file_pattern": "*.py",
    "path": "src",
    "use_regex": true
  }
}
```

**预期响应**:
```json
{
  "matches": [
    {
      "file_path": "src/tools/navigation.py",
      "line_number": 10,
      "line_content": "def list_directory(path: str):"
    },
    ...
  ],
  "total_matches": 15,
  "files_searched": 5,
  "timed_out": false
}
```

**验证点**:
- [x] 只搜索`.py`文件
- [x] 正则表达式匹配生效
- [x] `timed_out=false`

#### 3.3 按文件名查找
**MCP请求**:
```json
{
  "tool": "find_files_by_name",
  "arguments": {
    "name_pattern": "*.json",
    "path": "."
  }
}
```

**预期响应**:
```json
{
  "files": [
    "./package.json",
    "./tsconfig.json",
    "./contracts/navigation_tools.json"
  ],
  "total_found": 3
}
```

**验证点**:
- [x] 找到所有`.json`文件
- [x] 路径相对于项目根目录

#### 3.4 查找最近修改文件
**MCP请求**:
```json
{
  "tool": "find_recently_modified_files",
  "arguments": {
    "path": "src",
    "file_pattern": "*.py",
    "hours_ago": 24
  }
}
```

**预期响应**:
```json
{
  "files": [
    {
      "path": "src/server.py",
      "mtime": 1727900000.0
    },
    ...
  ],
  "total_found": 3
}
```

**验证点**:
- [x] 只返回最近24小时修改的文件
- [x] 按修改时间排序(最新在前)

---

### 步骤4: 验证读取功能

#### 4.1 读取完整文件
**MCP请求**:
```json
{
  "tool": "read_entire_file",
  "arguments": {
    "file_path": "README.md"
  }
}
```

**预期响应**:
```json
{
  "content": "# Project Title\n\n...",
  "encoding": "utf-8",
  "line_count": 50,
  "file_path": "README.md"
}
```

**验证点**:
- [x] `content`包含完整文件内容
- [x] `encoding`正确检测
- [x] `line_count`准确

#### 4.2 读取指定行范围
**MCP请求**:
```json
{
  "tool": "read_file_lines",
  "arguments": {
    "file_path": "src/server.py",
    "start_line": 10,
    "end_line": 20
  }
}
```

**预期响应**:
```json
{
  "content": "line 10\nline 11\n...\nline 20\n",
  "encoding": "utf-8",
  "line_count": 11,
  "file_path": "src/server.py",
  "is_partial": true,
  "total_lines": 100
}
```

**验证点**:
- [x] 只返回第10-20行
- [x] `is_partial=true`
- [x] `total_lines`显示文件总行数

#### 4.3 读取文件末尾
**MCP请求**:
```json
{
  "tool": "read_file_tail",
  "arguments": {
    "file_path": "logs/app.log",
    "num_lines": 50
  }
}
```

**预期响应**:
```json
{
  "content": "...(最后50行)",
  "encoding": "utf-8",
  "line_count": 50,
  "file_path": "logs/app.log",
  "is_partial": true,
  "total_lines": 1000
}
```

**验证点**:
- [x] 只返回最后50行
- [x] 对于日志文件特别有用

#### 4.4 批量读取文件
**MCP请求**:
```json
{
  "tool": "read_files",
  "arguments": {
    "file_paths": [
      ".env.example",
      "pyproject.toml",
      "nonexistent.txt"
    ]
  }
}
```

**预期响应**:
```json
{
  "files": [
    {
      "file_path": ".env.example",
      "content": "PROJECT_ROOT=...",
      "encoding": "utf-8",
      "line_count": 3
    },
    {
      "file_path": "pyproject.toml",
      "content": "[project]...",
      "encoding": "utf-8",
      "line_count": 20
    },
    {
      "file_path": "nonexistent.txt",
      "error": {
        "code": "FILE_NOT_FOUND",
        "message": "文件不存在"
      }
    }
  ],
  "success_count": 2,
  "error_count": 1
}
```

**验证点**:
- [x] 成功的文件包含content
- [x] 失败的文件包含error
- [x] `success_count + error_count = 总文件数`

---

### 步骤5: 验证安全边界

#### 5.1 路径遍历攻击(应失败)
**MCP请求**:
```json
{
  "tool": "read_entire_file",
  "arguments": {
    "file_path": "../../etc/passwd"
  }
}
```

**预期响应**:
```json
{
  "error": {
    "code": "PATH_SECURITY_ERROR",
    "message": "Path ../../etc/passwd outside root /path/to/your/project"
  }
}
```

**验证点**:
- [x] 拒绝访问项目根目录外的文件
- [x] 返回明确的安全错误

#### 5.2 二进制文件读取(应失败)
**MCP请求**:
```json
{
  "tool": "read_entire_file",
  "arguments": {
    "file_path": "image.png"
  }
}
```

**预期响应**:
```json
{
  "error": {
    "code": "BINARY_FILE_ERROR",
    "message": "不支持读取二进制文件: image.png"
  }
}
```

**验证点**:
- [x] 检测到二进制文件
- [x] 返回错误而非尝试读取

#### 5.3 搜索超时(模拟大项目)
**MCP请求**:
```json
{
  "tool": "search_in_files",
  "arguments": {
    "query": ".*",
    "file_pattern": "*",
    "path": ".",
    "use_regex": true,
    "timeout": 1
  }
}
```

**预期响应**:
```json
{
  "matches": [...],
  "total_matches": 1234,
  "files_searched": 50,
  "timed_out": true
}
```

**验证点**:
- [x] 在超时后停止搜索
- [x] 返回部分结果
- [x] `timed_out=true`

---

### 步骤6: 验证边界情况

#### 6.1 空目录
**MCP请求**:
```json
{
  "tool": "list_directory",
  "arguments": {
    "path": "empty_dir"
  }
}
```

**预期响应**:
```json
{
  "entries": [],
  "total": 0,
  "truncated": false
}
```

#### 6.2 无搜索结果
**MCP请求**:
```json
{
  "tool": "search_in_files",
  "arguments": {
    "query": "NONEXISTENT_STRING_XYZ"
  }
}
```

**预期响应**:
```json
{
  "matches": [],
  "total_matches": 0,
  "files_searched": 100,
  "timed_out": false
}
```

#### 6.3 行号超出范围
**MCP请求**:
```json
{
  "tool": "read_file_lines",
  "arguments": {
    "file_path": "small.txt",
    "start_line": 100,
    "end_line": 200
  }
}
```

**预期响应**:
```json
{
  "error": {
    "code": "INVALID_LINE_RANGE",
    "message": "行号范围无效: 文件仅有10行"
  }
}
```

---

## 完整工作流测试

**场景**: Agent分析新项目

```bash
# 1. 查看项目结构
show_tree(path=".", max_depth=3)

# 2. 找到主要配置文件
find_files_by_name(name_pattern="*.json")
find_files_by_name(name_pattern="*.yaml")

# 3. 读取关键配置
read_files(file_paths=["package.json", "pyproject.toml", ".gitignore"])

# 4. 搜索所有导入语句
search_in_files(query="^import ", use_regex=true, file_pattern="*.py")

# 5. 查找最近修改的代码
find_recently_modified_files(path="src", hours_ago=48)

# 6. 读取最近修改文件的内容
read_files(file_paths=[<recent files>])

# 7. 分析特定函数
search_in_files(query="def main\\(", use_regex=true)
read_file_lines(file_path="src/main.py", start_line=<found_line>, end_line=<found_line+20>)
```

---

## 验收清单

### 功能完整性
- [x] 所有10个MCP工具可调用
- [x] 导航工具(2个): list_directory, show_tree
- [x] 搜索工具(4个): search_in_file, search_in_files, find_files_by_name, find_recently_modified_files
- [x] 读取工具(4个): read_entire_file, read_file_lines, read_file_tail, read_files

### 契约符合性
- [x] 所有响应符合contracts/*.json定义的schema
- [x] 错误码与契约一致
- [x] 必填字段全部存在

### 安全性
- [x] 路径遍历攻击被拦截
- [x] 所有路径限制在PROJECT_ROOT内
- [x] 二进制文件读取被拒绝

### 性能
- [x] 搜索超时机制生效
- [x] 大型项目列表操作响应正常(<5秒)
- [x] 日志文件按配置轮转(7天)

### 边界情况
- [x] 空目录、空结果正确处理
- [x] 行号超出范围报错
- [x] 文件不存在报错明确
- [x] 权限错误报错明确

---

## 故障排查

### 问题1: MCP服务器启动失败
**症状**: `ValueError: PROJECT_ROOT environment variable not set`
**解决**:
```bash
export PROJECT_ROOT=/path/to/your/project
```

### 问题2: ripgrep未找到
**症状**: 搜索功能报错 `rg command not found`
**解决**:
```bash
# 自动回退到grep(性能降低)
# 或安装ripgrep: brew install ripgrep
```

### 问题3: 搜索经常超时
**症状**: 大项目搜索频繁超时
**解决**:
```bash
# 增加超时配置
export SEARCH_TIMEOUT=120
```

### 问题4: 日志文件过大
**症状**: 磁盘空间不足
**解决**:
- 检查日志配置是否正确(7天轮转)
- 手动清理: `rm agent_mcp.log.*`

---

## 下一步

- ✅ 所有功能验证通过 → 开始实施任务(/tasks命令)
- ❌ 部分验证失败 → 返回Phase 1调整设计
