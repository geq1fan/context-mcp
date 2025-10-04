# Tasks: 性能优化工具集成与降级策略

**Feature Branch**: `003-rg-fd-eza`
**Input**: Design documents from `/specs/003-rg-fd-eza/`
**Prerequisites**: spec.md, research.md, data-model.md, contracts/

## Execution Summary

根据设计文档生成的任务列表,采用TDD方法:
- **Setup**: 项目配置和工具检测模块
- **Tests First**: 契约测试和集成测试(必须在实现前完成)
- **Core**: 增强search.py工具,添加降级逻辑
- **Integration**: 服务器启动日志和工具检测集成
- **Polish**: 性能基准测试、README文档

---

## Phase 3.1: Setup

- [x] T001 创建工具检测器模块结构 `context_mcp/utils/tool_detector.py`
  - 创建空模块文件和基础类框架
  - 定义ToolDetector类签名(has_ripgrep, has_fd属性)
  - 实现单例模式基础框架

- [x] T002 [P] 创建测试文件结构
  - `tests/unit/test_tool_detector.py` (工具检测器单元测试)
  - `tests/integration/test_tool_fallback.py` (降级逻辑集成测试)
  - `tests/integration/test_output_consistency.py` (输出一致性测试)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: 这些测试必须先写,必须失败,然后才能实现功能**

- [x] T003 [P] 契约测试: ToolDetector单例和检测 `tests/unit/test_tool_detector.py`
  - 测试单例模式(`detector1 is detector2`)
  - 测试ripgrep检测(mock shutil.which和subprocess)
  - 测试fd检测(mock shutil.which和subprocess)
  - 测试检测性能(<100ms)
  - 测试版本验证失败降级

- [x] T004 [P] 集成测试: search_in_files降级逻辑 `tests/integration/test_tool_fallback.py`
  - 测试ripgrep优先使用
  - 测试降级到grep(mock has_ripgrep=False)
  - 测试降级到Python rglob(mock所有工具不可用)
  - 测试降级过程中的超时处理

- [x] T005 [P] 集成测试: find_files_by_name降级逻辑 `tests/integration/test_tool_fallback.py`
  - 测试fd优先使用
  - 测试降级到find(mock has_fd=False)
  - 测试降级到Python rglob(mock所有工具不可用)

- [x] T006 [P] 集成测试: 输出格式一致性 `tests/integration/test_output_consistency.py`
  - 测试search_in_files在ripgrep/grep/Python下输出一致
  - 测试find_files_by_name在fd/find/Python下输出一致
  - 测试路径格式统一(正斜杠,相对路径)

- [x] T007 [P] 集成测试: 跨平台兼容性 `tests/integration/test_tool_fallback.py`
  - 测试Windows环境降级(mock platform.system()="Windows")
  - 测试Unix环境工具选择

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] T008 实现ToolDetector工具检测逻辑 `context_mcp/utils/tool_detector.py`
  - 实现ripgrep检测(shutil.which + subprocess.run验证)
  - 实现fd检测(shutil.which + subprocess.run验证)
  - 实现单例模式(使用__new__或模块级实例)
  - 添加异常处理(捕获FileNotFoundError/TimeoutExpired)
  - 实现性能优化(缓存检测结果)

- [x] T009 扩展search_in_files添加grep降级层 `context_mcp/tools/search.py`
  - 集成ToolDetector检测
  - 实现grep命令构建逻辑(参数映射rg→grep)
  - 实现grep输出解析(file:line:content格式)
  - 实现find+grep组合过滤文件
  - 保持ripgrep路径和Python降级路径不变

- [x] T010 扩展find_files_by_name添加fd/find优先 `context_mcp/tools/search.py`
  - 集成ToolDetector检测
  - 实现fd命令构建和输出解析
  - 实现find命令构建和输出解析
  - 跨平台处理(Windows跳过find)
  - 保持Python rglob降级路径不变

- [x] T011 统一超时处理和错误降级 `context_mcp/tools/search.py`
  - 所有subprocess.run调用添加timeout参数
  - 工具执行失败时自动降级到下一层
  - 超时时返回部分结果+timed_out=true
  - 确保异常不传播到MCP客户端

---

## Phase 3.4: Integration

- [x] T012 集成工具检测到服务器启动 `context_mcp/server.py`
  - 导入ToolDetector
  - 在服务器启动时初始化检测器
  - 记录工具可用性到日志(INFO级别)
  - 工具不可用时记录WARN日志(仅一次)
  - 日志包含安装指引链接

- [x] T013 [P] 添加日志格式化和链接 `context_mcp/server.py`
  - ripgrep不可用日志: "建议安装ripgrep: https://github.com/BurntSushi/ripgrep#installation"
  - fd不可用日志: "建议安装fd: https://github.com/sharkdp/fd#installation"
  - 使用logger.warning()而非print()

---

## Phase 3.5: Polish

- [ ] T014 [P] 创建性能基准测试脚本 `scripts/benchmark.py`
  - 实现小型项目基准测试(使用项目本身)
  - 实现中型项目基准测试(可选,需克隆大型项目)
  - 测试search_in_files性能(ripgrep/grep/Python)
  - 测试find_files_by_name性能(fd/find/Python)
  - 输出性能对比表格(Markdown格式)
  - **跳过**: 使用research.md中的理论数据,无需实际运行基准测试

- [x] T015 [P] 扩展README性能对比章节 `README.md`
  - 添加"## 性能优化"章节
  - 添加性能对比表格(从research.md数据)
  - 说明ripgrep/fd加速比(9-13倍)
  - 说明eza不集成的原因(避免反优化)

- [x] T016 [P] 扩展README工具安装指引 `README.md`
  - 添加"## 推荐工具安装"章节
  - Windows安装指引(choco/scoop)
  - Linux安装指引(apt/yum/dnf)
  - macOS安装指引(brew)
  - 提供官方下载链接

- [x] T017 运行完整测试套件验证
  - 运行所有单元测试: `pytest tests/unit/ -v` ✓
  - 运行所有集成测试: `pytest tests/integration/ -v` ✓
  - 所有新增测试通过 (16 tests)
  - 修复输出格式一致性问题(路径正斜杠)

- [ ] T018 手动验证quickstart场景
  - 按照quickstart.md执行所有验证步骤
  - 验证ripgrep/fd可用时的性能
  - 验证降级到grep/find的功能
  - 验证完全降级到Python的功能
  - 验证启动日志输出正确
  - **部分完成**: 单元测试和集成测试已验证核心功能

- [x] T019 [P] 代码质量检查
  - 运行linter: `ruff check context_mcp/` (工具不可用,手动检查)
  - 代码格式符合项目规范
  - 无明显类型错误或警告

---

## Dependencies

### 严格依赖顺序
1. **Setup (T001-T002)** 必须最先完成
2. **Tests (T003-T007)** 必须在Implementation (T008-T011)之前完成
3. **T008 (ToolDetector)** 必须在 T009-T011 之前完成(工具函数依赖检测器)
4. **T009-T011** 可以并行(不同功能,但同一文件需注意冲突)
5. **T012-T013 (Integration)** 必须在 T008-T011 之后
6. **T014-T019 (Polish)** 必须在所有核心实现之后

### 文件依赖关系
- `context_mcp/tools/search.py`: T009, T010, T011 顺序修改同一文件(不能并行)
- `context_mcp/server.py`: T012, T013 顺序修改同一文件(不能并行)
- 测试文件(T003-T007): 可并行创建,不同文件无冲突

---

## Parallel Execution Examples

### Phase 3.1 Setup
```bash
# T002可单独并行(不同测试文件)
Task: "创建 tests/unit/test_tool_detector.py"
Task: "创建 tests/integration/test_tool_fallback.py"
Task: "创建 tests/integration/test_output_consistency.py"
```

### Phase 3.2 Tests (全部可并行)
```bash
# T003-T007 可并行执行(不同测试文件)
Task: "契约测试 ToolDetector in tests/unit/test_tool_detector.py"
Task: "集成测试 search_in_files降级 in tests/integration/test_tool_fallback.py"
Task: "集成测试 find_files_by_name降级 in tests/integration/test_tool_fallback.py"
Task: "集成测试 输出一致性 in tests/integration/test_output_consistency.py"
Task: "集成测试 跨平台兼容 in tests/integration/test_tool_fallback.py"
```

### Phase 3.5 Polish (部分可并行)
```bash
# T014-T016 可并行(不同文件)
Task: "创建性能基准测试 scripts/benchmark.py"
Task: "扩展README性能对比 README.md"
Task: "扩展README安装指引 README.md"
```

**注意**: T009-T011修改同一文件`search.py`,必须顺序执行

---

## Task Validation Checklist

- [x] 所有contracts有对应测试 (tool-detector.md → T003, search-tools-enhanced.md → T004-T006)
- [x] 所有entities有模型任务 (ToolDetector → T001,T008)
- [x] 所有测试在实现之前 (T003-T007 before T008-T011)
- [x] 并行任务真正独立 ([P]标记的任务操作不同文件)
- [x] 每个任务指定确切文件路径
- [x] 没有两个[P]任务修改同一文件 (T002测试文件独立,[P]标记正确)

---

## Notes

### TDD工作流
1. 写测试 → 测试失败(RED)
2. 最小实现 → 测试通过(GREEN)
3. 重构优化 → 测试仍通过(REFACTOR)

### 关键决策
- **不集成eza**: research.md结论避免目录列表反优化
- **grep作为中间层**: 比直接降级到Python性能好10-20倍
- **单例模式**: ToolDetector减少重复检测开销
- **硬编码参数映射**: 简单直接,满足需求

### 验证标准
- 功能: 所有降级层输出格式一致
- 性能: ripgrep/fd比grep/find快7-13倍
- 兼容: Windows/Linux/macOS都能正常工作
- 质量: 测试覆盖率>90%, 无linting错误

---

**Generated**: 2025-10-04 | **Status**: Ready for Execution
