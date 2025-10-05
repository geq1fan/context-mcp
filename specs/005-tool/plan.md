
# Implementation Plan: 测试用例覆盖完整性增强

**Branch**: `005-tool` | **Date**: 2025-10-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-tool/spec.md`

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
为11个MCP工具(3个导航、4个搜索、4个读取)补充契约测试用例,实现100%参数覆盖率。当前测试套件已覆盖基本功能和错误路径,但缺少边界值测试、参数组合测试和特殊场景验证。通过系统化补充测试用例,确保每个参数的默认值、枚举值、约束边界都有对应验证,提升回归检测能力和代码可维护性。

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest (测试框架), FastMCP (已有,仅测试调用)
**Storage**: N/A (测试仅验证工具函数行为)
**Testing**: pytest with contract/integration/unit layers (Three-Layer Testing原则)
**Target Platform**: Cross-platform (Windows/Linux/macOS) - 现有测试已支持
**Project Type**: Single (Python MCP server)
**Performance Goals**: N/A (测试执行速度非关键指标)
**Constraints**: 测试用例必须独立、可重复、快速执行(<1s per test class)
**Scale/Scope**: 11个工具 × 平均4个参数 = 约40-50个新增测试用例

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Security First (NON-NEGOTIABLE)
✅ **PASS** - 测试用例本身不涉及安全风险,仅验证现有工具的安全约束(路径验证、二进制检测)

### II. Test-Driven Development (NON-NEGOTIABLE)
✅ **PASS** - 本feature本身即是补充测试,遵循TDD原则:
- 新增测试用例将先编写(Red phase)
- 验证现有实现是否通过(Green phase)
- 如发现bug则修复代码(Refactor phase)

### III. Three-Layer Testing
✅ **PASS** - 聚焦contract层测试补充,符合三层测试架构
- Contract tests: 新增参数边界、枚举、组合测试
- Integration/Unit tests: 保持现有覆盖

### IV. Simplicity & Maintainability
✅ **PASS** - 测试用例设计遵循简单性原则:
- 每个测试一个明确目的(Single Responsibility)
- 清晰的docstring说明测试意图
- 使用pytest fixtures复用测试夹具
- 避免过度参数化导致的复杂性

### V. Performance with Fallback Strategy
✅ **PASS** - 不涉及性能优化,测试执行速度受pytest控制

**Initial Constitution Check Result**: ✅ PASS - 无violations需记录

## Project Structure

### Documentation (this feature)
```
specs/005-tool/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
└── contracts/           # Phase 1 output (/plan command) - 测试覆盖清单
```

### Source Code (repository root)
```
context_mcp/
└── tools/
    ├── navigation.py       # list_directory, show_tree, read_project_context
    ├── search.py          # search_in_file, search_in_files, find_files_by_name, find_recently_modified_files
    └── read.py            # read_entire_file, read_file_lines, read_file_tail, read_files

tests/
├── contract/              # 本feature主要修改目录
│   ├── test_navigation_contract.py  # 补充list_directory参数组合测试
│   ├── test_search_contract.py      # 补充search_in_files边界值测试
│   └── test_read_contract.py        # 补充read_file_lines/tail边界测试
├── integration/
│   └── (保持不变)
└── unit/
    └── (保持不变)
```

**Structure Decision**: 单体Python项目,聚焦`tests/contract/`目录的3个测试文件。无需修改源码(context_mcp/tools/),仅补充测试覆盖。

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
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from `contracts/test-coverage-checklist.md` (29个测试缺口)
- 按文件分组: test_navigation → test_search → test_read
- 按优先级排序: High(14) → Medium(14) → Low(1)
- 每个测试用例 → 独立task (避免批量task导致部分失败难追踪)

**Task Structure**:
```
1. [P] Add test_list_directory_limit_zero (navigation.py:22-27)
2. [P] Add test_list_directory_limit_one (navigation.py:22-27)
3. [P] Add test_max_depth_zero_rejected (navigation.py:110-132)
...
```

**Ordering Strategy**:
- **TDD order**: 测试编写 → 执行验证 → 修复bug(如有) → 重新验证
- **File grouping**: 同一测试文件的测试连续排列(减少上下文切换)
- **Parallel execution**: 所有测试task标记[P](文件互不依赖)
- **Final validation**: 最后3个task为覆盖率检查、quickstart验证、文档更新

**Estimated Output**: 32个tasks
- 29个测试补充tasks (按checklist)
- 1个覆盖率验证task
- 1个quickstart执行task
- 1个文档更新task (CLAUDE.md, coverage badge)

**Dependency Graph**:
```
Tasks 1-29 [P] (测试补充,独立并行)
    ↓
Task 30 (覆盖率验证,依赖全部测试完成)
    ↓
Task 31 (quickstart验证,依赖覆盖率通过)
    ↓
Task 32 (文档更新,依赖验证完成)
```

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
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (无TC中的NEEDS CLARIFICATION标记)
- [x] Complexity deviations documented (无violations需记录)

**Artifacts Generated**:
- [x] `research.md` - 测试现状分析和覆盖缺口详细列表
- [x] `data-model.md` - 测试覆盖追踪实体定义
- [x] `contracts/test-coverage-checklist.md` - 29个测试用例清单
- [x] `quickstart.md` - 7步验证流程
- [x] `CLAUDE.md` - 已更新项目上下文

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
