# Agent Context: MCP 项目上下文集成服务

**Generated**: 2025-10-03 | **Feature**: 001-agent-mcp-md

## 项目概述

创建一个MCP服务,允许AI Agent通过标准化接口访问和分析任意项目的代码上下文。服务提供只读文件系统操作能力,包括目录导航、内容搜索和文件读取。

## 技术栈

**语言**: Python 3.11+
**框架**: fastmcp (MCP框架), ripgrep (搜索加速)
**打包**: uv + uvx模式
**测试**: pytest (契约/集成/单元测试)

## 项目结构

```
agent_mcp/
├── server.py           # FastMCP服务器入口
├── config.py           # 环境变量配置
├── tools/              # MCP工具实现
│   ├── navigation.py   # list_directory, show_tree
│   ├── search.py       # 4个搜索工具
│   └── read.py         # 4个读取工具
├── validators/         # 路径安全验证
└── utils/              # 文件检测、日志

tests/
├── contract/           # MCP契约测试
├── integration/        # 集成测试
└── unit/               # 单元测试
```

## 核心设计决策

1. **FastMCP装饰器模式**: `@mcp.tool()`定义工具函数
2. **路径安全**: `Path.resolve()`防目录遍历攻击
3. **二进制检测**: NULL字节检测法
4. **超时控制**: subprocess.run(timeout=60)
5. **ripgrep优先**: 回退grep保证兼容性

## 环境变量

- `PROJECT_ROOT`: 项目根目录(必须)
- `SEARCH_TIMEOUT`: 搜索超时秒数(默认60)

## MCP工具清单

### 导航(2个)
- `list_directory`: 列出目录,支持排序和limit
- `show_tree`: 树状展示,支持max_depth

### 搜索(4个)
- `search_in_file`: 单文件搜索
- `search_in_files`: 多文件递归搜索,支持正则、排除
- `find_files_by_name`: 按名称查找(通配符)
- `find_recently_modified_files`: 按修改时间查找

### 读取(4个)
- `read_entire_file`: 读取完整文件
- `read_file_lines`: 读取指定行范围
- `read_file_tail`: 读取末尾N行
- `read_files`: 批量读取

## 安全约束

- ✅ 只读操作(禁止写入/删除)
- ✅ 路径限制在PROJECT_ROOT内
- ✅ 拒绝二进制文件读取
- ✅ 文件权限检查

## 最近变更

1. Phase 1完成: 数据模型、契约定义、quickstart
2. 定义10个MCP工具契约(JSON Schema)
3. 确定三层测试策略(契约/集成/单元)

## 参考文档

- Spec: `specs/001-agent-mcp-md/spec.md`
- Plan: `specs/001-agent-mcp-md/plan.md`
- Research: `specs/001-agent-mcp-md/research.md`
- Data Model: `specs/001-agent-mcp-md/data-model.md`
- Contracts: `specs/001-agent-mcp-md/contracts/`
- Quickstart: `specs/001-agent-mcp-md/quickstart.md`
