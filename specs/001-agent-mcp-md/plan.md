
# Implementation Plan: MCP 项目上下文集成服务

**Branch**: `001-agent-mcp-md` | **Date**: 2025-10-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-agent-mcp-md/spec.md`

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
创建一个MCP服务,允许AI Agent通过标准化接口访问和分析任意项目的代码上下文。服务提供只读文件系统操作能力,包括目录导航、内容搜索和文件读取。基于fastmcp框架实现,通过环境变量配置项目根目录,遵循MCP协议标准,采用Unix系统命令(ls, find, rg, cat, sed, tail)实现核心功能。

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: fastmcp (MCP框架), ripgrep (rg命令)
**Storage**: 文件系统只读访问,日志文件存储(7天保留期)
**Testing**: pytest (单元测试、集成测试、契约测试)
**Target Platform**: 跨平台(Linux, macOS, Windows - 支持Unix命令的环境)
**Project Type**: single (独立Python包,通过uvx打包分发)
**Performance Goals**: 尽力而为策略,无严格响应时间要求,支持大型项目(数千个文件)
**Constraints**: 搜索操作超时(默认60秒,可配置),只读操作,路径限制在配置的根目录内
**Scale/Scope**: 单一MCP服务实例,支持一个配置的项目目录,约10个MCP工具函数

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**初始检查** (Phase 0前):
- ✅ **简洁性**: 单一职责MCP服务,聚焦只读文件系统操作
- ✅ **可测试性**: 每个MCP工具函数独立可测试,支持契约测试
- ✅ **标准化**: 遵循MCP协议标准,使用fastmcp框架
- ✅ **安全性**: 只读操作,路径验证,环境变量隔离配置
- ✅ **可观察性**: 日志记录所有API调用,7天保留期

**Phase 1后重新评估**:
- ✅ **模块化**: 工具按功能分组(navigation/search/read),职责明确
- ✅ **契约完整**: 10个工具全部定义JSON Schema契约
- ✅ **错误处理**: 4种异常类型覆盖所有边界情况
- ✅ **测试覆盖**: 三层测试金字塔(契约/集成/单元)
- ✅ **无新增复杂度**: 设计符合原计划,无架构偏离

**无宪法违规** - ✅ Phase 1设计通过验证

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
agent_mcp/                    # Python包主目录
├── __init__.py
├── server.py                 # FastMCP服务器入口
├── config.py                 # 配置管理(环境变量读取)
├── tools/                    # MCP工具函数实现
│   ├── __init__.py
│   ├── navigation.py         # 导航工具: list_directory, show_tree
│   ├── search.py             # 搜索工具: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files
│   └── read.py               # 读取工具: read_entire_file, read_file_lines, read_file_tail, read_files
├── validators/               # 路径验证和安全检查
│   ├── __init__.py
│   └── path_validator.py
└── utils/                    # 工具函数
    ├── __init__.py
    ├── file_detector.py      # 二进制文件检测
    └── logger.py             # 日志配置

tests/
├── contract/                 # MCP契约测试
│   ├── test_navigation_contract.py
│   ├── test_search_contract.py
│   └── test_read_contract.py
├── integration/              # 集成测试
│   ├── test_full_workflow.py
│   └── test_edge_cases.py
└── unit/                     # 单元测试
    ├── test_validators.py
    ├── test_file_detector.py
    └── test_config.py

pyproject.toml                # uv项目配置
README.md                     # 项目文档
.env.example                  # 环境变量示例
```

**Structure Decision**: 采用单一Python包结构。选择此结构因为:
1. MCP服务是独立的工具包,不涉及前后端分离
2. 通过uvx打包分发,需要标准Python包结构
3. 功能模块按MCP工具类型分组(导航、搜索、读取)更清晰
4. 测试分层明确(契约、集成、单元)

## Phase 0: Outline & Research

**已完成研究**:
1. ✅ FastMCP框架使用模式 - 装饰器模式,自动协议处理
2. ✅ Unix命令封装 - subprocess.run()带超时控制
3. ✅ 路径安全验证 - pathlib.Path.resolve()防目录遍历
4. ✅ 二进制文件检测 - NULL字节检测法
5. ✅ 环境变量配置 - PROJECT_ROOT + SEARCH_TIMEOUT
6. ✅ 日志策略 - TimedRotatingFileHandler,7天保留
7. ✅ MCP响应格式 - fastmcp自动生成标准格式
8. ✅ 测试策略 - 三层金字塔(契约/集成/单元)
9. ✅ 打包分发 - uv + uvx模式
10. ✅ ripgrep集成 - 优先rg,回退grep

**技术风险已识别**:
- ripgrep未安装: 提供grep回退
- 跨平台差异: subprocess统一接口
- 大文件OOM: 实现流式读取
- 符号链接循环: Path.resolve()自动处理

**Output**: ✅ research.md已创建,无NEEDS CLARIFICATION遗留

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

**已完成设计**:

1. ✅ **数据模型** → `data-model.md`:
   - 6个核心实体: ProjectConfig, FileEntry, SearchMatch, SearchQuery, FileContent, TreeNode
   - 4个异常类型: PathSecurityError, BinaryFileError, SearchTimeoutError, PermissionDeniedError
   - 完整的Python dataclass定义
   - 验证规则与需求映射

2. ✅ **MCP工具契约** → `/contracts/`:
   - `navigation_tools.json`: list_directory, show_tree (2个工具)
   - `search_tools.json`: search_in_file, search_in_files, find_files_by_name, find_recently_modified_files (4个工具)
   - `read_tools.json`: read_entire_file, read_file_lines, read_file_tail, read_files (4个工具)
   - 每个工具定义: inputSchema, outputSchema, errors, requirements映射

3. ✅ **快速开始指南** → `quickstart.md`:
   - 完整工作流验证步骤(6大步骤)
   - 每个工具的示例请求/响应
   - 安全边界验证场景
   - 边界情况测试
   - 故障排查指南

4. ✅ **Agent上下文** → `CLAUDE.md`:
   - 项目概述和技术栈
   - 核心设计决策
   - MCP工具清单
   - 安全约束
   - 最近变更记录

**Output**: ✅ data-model.md, contracts/*.json, quickstart.md, CLAUDE.md已创建

**契约测试任务** (将在Phase 2任务中生成):
- tests/contract/test_navigation_contract.py
- tests/contract/test_search_contract.py
- tests/contract/test_read_contract.py

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **基础设施任务** (优先级最高):
   - 创建项目结构(agent_mcp/, tests/)
   - 配置pyproject.toml (uv配置)
   - 环境变量模板 (.env.example)
   - 日志配置 (utils/logger.py)

2. **契约测试任务** (TDD优先):
   - tests/contract/test_navigation_contract.py [P]
   - tests/contract/test_search_contract.py [P]
   - tests/contract/test_read_contract.py [P]
   - 基于contracts/*.json,断言输入/输出schema
   - **这些测试初始应该失败**(无实现)

3. **核心模块实现** (按依赖顺序):
   - config.py (环境变量加载) [P]
   - validators/path_validator.py (路径安全)
   - utils/file_detector.py (二进制检测) [P]
   - 单元测试: tests/unit/test_validators.py, test_file_detector.py

4. **MCP工具实现** (按契约):
   - tools/navigation.py: list_directory, show_tree [P]
   - tools/search.py: 4个搜索工具 [P]
   - tools/read.py: 4个读取工具 [P]
   - 实现后契约测试应通过

5. **服务器入口**:
   - server.py (FastMCP初始化,工具注册)
   - 集成测试: tests/integration/test_full_workflow.py

6. **边界情况测试**:
   - tests/integration/test_edge_cases.py
   - 基于spec.md Edge Cases和quickstart.md验证场景

**Ordering Strategy**:
- **TDD严格执行**: 契约测试 → 实现 → 测试通过
- **依赖顺序**: 基础设施 → 工具类 → 核心逻辑 → 服务器
- **并行标记[P]**: 独立模块可并行开发
- **测试先行**: 每个模块的测试任务在实现任务之前

**预估任务数**: 30-35个任务
- 基础设施: 5个任务
- 契约测试: 3个任务
- 核心模块: 10个任务(含单元测试)
- MCP工具: 12个任务(3组,每组4个)
- 服务器与集成: 5个任务
- 文档与验证: 3个任务

**任务示例**:
```
1. [基础] 创建项目目录结构
2. [基础] 配置pyproject.toml
3. [测试] 编写导航工具契约测试 [P]
4. [测试] 编写搜索工具契约测试 [P]
5. [测试] 编写读取工具契约测试 [P]
6. [核心] 实现配置管理模块 [P]
7. [核心] 实现路径验证器
8. [核心] 编写路径验证器单元测试
9. [核心] 实现二进制文件检测器 [P]
10. [核心] 编写文件检测器单元测试
11. [工具] 实现list_directory工具
12. [工具] 实现show_tree工具
... (继续)
30. [验证] 执行quickstart.md完整验收
```

**成功标准**:
- ✅ 所有契约测试通过
- ✅ 所有单元测试通过
- ✅ 集成测试覆盖quickstart.md场景
- ✅ 边界情况测试覆盖spec.md Edge Cases
- ✅ 代码覆盖率 > 80%

**IMPORTANT**: Phase 2由/tasks命令执行,本节仅描述生成策略

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
- [ ] Phase 3: Tasks generated (/tasks command) - **下一步**
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (无偏离)

**Artifacts Created**:
- [x] plan.md (本文件)
- [x] research.md (10项技术决策)
- [x] data-model.md (6实体 + 4异常)
- [x] contracts/navigation_tools.json (2工具)
- [x] contracts/search_tools.json (4工具)
- [x] contracts/read_tools.json (4工具)
- [x] quickstart.md (完整验收流程)
- [x] CLAUDE.md (Agent上下文)

---
*Based on Constitution principles - See `/memory/constitution.md`*
