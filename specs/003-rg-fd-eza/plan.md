
# Implementation Plan: 性能优化工具集成与降级策略

**Branch**: `003-rg-fd-eza` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/003-rg-fd-eza/spec.md`

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
优先使用高性能工具(ripgrep/fd/eza)进行文件搜索、查找和列表操作,当工具不可用时自动降级到标准工具(grep/find/ls)。在README中提供性能对比数据和安装指引,覆盖小型和中型项目场景的测试基准。

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: fastmcp, subprocess, shutil (工具检测), ripgrep/fd/eza (系统工具,非Python依赖)
**Storage**: N/A
**Testing**: pytest (contract/integration/unit tests)
**Target Platform**: 跨平台 (Windows/Linux/macOS)
**Project Type**: single (context_mcp/)
**Performance Goals**: 小型项目(<1000文件,<10MB)和中型项目(1000-10000文件,10MB-100MB)下可测量的性能提升
**Constraints**: 工具不可用时必须降级,降级过程对MCP客户端透明,输出格式保持一致
**Scale/Scope**: 3个工具对(rg/grep, fd/find, eza/ls), 3个平台(Windows/Linux/macOS), 2个测试场景(小型/中型项目)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS (宪法文件为空模板,无约束要求)

无需检查的约束项。

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
├── tools/
│   ├── search.py          # 扩展rg降级逻辑
│   ├── navigation.py      # 添加eza支持
│   └── (其他现有工具)
├── utils/
│   └── tool_detector.py   # 新增:工具检测模块
└── server.py              # 添加启动检测

tests/
├── contract/
│   ├── test_search_contract.py
│   └── test_navigation_contract.py
├── integration/
│   └── test_tool_fallback.py  # 新增:降级集成测试
└── unit/
    └── test_tool_detector.py  # 新增:工具检测单元测试

README.md                  # 扩展:性能对比章节
```

**Structure Decision**: 单体项目结构,在现有context_mcp/包内扩展。新增工具检测模块(utils/tool_detector.py)统一管理工具可用性检测,在search.py和navigation.py中调用。测试层新增降级场景的集成测试。

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

**Output**: ✅ [research.md](./research.md) - 完成工具能力对比、跨平台兼容性、性能测试方法研究。关键决策:fd/rg集成但不集成eza(避免反优化),使用shutil.which()检测,硬编码参数映射。

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

**Output**: ✅ [data-model.md](./data-model.md), [contracts/tool-detector.md](./contracts/tool-detector.md), [quickstart.md](./quickstart.md), [CLAUDE.md](../../CLAUDE.md) 已生成

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. **从 contracts/ 生成契约测试任务**:
   - `test_tool_detector_unit.py` - ToolDetector单元测试 [P]

2. **从 data-model.md 生成实现任务**:
   - 创建 `context_mcp/utils/tool_detector.py` - ToolDetector模块 [P]
   - 扩展 `context_mcp/tools/search.py` - 添加grep降级层和fd支持
   - 扩展 `context_mcp/server.py` - 启动时工具检测和日志

3. **从 quickstart.md 生成集成测试任务**:
   - `test_tool_fallback.py` - 搜索/查找工具降级集成测试
   - `test_cross_platform.py` - 跨平台兼容性测试

4. **文档任务**:
   - 扩展 `README.md` - 添加性能对比章节和安装指引
   - 创建 `scripts/benchmark.py` - 性能基准测试脚本(可选)

**Ordering Strategy**:
- TDD顺序: 测试先行 (ToolDetector单元测试 → ToolDetector实现)
- 依赖顺序: ToolDetector → search.py扩展 → server.py集成 → 集成测试
- 标记 [P] 的任务可并行执行(独立文件)

**Estimated Output**: 15-18个有序任务,包含:
- 3个单元测试任务
- 3个实现任务
- 2个集成测试任务
- 2个文档任务

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
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS (无宪法约束)
- [x] Post-Design Constitution Check: PASS (无宪法约束)
- [x] All NEEDS CLARIFICATION resolved (已通过 /clarify)
- [x] Complexity deviations documented (无偏离)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
