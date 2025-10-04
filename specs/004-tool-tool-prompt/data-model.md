# Data Model: Tool Usage Guide Tool

**Feature**: 004-tool-tool-prompt
**Date**: 2025-10-04

## Entity Overview

本功能的数据模型围绕**工具元数据**的结构化表示,涉及以下核心实体:

1. **ToolMetadata**: 单个工具的完整元数据
2. **ToolSchema**: 工具参数的JSON Schema定义
3. **ToolDescription**: 手动维护的工具描述文本
4. **ToolExample**: 手动维护的使用示例代码
5. **UsageGuideDocument**: 生成的混合格式文档
6. **GuideResponse**: API响应对象(包含文档+警告)

---

## Entity Definitions

### 1. ToolMetadata

**描述**: 聚合了单个MCP工具的所有元数据,包括自动提取和手动维护的部分。

**Fields**:
| Field | Type | Required | Source | Description |
|-------|------|----------|--------|-------------|
| `name` | str | Yes | FastMCP | 工具唯一标识符 (snake_case) |
| `category` | str | Yes | Inferred | 工具分类: "navigation" / "search" / "read" / "guide" |
| `description` | str | Yes | YAML | 详细用途说明(支持多行) |
| `input_schema` | ToolSchema | Yes | FastMCP | 参数JSON Schema对象 |
| `examples` | List[ToolExample] | No | YAML | 使用示例列表(可空) |
| `return_format` | str | No | YAML | 返回值描述(可空) |

**Validation Rules**:
- `name` must match FastMCP registered tool name
- `category` must be one of: ["navigation", "search", "read", "guide"]
- `description` length: 20-500 characters
- `input_schema` must be valid JSON Schema Draft 2020-12
- `examples` max count: 5 per tool

**Relationships**:
- 1 ToolMetadata → 1 ToolSchema (composition)
- 1 ToolMetadata → 0..5 ToolExample (composition)

---

### 2. ToolSchema

**描述**: 工具参数的JSON Schema定义,符合MCP协议规范。

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | Yes | 固定值"object" |
| `properties` | Dict[str, ParamDef] | Yes | 参数名→参数定义映射 |
| `required` | List[str] | No | 必需参数名列表 |
| `additionalProperties` | bool | No | 默认false |

**ParamDef SubSchema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | Yes | 参数类型: string/number/boolean/array/object |
| `description` | str | Yes | 参数说明 |
| `default` | Any | No | 默认值(如有) |
| `enum` | List[Any] | No | 枚举值(如有) |
| `items` | Dict | No | 数组元素类型(type=array时) |

**Example**:
```json
{
  "type": "object",
  "properties": {
    "tool_names": {
      "type": "array",
      "description": "Optional list of tool names to filter",
      "items": {"type": "string"}
    }
  },
  "required": [],
  "additionalProperties": false
}
```

---

### 3. ToolDescription

**描述**: 从`tool_descriptions.yaml`加载的工具描述文本。

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | str | Yes | 工具名(YAML键) |
| `text` | str | Yes | 多行描述文本 |

**Storage Format (YAML)**:
```yaml
list_directory: |
  列出指定目录下的所有文件和子目录。
  支持按名称/时间排序,可限制返回数量。
```

**Validation Rules**:
- `tool_name` must match existing MCP tool
- `text` length: 20-500 characters
- Must not contain placeholder text `[Description pending]` in production

---

### 4. ToolExample

**描述**: 从`tool_examples.yaml`加载的使用示例代码。

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_name` | str | Yes | 工具名(YAML键) |
| `code` | str | Yes | Python调用代码 |
| `comment` | str | No | 示例说明(从代码注释提取) |

**Storage Format (YAML)**:
```yaml
list_directory:
  - |
    # 列出当前目录,按修改时间排序
    list_directory(path=".", sort_by="mtime")
  - |
    # 列出src/目录
    list_directory(path="src")
```

**Validation Rules**:
- `code` must be valid Python syntax
- Max 10 lines per example
- Comment line (starting with `#`) is optional

---

### 5. UsageGuideDocument

**描述**: 生成的最终混合格式文档字符串。

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | str | Yes | Markdown格式的完整文档 |
| `tool_count` | int | Yes | 包含的工具数量 |
| `size_bytes` | int | Yes | 文档字节数 |

**Structure (Markdown)**:
```markdown
# Context MCP Tools Usage Guide

Generated: 2025-10-04 | Tools: 11 | Category Filter: None

## Navigation Tools (3)

### list_directory
**Purpose**: 列出指定目录下的所有文件和子目录...

**Parameters**:
```json
{
  "type": "object",
  "properties": {...}
}
```

**Example**:
```python
list_directory(path=".", sort_by="mtime")
```

**Returns**: 文件列表,包含名称、类型、大小、修改时间...

---
(Repeat for other tools in category)

## Search Tools (4)
...

## Read Tools (4)
...
```

**Constraints**:
- Max size: 50KB (prevents LLM context overflow)
- Min tool count: 1 (at least one tool after filtering)
- Markdown must be valid CommonMark

---

### 6. GuideResponse

**描述**: `get_tool_usage_guide`工具返回的完整响应对象。

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | str | Yes | UsageGuideDocument.content |
| `warnings` | List[str] | No | 无效工具名警告列表 |
| `metadata` | ResponseMetadata | Yes | 响应元数据 |

**ResponseMetadata SubSchema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `total_tools` | int | Yes | 系统中所有工具总数 |
| `filtered_count` | int | Yes | 过滤后返回的工具数 |
| `invalid_names` | List[str] | No | tool_names中无效的名称 |
| `generation_time_ms` | float | No | 文档生成耗时(毫秒) |

**Example Response**:
```json
{
  "content": "# Context MCP Tools Usage Guide\n...",
  "warnings": [
    "Tool 'nonexistent' not found. Available: list_directory, search_in_files, ..."
  ],
  "metadata": {
    "total_tools": 11,
    "filtered_count": 2,
    "invalid_names": ["nonexistent"],
    "generation_time_ms": 8.3
  }
}
```

---

## Data Flow Diagram

```
[FastMCP Registry] ──(1)──> [SchemaExtractor] ──┐
                                                  │
[tool_descriptions.yaml] ──(2)──> [YAMLLoader] ──┤
                                                  ├──> [ToolMetadata]
[tool_examples.yaml] ──(3)──> [YAMLLoader] ──────┘
                                                  │
                                                  v
                                           [DocGenerator]
                                                  │
                                                  v
                                         [UsageGuideDocument]
                                                  │
                                                  v
                                           [GuideResponse]
```

**Flow Steps**:
1. Schema提取器通过FastMCP API获取所有工具的input_schema
2. YAML加载器读取手动维护的描述文件
3. YAML加载器读取手动维护的示例文件
4. 聚合为ToolMetadata对象列表
5. 文档生成器应用Jinja2模板渲染Markdown
6. 包装为GuideResponse返回给客户端

---

## State Transitions

### ToolMetadata Lifecycle

```
[Unregistered] ──register in FastMCP──> [SchemaOnly]
                                            │
                                            v
                              [Add description in YAML]
                                            │
                                            v
                                       [Documented]
                                            │
                                            v
                                [Add examples in YAML]
                                            │
                                            v
                                      [Complete] ✅
```

**States**:
- **Unregistered**: 工具未在FastMCP注册(不可用)
- **SchemaOnly**: 工具已注册,但YAML中缺失描述/示例
- **Documented**: 有描述但无示例
- **Complete**: 描述+示例均完整

**Validation**: 文档生成时,SchemaOnly状态的工具使用占位符`[Description pending]`。

---

## Invariants & Constraints

### System-Wide Invariants
1. **Schema一致性**: `ToolMetadata.input_schema` MUST 与FastMCP注册的Schema完全一致
2. **唯一性**: `ToolMetadata.name` MUST 在系统中唯一
3. **完整性**: 所有FastMCP注册的工具 MUST 在YAML中有对应条目(允许占位符)

### Runtime Constraints
1. **文档大小上限**: `UsageGuideDocument.size_bytes` ≤ 50KB
2. **生成时间上限**: 全量文档生成 ≤ 100ms
3. **缓存一致性**: YAML文件修改后,缓存MUST在下次调用时刷新

### Validation Gates
- **Contract Test Gate**: Schema结构必须符合JSON Schema Draft 2020-12
- **Integration Test Gate**: 生成的Markdown必须能被CommonMark解析器验证
- **Unit Test Gate**: YAML加载必须处理缺失文件/损坏格式/空文件

---

## Summary

**Primary Entities**: 6个
**Relationships**: 3个组合关系
**External Dependencies**: FastMCP Registry, 2个YAML文件
**Data Flow Complexity**: 线性流(无循环依赖)
**State Machine**: 1个(ToolMetadata生命周期)

**Key Design Decisions**:
- Schema自动提取保证100%一致性
- 双YAML文件分离关注点(描述vs示例)
- GuideResponse包含警告而非抛出异常(优雅降级)
- 元数据字段包含性能指标(generation_time_ms)便于监控
