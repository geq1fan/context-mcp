# Feature Specification: Tool Usage Guide Tool

**Feature Branch**: `004-tool-tool-prompt`
**Created**: 2025-10-04
**Status**: Draft
**Input**: User description: "新增tool：返回所有tool具体用法的Prompt，这样每次使用mcp前，可以先调用该tool让llm学习工具用法"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature: Add a new MCP tool that returns usage documentation for all available tools
2. Extract key concepts from description
   → Actors: LLM agents using MCP service
   → Actions: Query tool documentation, learn tool usage patterns
   → Data: Tool metadata (names, parameters, descriptions, usage examples)
   → Constraints: Must be callable before using actual tools
3. For each unclear aspect:
   → All clarified via /clarify session
4. Fill User Scenarios & Testing section
   → User flow: LLM calls guide tool → receives documentation → uses actual tools correctly
5. Generate Functional Requirements
   → Tool must return comprehensive usage documentation
   → Documentation must be LLM-optimized for learning
6. Identify Key Entities
   → Tool metadata, usage patterns, parameter schemas
7. Run Review Checklist
   → WARNING: Spec has uncertainties regarding format and filtering
8. Return: SUCCESS (spec ready for planning after clarification)
```

---

## Clarifications

### Session 2025-10-04
- Q: 文档返回格式应该是什么? → A: 混合格式(Markdown外壳包含JSON Schema片段,兼顾可读性和结构化)
- Q: 工具是否支持过滤特定工具的文档? → A: 支持多工具过滤,可传递tool_names数组查询特定工具子集
- Q: 工具文档是否需要包含使用示例? → A: 必须包含示例,每个工具都提供典型调用场景的代码示例
- Q: 文档内容如何维护? → A: 混合方式,Schema从代码自动提取,描述和示例手动维护
- Q: 查询不存在的工具名时如何处理? → A: 警告继续,返回有效工具文档并附带无效工具名的警告列表

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
作为一个使用 Context MCP 服务的 LLM Agent,我需要在实际调用工具前先了解所有可用工具的详细用法,以便正确构造工具调用参数并理解每个工具的能力边界。

### Acceptance Scenarios
1. **Given** LLM agent刚连接到MCP服务, **When** 调用工具使用指南工具, **Then** 收到包含所有11个现有工具(导航3个+搜索4个+读取4个)的详细用法文档
2. **Given** 文档已获取, **When** LLM阅读某个工具的说明, **Then** 能够理解该工具的参数定义、用途、使用示例和返回值格式
3. **Given** LLM需要搜索文件内容, **When** 参考指南中的search_in_files说明, **Then** 能正确传递pattern、include_pattern等参数
4. **Given** LLM需要查询特定工具, **When** 传递tool_names数组["list_directory", "read_entire_file"], **Then** 仅收到这两个工具的文档,每个都包含代码示例
5. **Given** 用户传递tool_names数组["list_directory", "nonexistent_tool", "read_entire_file"], **When** 系统处理请求, **Then** 返回list_directory和read_entire_file的文档,并附带警告信息指出"nonexistent_tool"不存在

### Edge Cases
- 当新工具添加到MCP服务时,Schema自动提取,但描述和示例缺失如何处理(报错/返回不完整文档/使用默认占位符)?
- 文档内容过长超出LLM上下文窗口时如何处理?
- 如果tool_names数组为空,系统应返回所有工具还是空结果?
- 如果工具代码更新导致Schema变化,但手动维护的描述过时,如何检测和警告?

## Requirements

### Functional Requirements
- **FR-001**: 系统 MUST 提供一个新的MCP工具,允许LLM查询所有可用工具的使用文档
- **FR-002**: 文档 MUST 包含每个工具的以下信息:工具名称、用途描述、参数列表(含类型和是否必需)、返回值格式
- **FR-003**: 文档 MUST 针对LLM理解进行优化,使用清晰的自然语言描述和结构化格式
- **FR-004**: 工具 MUST 能够在不传递任何参数的情况下返回完整文档
- **FR-005**: 参数Schema MUST 从工具代码的装饰器和类型注解中自动提取,以确保与实际实现同步;工具描述和使用示例作为手动维护的静态资源存储
- **FR-006**: 系统 MUST 支持通过可选的tool_names数组参数过滤特定工具的文档;不传递参数时返回所有工具文档
- **FR-007**: 返回的文档 MUST 使用混合格式,即Markdown外壳包含嵌入的JSON Schema片段,以兼顾人类可读性和程序化处理能力
- **FR-008**: 每个工具的文档 MUST 包含典型调用场景的代码示例,展示参数传递和预期返回值
- **FR-009**: 当tool_names数组包含不存在的工具名时,系统 MUST 返回所有有效工具的文档,并在响应中包含无效工具名的警告列表

### Key Entities
- **Tool Metadata**: 工具的元信息,包括名称、描述、所属分类(导航/搜索/读取)
- **Parameter Schema**: 每个工具参数的定义,包括名称、类型、是否必需、默认值、取值范围
- **Usage Example**: 展示工具正确调用方式的示例,可能包含典型场景和边界情况
- **Return Format**: 工具执行成功或失败时的返回数据结构说明

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain (5 clarifications resolved)
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (5 clarifications completed via /clarify)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
