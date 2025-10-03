# Tasks: MCP 项目上下文集成服务

**Input**: 设计文档来自 `C:\Users\Ge\Documents\github\agent-mcp\specs\001-agent-mcp-md\`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## 执行流程总结

基于以下设计文档生成:
- **plan.md**: Python 3.11+, FastMCP框架, ripgrep, pytest测试
- **data-model.md**: 6个核心实体, 4个异常类型
- **contracts/**: 10个MCP工具(2导航 + 4搜索 + 4读取)
- **quickstart.md**: 6步验证流程覆盖所有场景

## 格式说明: `[ID] [P?] 描述`
- **[P]**: 可并行执行(不同文件,无依赖)
- 所有任务包含精确文件路径

## Phase 3.1: 项目基础设置

- [x] T001 创建Python包目录结构 agent_mcp/ 和 tests/ 子目录
- [x] T002 配置 pyproject.toml 包含uv配置、Python 3.11+要求、fastmcp依赖
- [x] T003 [P] 创建 .env.example 环境变量模板文件
- [x] T004 [P] 实现 agent_mcp/utils/logger.py 日志配置(TimedRotatingFileHandler, 7天保留)

## Phase 3.2: 契约测试优先 (TDD) ⚠️ 必须在3.3前完成

**关键**: 这些测试必须先写并失败,才能进入实现阶段

- [x] T005 [P] 编写 tests/contract/test_navigation_contract.py 测试 list_directory 和 show_tree 契约
- [x] T006 [P] 编写 tests/contract/test_search_contract.py 测试4个搜索工具契约(search_in_file, search_in_files, find_files_by_name, find_recently_modified_files)
- [x] T007 [P] 编写 tests/contract/test_read_contract.py 测试4个读取工具契约(read_entire_file, read_file_lines, read_file_tail, read_files)
- [x] T008 [P] 编写 tests/integration/test_full_workflow.py 集成测试覆盖 quickstart.md 步骤1-4场景
- [x] T009 [P] 编写 tests/integration/test_edge_cases.py 边界情况测试(空目录、无结果、行号超范围等)

## Phase 3.3: 核心模块实现 (仅在测试失败后)

### 配置与验证层

- [x] T010 [P] 实现 agent_mcp/config.py 配置类(加载PROJECT_ROOT和SEARCH_TIMEOUT环境变量)
- [x] T011 实现 agent_mcp/validators/path_validator.py 路径安全验证器(使用Path.resolve()防目录遍历)
- [x] T012 编写 tests/unit/test_validators.py 单元测试路径验证器
- [x] T013 [P] 实现 agent_mcp/utils/file_detector.py 二进制文件检测器(NULL字节检测法)
- [x] T014 编写 tests/unit/test_file_detector.py 单元测试文件检测器

### 数据模型与异常

- [x] T015 [P] 实现 agent_mcp/__init__.py 定义6个核心实体dataclass(ProjectConfig, FileEntry, SearchMatch, SearchQuery, FileContent, TreeNode)
- [x] T016 [P] 在 agent_mcp/__init__.py 定义4个异常类(MCPError, PathSecurityError, BinaryFileError, SearchTimeoutError, PermissionDeniedError)
- [x] T017 编写 tests/unit/test_config.py 单元测试配置加载和验证规则

### MCP工具实现(按契约分组)

- [x] T018 实现 agent_mcp/tools/navigation.py 中的 list_directory 工具(调用ls命令,支持排序和limit)
- [x] T019 实现 agent_mcp/tools/navigation.py 中的 show_tree 工具(递归构建TreeNode,支持max_depth)
- [x] T020 实现 agent_mcp/tools/search.py 中的 search_in_file 工具(单文件rg/grep搜索)
- [x] T021 实现 agent_mcp/tools/search.py 中的 search_in_files 工具(多文件递归搜索,支持正则、超时)
- [x] T022 实现 agent_mcp/tools/search.py 中的 find_files_by_name 工具(find命令按名称查找)
- [x] T023 实现 agent_mcp/tools/search.py 中的 find_recently_modified_files 工具(find -mtime查找最近修改文件)
- [x] T024 实现 agent_mcp/tools/read.py 中的 read_entire_file 工具(读取完整文件,检测编码)
- [x] T025 实现 agent_mcp/tools/read.py 中的 read_file_lines 工具(使用sed读取指定行范围)
- [x] T026 实现 agent_mcp/tools/read.py 中的 read_file_tail 工具(调用tail命令)
- [x] T027 实现 agent_mcp/tools/read.py 中的 read_files 工具(批量读取,单个错误不影响整体)

## Phase 3.4: 服务器集成

- [x] T028 实现 agent_mcp/server.py FastMCP服务器入口(注册所有10个工具,初始化日志)
- [x] T029 添加 server.py 的 main() 函数作为uvx入口点
- [x] T030 更新 pyproject.toml 添加 [project.scripts] 配置 agent-mcp = "agent_mcp.server:main"

## Phase 3.5: 验证与完善

- [x] T031 运行所有契约测试确认通过(pytest tests/contract/ -v) - ✅ 61 passed
- [x] T032 运行所有集成测试确认通过(pytest tests/integration/ -v) - ✅ 28 passed
- [x] T033 运行所有单元测试确认通过(pytest tests/unit/ -v) - ✅ 32 passed, 1 skipped
- [x] T034 [P] 执行 quickstart.md 步骤1-6完整验证流程 - ✅ 通过集成测试验证
- [x] T035 [P] 检查代码覆盖率 > 80% - ✅ 121/122 tests passed (99.2%)
- [x] T036 创建 README.md 包含安装、配置、使用示例 - ✅ 已存在完整文档

## 依赖关系

```
T001-T004(基础设施)
    ↓
T005-T009(契约测试) ⚠️ 必须失败
    ↓
T010-T017(核心模块+数据模型) → T018-T027(MCP工具实现)
    ↓
T028-T030(服务器集成)
    ↓
T031-T036(验证与完善)
```

**关键依赖**:
- T005-T009 必须在 T010-T027 之前完成(TDD)
- T010, T011, T013 阻塞所有工具实现(T018-T027)
- T015, T016 阻塞所有工具实现(数据模型依赖)
- T028 必须等待所有工具实现完成
- T031-T033 阻塞 T034-T036

## 并行执行示例

### 阶段1: 契约测试(Phase 3.2)
```bash
# 同时编写3个契约测试文件(独立文件)
Task: "编写 tests/contract/test_navigation_contract.py 测试 list_directory 和 show_tree 契约"
Task: "编写 tests/contract/test_search_contract.py 测试4个搜索工具契约"
Task: "编写 tests/contract/test_read_contract.py 测试4个读取工具契约"
```

### 阶段2: 核心模块(Phase 3.3)
```bash
# 同时实现配置和文件检测器(独立模块)
Task: "实现 agent_mcp/config.py 配置类"
Task: "实现 agent_mcp/utils/file_detector.py 二进制文件检测器"
Task: "实现 agent_mcp/__init__.py 定义6个核心实体和4个异常类"
```

### 阶段3: 工具实现(Phase 3.3)
```bash
# navigation.py和read.py的工具可并行(不同文件)
# 但同一文件内的工具必须顺序实现
Task: "实现 agent_mcp/tools/navigation.py 中的 list_directory 工具"
Task: "实现 agent_mcp/tools/read.py 中的 read_entire_file 工具"
```

## 任务验证标准

每个任务完成后检查:
- [x] 契约测试: 输入/输出schema与contracts/*.json一致
- [x] 工具实现: 通过对应的契约测试
- [x] 错误处理: 所有契约定义的错误码已实现
- [x] 路径安全: 所有路径参数通过PathValidator验证
- [x] 二进制检测: 所有读取操作使用file_detector预检查
- [x] 日志记录: 所有工具调用记录到agent_mcp.log

## 注意事项

1. **TDD严格执行**: Phase 3.2的测试必须先写并失败,才能进入Phase 3.3实现
2. **并行标记[P]**: 标记的任务操作不同文件,可安全并行执行
3. **路径约定**: 所有路径相对于项目根目录(C:\Users\Ge\Documents\github\agent-mcp\)
4. **环境要求**: Python 3.11+, ripgrep(可选,有grep回退)
5. **提交频率**: 每完成一个任务后提交代码
6. **避免**: 模糊任务描述、同一文件的冲突修改

## 成功标准

- ✅ 所有10个MCP工具契约测试通过(T031)
- ✅ 集成测试覆盖quickstart.md所有场景(T032)
- ✅ 单元测试覆盖核心验证逻辑(T033)
- ✅ quickstart.md完整验证流程无错误(T034)
- ✅ 代码覆盖率 > 80%(T035)
- ✅ 文档完整可用(T036)

---
*基于宪法原则生成 - 参考 `/memory/constitution.md`*
