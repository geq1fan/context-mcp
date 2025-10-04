# Research: Tool Usage Guide Tool

**Date**: 2025-10-04
**Feature**: 004-tool-tool-prompt

## Research Overview

本文档记录为实现工具使用指南功能所需的技术调研结果。主要聚焦于:如何从FastMCP装饰器提取Schema、如何生成混合格式文档、如何设计YAML数据结构。

---

## 1. FastMCP装饰器元数据提取

### Decision: 使用Python inspect模块 + FastMCP内部API

### Rationale
- FastMCP的`@mcp.tool()`装饰器将工具注册在MCP实例的内部registry中
- 可通过`mcp.list_tools()`获取所有已注册工具的元数据
- 每个工具对象包含`input_schema`属性,即JSON Schema定义
- inspect.signature()可补充获取参数默认值等运行时信息

### Alternatives Considered
- **AST静态分析**: 解析server.py源代码提取装饰器参数
  - ❌ Rejected: 无法处理动态生成的Schema,维护成本高
- **手动复制Schema**: 在YAML中重复定义参数Schema
  - ❌ Rejected: 违反DRY原则,容易产生不一致

### Implementation Approach
```python
# 伪代码示例
from context_mcp.server import mcp

def extract_tool_schemas() -> dict[str, dict]:
    """从FastMCP实例提取所有工具的Schema"""
    tools_metadata = {}
    for tool in mcp.list_tools():
        tools_metadata[tool.name] = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,  # JSON Schema对象
        }
    return tools_metadata
```

### Key Findings
- FastMCP的`Tool`对象符合MCP协议标准,input_schema已是完整JSON Schema
- 无需额外转换,直接嵌入Markdown代码块即可
- Schema提取为运行时操作,工具更新后无需手动同步

---

## 2. 混合格式文档生成策略

### Decision: Markdown模板 + Jinja2渲染引擎

### Rationale
- Markdown提供良好的人类可读性和结构化标题
- JSON Schema片段作为```json代码块嵌入,保持语法高亮
- Jinja2模板支持条件渲染(如工具分类、可选参数标记)
- 生成逻辑与内容分离,便于调整文档格式

### Alternatives Considered
- **纯字符串拼接**: 使用f-string或.format()构建文档
  - ❌ Rejected: 模板逻辑混杂在代码中,难以维护
- **JSON格式**: 返回结构化JSON而非Markdown
  - ❌ Rejected: 不符合需求(混合格式明确要求Markdown外壳)

### Template Structure
```markdown
# Context MCP Tools Usage Guide

## Navigation Tools (3)

### list_directory
**Purpose**: {description}

**Parameters**:
```json
{input_schema}
```

**Example**:
```python
{example_code}
```

**Returns**: {return_description}

---
(重复其他工具...)
```

### Key Findings
- Jinja2的autoescaping需禁用,避免JSON Schema中的`<`/`>`被转义
- 工具按分类(navigation/search/read)分组展示,提升可读性
- 示例代码使用Python语法(tool_name(param=value)),贴近实际调用

---

## 3. YAML数据结构设计

### Decision: 两个独立YAML文件,扁平键值结构

### Rationale
- `tool_descriptions.yaml`: 工具名 → 详细描述(支持多行)
- `tool_examples.yaml`: 工具名 → 示例代码列表
- 分离描述和示例,便于独立更新和版本控制
- 扁平结构降低编辑门槛,非技术人员可直接修改

### Schema Example
```yaml
# tool_descriptions.yaml
list_directory: |
  列出指定目录下的所有文件和子目录。
  支持按名称/时间排序,可限制返回数量。
  常用于项目结构探索和文件导航。

search_in_files: |
  在多个文件中递归搜索匹配的文本模式。
  支持正则表达式、忽略大小写、排除路径。
  基于ripgrep优化,回退grep保证兼容性。

# tool_examples.yaml
list_directory:
  - |
    # 列出当前目录,按修改时间排序
    list_directory(path=".", sort_by="mtime", limit=10)
  - |
    # 列出src/目录,仅显示前5项
    list_directory(path="src", limit=5)

search_in_files:
  - |
    # 在Python文件中搜索"class"关键字
    search_in_files(pattern="class ", include_pattern="*.py")
  - |
    # 搜索TODO注释,忽略大小写
    search_in_files(pattern="todo", case_sensitive=False)
```

### Alternatives Considered
- **单一YAML文件**: 所有数据合并在一个文件
  - ❌ Rejected: 文件过大(11工具×描述+示例),难以快速定位
- **JSON格式**: 使用JSON替代YAML
  - ❌ Rejected: JSON不支持多行字符串,编辑体验差
- **嵌套结构**: 每个工具包含description/examples/category等子键
  - ⚠️ Deferred: 初期采用扁平结构简化,未来可重构为嵌套

### Key Findings
- YAML的`|`多行字符串literal保留换行,适合代码示例
- 工具名作为顶层键,与FastMCP的tool.name直接对应
- 文件放置在`context_mcp/data/`,与代码分离,Git diff友好

---

## 4. 错误处理与边缘情况

### Decision: 优雅降级 + 警告机制

### Rationale
- **无效工具名**: 过滤后返回有效文档,警告列表附加在响应元数据
- **缺失描述/示例**: 使用占位符`[Description pending]`,不阻塞文档生成
- **Schema提取失败**: 记录错误日志,返回fallback Schema `{"type": "object"}`
- **YAML文件不存在**: 首次运行时自动创建空模板,提示用户填充

### Error Response Format
```json
{
  "content": "# Context MCP Tools Usage Guide\n...",
  "warnings": [
    "Tool 'nonexistent_tool' not found. Available tools: list_directory, search_in_files, ..."
  ],
  "metadata": {
    "total_tools": 11,
    "filtered_count": 2,
    "invalid_names": ["nonexistent_tool"]
  }
}
```

### Key Findings
- 警告信息包含可用工具列表,帮助用户纠正拼写错误
- 占位符文本需明显标记(括号+大写),提醒维护者补充内容
- Schema提取异常不应导致整个工具失败,单个工具错误隔离

---

## 5. 性能优化考虑

### Decision: 内存缓存 + Lazy Load

### Rationale
- YAML文件在首次调用时加载,缓存在模块级全局变量
- Schema提取结果缓存,避免重复反射(工具定义运行时不变)
- 文档生成为纯内存操作,无I/O瓶颈
- 当前11工具规模下,全量生成<5ms,无需复杂优化

### Future Optimization (>50 tools)
- 分页返回: 添加`offset`/`limit`参数
- 增量更新: 仅重新生成变更工具的文档
- 压缩传输: 返回gzip压缩后的文档字符串

### Benchmarking Target
- 全量文档生成: <50ms (11工具)
- 单工具过滤: <10ms
- YAML加载: <20ms (一次性成本)

---

## 6. 集成与部署

### Decision: 作为标准MCP工具注册,无需额外配置

### Rationale
- 在`server.py`中导入`tools.guide`模块,工具自动注册
- YAML文件打包在Python包中,uvx安装时一并部署
- 无需环境变量配置,开箱即用

### Deployment Checklist
- [x] 添加`context_mcp/data/`到package_data (pyproject.toml)
- [x] 在server.py导入guide模块: `from context_mcp.tools import guide`
- [x] 创建初始YAML模板(包含11个现有工具的占位符)
- [ ] 在CLAUDE.md更新工具清单(12个工具)

---

## Summary of Decisions

| 决策点 | 选择方案 | 关键依赖 |
|--------|---------|---------|
| Schema提取 | FastMCP内部API + inspect | mcp.list_tools() |
| 文档格式 | Markdown + Jinja2模板 | jinja2库 |
| 数据存储 | 双YAML文件(描述+示例) | PyYAML |
| 错误处理 | 优雅降级 + 警告列表 | 无 |
| 性能策略 | 内存缓存 + 全量生成 | functools.lru_cache |
| 部署方式 | 标准MCP工具 | package_data配置 |

---

**Status**: ✅ All NEEDS CLARIFICATION resolved
**Next Phase**: Phase 1 - Design & Contracts
