
# Implementation Plan: Tool Usage Guide Tool

**Branch**: `004-tool-tool-prompt` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `C:\Users\Ge\Documents\github\context-mcp\specs\004-tool-tool-prompt\spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
新增一个MCP工具 `get_tool_usage_guide`,返回所有现有工具的详细使用文档。文档采用混合格式(Markdown外壳+JSON Schema片段),支持按tool_names数组过滤特定工具。每个工具文档包含:名称、用途、参数Schema(自动提取)、描述和示例(手动维护)。无效工具名返回警告但继续处理有效工具。此工具帮助LLM Agent在实际调用工具前学习正确用法,提升调用成功率。

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: FastMCP (MCP protocol), inspect模块 (运行时反射), pathlib (文件路径)
**Storage**: 文件系统 (手动维护的tool_descriptions.yaml + tool_examples.yaml)
**Testing**: pytest (contract/integration/unit三层测试)
**Target Platform**: Cross-platform (Windows/Linux/macOS), 通过uvx零安装部署
**Project Type**: single (MCP服务器单体项目)
**Performance Goals**: <100ms响应时间 (文档生成+Schema提取), 支持动态工具数量扩展
**Constraints**: 文档总大小<50KB (避免超LLM上下文窗口), Schema提取必须与实际工具定义100%一致
**Scale/Scope**: 当前11个工具, 设计支持扩展至50+工具而无性能降级

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Security First ✅ PASS
- **Read-only operations**: 工具仅读取MCP装饰器元数据和YAML配置文件,无写入/修改操作
- **Path validation**: YAML文件路径使用pathlib.Path.resolve()验证,限定在项目根目录
- **Binary detection**: N/A (仅读取YAML文本文件)
- **Permission handling**: 文件读取失败返回友好错误信息,不暴露系统路径
- **Directory traversal prevention**: YAML文件路径硬编码,无用户输入路径

### II. Test-Driven Development ✅ PASS
- **TDD cycle**: 契约测试 → 集成测试 → 单元测试 → 实现
- **Test-first**: Phase 1生成所有测试(failing),Phase 4实现
- **Coverage target**: 维持99.2%覆盖率,新增工具函数必须100%覆盖

### III. Three-Layer Testing ✅ PASS
- **Contract tests**: 验证get_tool_usage_guide的JSON Schema输出格式
- **Integration tests**: 完整场景 (无参数→全部文档, 过滤→部分文档, 无效名称→警告)
- **Unit tests**: Schema提取逻辑、YAML加载、Markdown生成、过滤逻辑

### IV. Simplicity & Maintainability ✅ PASS
- **Single responsibility**: 工具函数仅协调Schema提取+YAML加载+Markdown生成
- **Max nesting**: 2层 (if tool_names存在 → for each tool)
- **Type hints**: 所有函数签名包含完整类型注解
- **Docstrings**: Google style文档说明
- **No premature optimization**: 使用dict查找而非复杂索引结构

### V. Performance with Fallback ⚠️ ATTENTION
- **High-performance tools**: N/A (无外部工具依赖)
- **Fallback strategy**: inspect模块为Python标准库,无需fallback
- **Timeout**: 文档生成为内存操作,无subprocess调用,不需要timeout
- **Performance degradation**: YAML文件缓存在内存,重复调用O(1)复杂度
- **注意事项**: 如果工具数量>50,考虑lazy load YAML或分页返回

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
context_mcp/
├── server.py                      # FastMCP服务器入口 (已存在,需注册新工具)
├── config.py                      # 环境变量配置 (无需修改)
├── tools/
│   ├── __init__.py
│   ├── navigation.py              # 已存在: list_directory, show_tree
│   ├── search.py                  # 已存在: 4个搜索工具
│   ├── read.py                    # 已存在: 4个读取工具
│   └── guide.py                   # 新增: get_tool_usage_guide工具实现
├── utils/
│   ├── __init__.py
│   ├── schema_extractor.py        # 新增: 从FastMCP装饰器提取Schema
│   └── doc_generator.py           # 新增: 生成混合格式文档
└── data/
    ├── tool_descriptions.yaml     # 新增: 手动维护的工具描述
    └── tool_examples.yaml         # 新增: 手动维护的使用示例

tests/
├── contract/
│   └── test_get_tool_usage_guide_contract.py  # 新增: Schema验证
├── integration/
│   └── test_tool_guide_scenarios.py           # 新增: 完整场景测试
└── unit/
    ├── test_schema_extractor.py               # 新增: Schema提取单元测试
    └── test_doc_generator.py                  # 新增: 文档生成单元测试
```

**Structure Decision**: 单体项目结构,新增工具遵循现有模式放置在`tools/guide.py`,辅助逻辑放入`utils/`。手动维护的描述和示例集中在新建的`data/`目录,便于非技术人员编辑。测试文件遵循三层测试结构。

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. **Contract Tests** (from `contracts/get_tool_usage_guide.json`)
   - test_get_tool_usage_guide_contract.py: 验证输入Schema、输出Schema、5个测试场景 [P]
2. **Data Model Setup** (from `data-model.md`)
   - 创建 context_mcp/data/ 目录和YAML模板文件 [P]
   - 填充 tool_descriptions.yaml (12个工具的描述) [P]
   - 填充 tool_examples.yaml (12个工具的示例) [P]
3. **Unit Tests** (从bottom-up设计)
   - test_schema_extractor.py: 测试FastMCP元数据提取逻辑 [P]
   - test_doc_generator.py: 测试Markdown生成、Jinja2模板渲染 [P]
4. **Integration Tests** (from `quickstart.md` scenarios)
   - test_tool_guide_scenarios.py: 5个acceptance scenarios的集成测试
5. **Implementation Tasks** (TDD顺序,使测试通过)
   - 实现 utils/schema_extractor.py (Schema提取+缓存)
   - 实现 utils/doc_generator.py (Jinja2模板+Markdown生成)
   - 实现 tools/guide.py (工具主函数,协调上述模块)
   - 在 server.py 注册工具

**Ordering Strategy**:
- Phase A: 并行创建测试和数据文件 (tasks 1-7, 全部[P])
- Phase B: 串行实现 (依赖关系: schema_extractor → doc_generator → guide.py → server.py)
- Phase C: Quickstart验证 (最后1个task)

**Dependency Graph**:
```
[Contract Test] ─┐
[Unit Tests]     ├─> [schema_extractor] ─> [doc_generator] ─> [guide.py] ─> [server.py]
[Data YAMLs]     ─┘                                                             │
[Integration Test] ─────────────────────────────────────────────────────────────┘
                                                                                 v
                                                                         [Quickstart]
```

**Estimated Output**: 12-15 tasks in tasks.md (精简设计,避免过度细分)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, CLAUDE.md updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (all principles satisfied)
- [x] Post-Design Constitution Check: PASS (no violations introduced)
- [x] All NEEDS CLARIFICATION resolved (via research.md)
- [x] Complexity deviations documented (none - design is simple)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
