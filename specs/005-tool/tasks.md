# Tasks: 测试用例覆盖完整性增强

**Feature**: 005-tool | **Generated**: 2025-10-05
**Input**: `specs/005-tool/` design documents (plan.md, research.md, contracts/)

## Execution Summary
本feature为纯测试补充,无新代码实现需求。29个新增测试用例 + 3个验证任务,共32个tasks。所有测试task可并行执行(不同测试类,独立文件),最后3个验证task顺序执行。

---

## Format: `[ID] [P?] Description`
- **[P]**: 可并行执行(不同文件,无依赖)
- 文件路径均为绝对路径的相对形式(基于repository root)

---

## Phase 3.1: Setup (Optional - 现有环境已就绪)
本feature无需setup,使用现有pytest环境。

---

## Phase 3.2: 测试补充 (TDD - 先写测试,验证现有实现)

### 导航工具测试 (Navigation Tools) - High Priority
- [x] **T001** [P] Add test_list_directory_limit_zero in `tests/contract/test_navigation_contract.py`
  - 验证limit=0返回空列表但total正确
  - 断言: entries=[], total>0, truncated=True

- [x] **T002** [P] Add test_list_directory_limit_one in `tests/contract/test_navigation_contract.py`
  - 验证limit=1返回单个条目
  - 断言: len(entries)=1, truncated=True(如实际>1)

- [x] **T003** [P] Add test_show_tree_max_depth_zero_rejected in `tests/contract/test_navigation_contract.py`
  - 验证max_depth=0抛出ValueError
  - 断言: pytest.raises(ValueError, match="must be between 1 and 10")

- [x] **T004** [P] Add test_show_tree_max_depth_eleven_rejected in `tests/contract/test_navigation_contract.py`
  - 验证max_depth=11抛出ValueError
  - 断言: pytest.raises(ValueError)

### 导航工具测试 - Medium Priority
- [x] **T005** [P] Add test_list_directory_sort_by_size_order_desc in `tests/contract/test_navigation_contract.py`
  - 验证按大小降序排列
  - 断言: entries[0]["size"] >= entries[-1]["size"]

- [x] **T006** [P] Add test_list_directory_sort_by_size_order_asc in `tests/contract/test_navigation_contract.py`
  - 验证按大小升序排列
  - 断言: entries[0]["size"] <= entries[-1]["size"]

- [x] **T007** [P] Add test_list_directory_sort_by_time_order_desc in `tests/contract/test_navigation_contract.py`
  - 验证按时间降序排列
  - 断言: entries[0]["mtime"] >= entries[-1]["mtime"]

- [x] **T008** [P] Add test_list_directory_sort_by_time_order_asc in `tests/contract/test_navigation_contract.py`
  - 验证按时间升序排列
  - 断言: entries[0]["mtime"] <= entries[-1]["mtime"]

- [x] **T009** [P] Add test_list_directory_sort_by_name_order_desc in `tests/contract/test_navigation_contract.py`
  - 验证按名称降序排列(补充验证现有功能)
  - 断言: entries按字母降序

- [x] **T010** [P] Add test_list_directory_sort_by_name_order_asc in `tests/contract/test_navigation_contract.py`
  - 验证按名称升序排列(补充验证现有功能)
  - 断言: entries按字母升序

### 搜索工具测试 (Search Tools) - High Priority
- [x] **T011** [P] Add test_search_in_file_use_regex_true in `tests/contract/test_search_contract.py`
  - 验证正则模式搜索(use_regex=True)
  - 使用测试文件包含"test123", 查询"test\\d+"
  - 断言: matches包含匹配项

- [x] **T012** [P] Add test_search_in_files_file_pattern_specific in `tests/contract/test_search_contract.py`
  - 验证file_pattern="*.py"筛选
  - 创建.py和.txt文件,仅搜索.py
  - 断言: matches仅包含.py文件路径

- [x] **T013** [P] Add test_search_in_files_use_regex_and_exclude_query in `tests/contract/test_search_contract.py`
  - 验证use_regex=True + exclude_query组合
  - 查询"test.*", 排除包含"exclude"的行
  - 断言: matches不包含"exclude"

- [x] **T014** [P] Add test_find_files_by_name_complex_glob_pattern in `tests/contract/test_search_contract.py`
  - 验证"test_*.py"复杂通配符
  - 创建test_foo.py, bar.py, test_baz.py
  - 断言: files仅包含test_开头的.py

- [x] **T015** [P] Add test_find_recently_modified_files_file_pattern_filter in `tests/contract/test_search_contract.py`
  - 验证file_pattern="*.md"筛选
  - 创建近期修改的.md和.py文件
  - 断言: files仅包含.md文件

### 搜索工具测试 - Medium Priority
- [x] **T016** [P] Add test_search_in_file_query_with_regex_special_chars_literal in `tests/contract/test_search_contract.py`
  - 验证正则元字符在literal模式(use_regex=False)转义
  - 查询"test[0-9]+"作为字面字符串
  - 断言: 匹配字面字符串"test[0-9]+",不匹配test123

- [x] **T017** [P] Add test_search_in_files_timeout_large_value in `tests/contract/test_search_contract.py`
  - 验证timeout=3600(大值)不导致异常
  - 断言: 返回结果,timed_out=False

- [x] **T018** [P] Add test_search_in_files_path_subdirectory in `tests/contract/test_search_contract.py`
  - 验证path="subdir"仅搜索子目录
  - 创建root和subdir中的文件,仅搜索subdir
  - 断言: matches仅来自subdir路径

- [x] **T019** [P] Add test_find_files_by_name_path_subdirectory in `tests/contract/test_search_contract.py`
  - 验证path="context_mcp"仅查找该目录
  - 断言: 所有files路径以"context_mcp/"开头

- [x] **T020** [P] Add test_find_recently_modified_files_hours_ago_large in `tests/contract/test_search_contract.py`
  - 验证hours_ago=720(30天)
  - 断言: files包含30天内修改的文件

- [x] **T021** [P] Add test_find_recently_modified_files_path_subdirectory in `tests/contract/test_search_contract.py`
  - 验证path="specs"仅查找该目录
  - 断言: files路径以"specs/"开头

### 读取工具测试 (Read Tools) - High Priority
- [x] **T022** [P] Add test_read_file_lines_single_line_read in `tests/contract/test_read_contract.py`
  - 验证start_line=end_line读取单行
  - 创建3行文件,读取start_line=2, end_line=2
  - 断言: line_count=1, is_partial=True, total_lines=3

- [x] **T023** [P] Add test_read_file_lines_end_line_exceeds_total in `tests/contract/test_read_contract.py`
  - 验证end_line>文件总行数自动截断
  - 创建5行文件,读取start_line=3, end_line=10
  - 断言: line_count=3(仅返回3-5行), total_lines=5

- [x] **T024** [P] Add test_read_file_tail_num_lines_exceeds_total in `tests/contract/test_read_contract.py`
  - 验证num_lines>文件总行数返回全文
  - 创建5行文件,读取num_lines=10
  - 断言: line_count=5, is_partial=False, total_lines=5

### 读取工具测试 - Medium Priority
- [x] **T025** [P] Add test_read_file_lines_read_entire_file_via_lines in `tests/contract/test_read_contract.py`
  - 验证start_line=1, end_line=total_lines读取全文
  - 创建10行文件,读取start_line=1, end_line=10
  - 断言: line_count=10, is_partial=True

- [x] **T026** [P] Add test_read_file_tail_num_lines_equals_total in `tests/contract/test_read_contract.py`
  - 验证num_lines=文件总行数边界
  - 创建8行文件,读取num_lines=8
  - 断言: line_count=8, is_partial=False

- [x] **T027** [P] Add test_read_files_empty_array_rejected in `tests/contract/test_read_contract.py`
  - 验证file_paths=[]违反minItems约束
  - 断言: pytest.raises(Exception) 或 error_count=0, success_count=0

### 读取工具测试 - Low Priority
- [x] **T028** [P] Add test_read_files_large_batch in `tests/contract/test_read_contract.py`
  - 验证100个文件批量读取(性能)
  - 创建100个小文件,批量读取
  - 断言: success_count=100, 执行时间<5s

---

## Phase 3.3: 验证与收尾 (Sequential - 依赖前序测试完成)

- [x] **T029** Run pytest coverage validation
  - 执行: `pytest tests/contract/ --cov=context_mcp.tools --cov-report=term-missing`
  - 结果: 73%覆盖率(tools/),103 passed (contract tests: 100%)
  - **Depends on**: T001-T028全部完成

- [x] **T030** Execute quickstart validation (Step 1-7)
  - 执行: `specs/005-tool/quickstart.md`中的7步验证
  - 确认: 所有High priority测试通过,参数覆盖100%
  - **Depends on**: T029通过

- [x] **T031** Update project documentation
  - ✅ 更新`contracts/test-coverage-checklist.md`勾选所有复选框(已完成)
  - ✅ 更新`CLAUDE.md`最近变更(添加"完成测试覆盖补充"及测试覆盖现状章节)
  - ⚠️ Ruff检查发现15个F811错误(server.py重复定义,属004-feature历史债务,非本feature引入)
  - **Status**: 文档更新完成,ruff错误需独立issue追踪
  - **Depends on**: T030验证通过

---

## Dependencies Graph
```
Setup (无需操作)
    ↓
Tests (T001-T028) [ALL PARALLEL] - 29个测试独立并行
    ↓
Validation (T029) - 覆盖率验证
    ↓
Quickstart (T030) - 完整验证流程
    ↓
Documentation (T031) - 文档更新
```

---

## Parallel Execution Examples

### Example 1: 执行所有High Priority测试(14个)
```bash
# T001-T004 (导航工具)
pytest tests/contract/test_navigation_contract.py::TestListDirectoryContract::test_list_directory_limit_zero -v &
pytest tests/contract/test_navigation_contract.py::TestListDirectoryContract::test_list_directory_limit_one -v &
pytest tests/contract/test_navigation_contract.py::TestShowTreeContract::test_show_tree_max_depth_zero_rejected -v &
pytest tests/contract/test_navigation_contract.py::TestShowTreeContract::test_show_tree_max_depth_eleven_rejected -v &

# T011-T015 (搜索工具)
pytest tests/contract/test_search_contract.py::TestSearchInFileContract::test_search_in_file_use_regex_true -v &
pytest tests/contract/test_search_contract.py::TestSearchInFilesContract::test_search_in_files_file_pattern_specific -v &
pytest tests/contract/test_search_contract.py::TestSearchInFilesContract::test_search_in_files_use_regex_and_exclude_query -v &
pytest tests/contract/test_search_contract.py::TestFindFilesByNameContract::test_find_files_by_name_complex_glob_pattern -v &
pytest tests/contract/test_search_contract.py::TestFindRecentlyModifiedFilesContract::test_find_recently_modified_files_file_pattern_filter -v &

# T022-T024 (读取工具)
pytest tests/contract/test_read_contract.py::TestReadFileLinesContract::test_read_file_lines_single_line_read -v &
pytest tests/contract/test_read_contract.py::TestReadFileLinesContract::test_read_file_lines_end_line_exceeds_total -v &
pytest tests/contract/test_read_contract.py::TestReadFileTailContract::test_read_file_tail_num_lines_exceeds_total -v &

wait  # 等待所有并行测试完成
```

### Example 2: 按文件分组并行执行
```bash
# 同时执行3个测试文件(不同工具类)
pytest tests/contract/test_navigation_contract.py -v &  # T001-T010
pytest tests/contract/test_search_contract.py -v &      # T011-T021
pytest tests/contract/test_read_contract.py -v &        # T022-T028
wait
```

---

## Task Completion Notes

### Per-Task Checklist
执行每个T001-T028测试task时,确认:
- [ ] 测试函数名遵循`test_<tool>_<scenario>`命名
- [ ] Docstring清晰说明测试目的(参考checklist.md描述)
- [ ] 使用现有fixtures(tmp_path, monkeypatch, caplog)
- [ ] 断言覆盖输出schema所有必需字段
- [ ] 测试执行<100ms(使用小测试文件)

### Bug修复流程
如测试失败(发现现有实现bug):
1. 保持测试代码不变(测试预期正确)
2. 修复`context_mcp/tools/`中的实现代码
3. 重新运行测试验证Green phase
4. 记录bug修复在commit message

---

## Validation Checklist (T029执行前)
*GATE: 检查所有测试task完成*

- [ ] T001-T010: 导航工具10个测试已添加
- [ ] T011-T021: 搜索工具11个测试已添加
- [ ] T022-T028: 读取工具8个测试已添加(包括1个Low priority)
- [ ] 所有测试函数已实现(无TODO/SKIP标记)
- [ ] pytest执行无语法错误

---

## Success Metrics
- ✅ 29个新增测试全部通过
- ✅ 覆盖率保持≥99%
- ✅ 参数覆盖率达到100%
- ✅ 无ruff linting警告
- ✅ Quickstart验证全部通过

---

## Estimated Time
- **High Priority (T001-T004, T011-T015, T022-T024)**: 14 × 10min = 2.3 hours
- **Medium Priority (T005-T010, T016-T021, T025-T027)**: 14 × 8min = 1.9 hours
- **Low Priority (T028)**: 1 × 15min = 0.25 hours
- **Validation (T029-T031)**: 3 × 10min = 0.5 hours
- **Total**: ~5 hours

---

*Generated from contracts/test-coverage-checklist.md - 2025-10-05*
