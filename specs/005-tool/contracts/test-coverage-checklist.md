# Test Coverage Checklist

**Feature**: 005-tool | **Generated**: 2025-10-05

本文档列出所有需补充的测试用例,按工具分类,优先级标注。

---

## 导航工具 (Navigation Tools)

### list_directory
- [x] **[High]** test_limit_zero - 验证limit=0返回空列表但total正确
- [x] **[High]** test_limit_one - 验证limit=1返回单个条目
- [x] **[Medium]** test_sort_by_size_order_desc - 按大小降序排列
- [x] **[Medium]** test_sort_by_size_order_asc - 按大小升序排列
- [x] **[Medium]** test_sort_by_time_order_desc - 按时间降序排列
- [x] **[Medium]** test_sort_by_time_order_asc - 按时间升序排列
- [x] **[Medium]** test_sort_by_name_order_desc - 按名称降序排列(补充验证)
- [x] **[Medium]** test_sort_by_name_order_asc - 按名称升序排列(补充验证)

**File**: `tests/contract/test_navigation_contract.py`

### show_tree
- [x] **[High]** test_max_depth_zero_rejected - 验证max_depth=0抛出异常
- [x] **[High]** test_max_depth_eleven_rejected - 验证max_depth=11抛出异常

**File**: `tests/contract/test_navigation_contract.py`

### read_project_context
✅ **[Complete]** - 已有8个场景测试,覆盖完整

---

## 搜索工具 (Search Tools)

### search_in_file
- [x] **[High]** test_use_regex_true - 验证正则模式搜索
- [x] **[Medium]** test_query_with_regex_special_chars_literal - 验证正则元字符在literal模式转义

**File**: `tests/contract/test_search_contract.py`

### search_in_files
- [x] **[High]** test_file_pattern_specific - 验证file_pattern="*.py"筛选
- [x] **[High]** test_use_regex_and_exclude_query - 验证use_regex=True + exclude_query组合
- [x] **[Medium]** test_timeout_large_value - 验证timeout=3600(大值)不导致异常
- [x] **[Medium]** test_path_subdirectory - 验证path="subdir"仅搜索子目录

**File**: `tests/contract/test_search_contract.py`

### find_files_by_name
- [x] **[High]** test_complex_glob_pattern - 验证"test_*.py"复杂通配符
- [x] **[Medium]** test_path_subdirectory - 验证path="context_mcp"仅查找该目录

**File**: `tests/contract/test_search_contract.py`

### find_recently_modified_files
- [x] **[High]** test_file_pattern_filter - 验证file_pattern="*.md"筛选
- [x] **[Medium]** test_hours_ago_large - 验证hours_ago=720(30天)
- [x] **[Medium]** test_path_subdirectory - 验证path="specs"仅查找该目录

**File**: `tests/contract/test_search_contract.py`

---

## 读取工具 (Read Tools)

### read_entire_file
✅ **[Complete]** - 单参数工具,已覆盖

### read_file_lines
- [x] **[High]** test_single_line_read - 验证start_line=end_line读取单行
- [x] **[High]** test_end_line_exceeds_total - 验证end_line>文件总行数自动截断
- [x] **[Medium]** test_read_entire_file_via_lines - 验证start_line=1, end_line=total_lines

**File**: `tests/contract/test_read_contract.py`

### read_file_tail
- [x] **[High]** test_num_lines_exceeds_total - 验证num_lines>文件总行数返回全文
- [x] **[Medium]** test_num_lines_equals_total - 验证num_lines=文件总行数边界

**File**: `tests/contract/test_read_contract.py`

### read_files
- [x] **[Medium]** test_empty_array_rejected - 验证file_paths=[]违反minItems约束
- [x] **[Low]** test_large_batch - 验证100个文件批量读取(性能)

**File**: `tests/contract/test_read_contract.py`

---

## Summary Statistics

| Priority | Count | Percentage |
|----------|-------|------------|
| High     | 14    | 48%        |
| Medium   | 14    | 48%        |
| Low      | 1     | 4%         |
| **Total** | **29** | **100%** |

**Files to Modify**:
- `tests/contract/test_navigation_contract.py` (10 tests)
- `tests/contract/test_search_contract.py` (11 tests)
- `tests/contract/test_read_contract.py` (8 tests)

**Estimated Effort**:
- High priority: 14 tests × 10min = 2.3 hours
- Medium priority: 14 tests × 8min = 1.9 hours
- Low priority: 1 test × 15min = 0.25 hours
- **Total**: ~4.5 hours

---

## Acceptance Criteria

### Definition of Done (per test)
1. ✅ 测试函数名遵循`test_<tool>_<scenario>`命名
2. ✅ Docstring清晰说明测试目的
3. ✅ 使用现有fixtures(tmp_path, monkeypatch)
4. ✅ 断言覆盖输出schema所有必需字段
5. ✅ 测试执行<100ms

### Suite-Level Acceptance
1. ✅ 所有High priority测试通过
2. ✅ pytest coverage不低于99%
3. ✅ 无ruff linting警告
4. ✅ CI通过(Windows + Linux)

---

## Usage

### For Implementation
```bash
# 按文件执行
pytest tests/contract/test_navigation_contract.py -v
pytest tests/contract/test_search_contract.py -v
pytest tests/contract/test_read_contract.py -v

# 按优先级执行(使用pytest标记)
pytest -m high_priority
```

### For Progress Tracking
勾选每个测试前的复选框,提交时更新此文档。
