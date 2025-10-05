# Quickstart: 测试用例覆盖完整性增强

**Feature**: 005-tool | **Date**: 2025-10-05

本quickstart验证测试补充工作是否完成,通过执行测试套件和覆盖率检查确认成功。

---

## Prerequisites

### System Requirements
- Python 3.11+
- pytest installed (`uv pip install pytest`)
- 现有context-mcp项目环境

### Environment Setup
```bash
# 1. 确保在项目根目录
cd context-mcp

# 2. 设置PROJECT_ROOT环境变量
export PROJECT_ROOT=$(pwd)  # Linux/Mac
set PROJECT_ROOT=%CD%       # Windows cmd
$env:PROJECT_ROOT = (Get-Location).Path  # Windows PowerShell

# 3. 安装依赖(如未安装)
uv pip install -e .
```

---

## Step 1: 验证基线测试通过

**Purpose**: 确认现有测试正常,避免新增测试掩盖已有失败

```bash
# 运行现有contract测试
pytest tests/contract/ -v

# 预期输出:
# ✅ All existing tests PASS
# ✅ No failures or errors
```

**Success Criteria**:
- 所有测试绿色通过
- 无warnings或errors

---

## Step 2: 运行新增测试(按优先级)

### Step 2.1: High Priority Tests
```bash
# 导航工具高优先级测试
pytest tests/contract/test_navigation_contract.py::TestListDirectoryContract::test_limit_zero -v
pytest tests/contract/test_navigation_contract.py::TestListDirectoryContract::test_limit_one -v
pytest tests/contract/test_navigation_contract.py::TestShowTreeContract::test_max_depth_zero_rejected -v
pytest tests/contract/test_navigation_contract.py::TestShowTreeContract::test_max_depth_eleven_rejected -v

# 搜索工具高优先级测试
pytest tests/contract/test_search_contract.py::TestSearchInFileContract::test_use_regex_true -v
pytest tests/contract/test_search_contract.py::TestSearchInFilesContract::test_file_pattern_specific -v
pytest tests/contract/test_search_contract.py::TestSearchInFilesContract::test_use_regex_and_exclude_query -v
pytest tests/contract/test_search_contract.py::TestFindFilesByNameContract::test_complex_glob_pattern -v
pytest tests/contract/test_search_contract.py::TestFindRecentlyModifiedFilesContract::test_file_pattern_filter -v

# 读取工具高优先级测试
pytest tests/contract/test_read_contract.py::TestReadFileLinesContract::test_single_line_read -v
pytest tests/contract/test_read_contract.py::TestReadFileLinesContract::test_end_line_exceeds_total -v
pytest tests/contract/test_read_contract.py::TestReadFileTailContract::test_num_lines_exceeds_total -v
```

**Success Criteria**:
- 所有14个High priority测试通过
- 每个测试执行时间<100ms

### Step 2.2: Medium + Low Priority Tests
```bash
# 运行所有新增测试
pytest tests/contract/ -v --tb=short

# 或按文件运行
pytest tests/contract/test_navigation_contract.py -v
pytest tests/contract/test_search_contract.py -v
pytest tests/contract/test_read_contract.py -v
```

**Success Criteria**:
- 全部29个新增测试通过
- 无意外失败

---

## Step 3: 验证测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/contract/ --cov=context_mcp.tools --cov-report=term-missing

# 预期输出示例:
# context_mcp/tools/navigation.py    100%
# context_mcp/tools/search.py        99%
# context_mcp/tools/read.py          100%
# -------------------------------
# TOTAL                              99%+
```

**Success Criteria**:
- 总体覆盖率保持≥99%
- 无新的未覆盖行(uncovered lines)

---

## Step 4: 参数覆盖验证

**Manual Check**: 根据`contracts/test-coverage-checklist.md`验证

```bash
# 1. 打开checklist文件
cat specs/005-tool/contracts/test-coverage-checklist.md

# 2. 确认所有复选框已勾选
# 3. 确认29个测试都有对应实现
```

**Automated Validation** (可选):
```bash
# 使用grep统计测试函数数量
grep -r "def test_" tests/contract/test_navigation_contract.py | wc -l  # 应为18(10个新增+8个已有)
grep -r "def test_" tests/contract/test_search_contract.py | wc -l     # 应为27(11个新增+16个已有)
grep -r "def test_" tests/contract/test_read_contract.py | wc -l       # 应为32(8个新增+24个已有)
```

**Success Criteria**:
- 每个工具参数都有专门测试
- 所有枚举值都被测试
- 所有边界值都有验证

---

## Step 5: 集成验证(完整测试套件)

```bash
# 运行三层测试(contract + integration + unit)
pytest tests/ -v --tb=short

# 检查是否引入回归
pytest tests/integration/ -v
pytest tests/unit/ -v
```

**Success Criteria**:
- Contract层: 所有测试通过
- Integration层: 无回归(已有测试保持绿色)
- Unit层: 无回归

---

## Step 6: 代码质量检查

```bash
# Ruff格式检查
ruff format --check tests/contract/

# Ruff linting
ruff check tests/contract/

# 类型检查(如启用mypy)
mypy tests/contract/ --strict
```

**Success Criteria**:
- 无格式错误
- 无linting warnings
- 无类型错误

---

## Step 7: CI模拟(跨平台验证)

**Linux/Mac**:
```bash
# 在Unix-like系统运行
pytest tests/contract/ -v --tb=short
```

**Windows**:
```powershell
# 在Windows系统运行
pytest tests/contract/ -v --tb=short
```

**Success Criteria**:
- 两个平台测试结果一致
- 无平台特定失败

---

## Troubleshooting

### Issue 1: 测试失败 - "limit=0 returns non-empty list"
**Cause**: `list_directory`实现未正确处理limit=0
**Fix**:
1. 检查`context_mcp/tools/navigation.py:88-92`
2. 确认`if limit > 0`逻辑包含`limit == 0`分支
3. 修复后重新运行测试

### Issue 2: 测试超时 - "search_in_files timeout"
**Cause**: 测试使用真实大文件导致搜索慢
**Fix**:
1. 使用`tmp_path` fixture创建小测试文件(<100 lines)
2. 设置timeout=1仅验证参数接受性,不验证实际搜索

### Issue 3: 覆盖率下降
**Cause**: 新增测试未正确调用所有代码路径
**Fix**:
1. 运行`pytest --cov-report=html`生成HTML报告
2. 检查未覆盖行
3. 补充缺失的断言或边界场景

---

## Validation Checklist

执行前勾选每个步骤:

- [ ] Step 1: 基线测试通过
- [ ] Step 2.1: High priority测试通过(14个)
- [ ] Step 2.2: Medium/Low priority测试通过(15个)
- [ ] Step 3: 覆盖率≥99%
- [ ] Step 4: 参数覆盖100%
- [ ] Step 5: 无回归(integration + unit)
- [ ] Step 6: 代码质量检查通过
- [ ] Step 7: 跨平台验证通过

---

## Expected Outcomes

### Quantitative Metrics
- ✅ 新增测试用例数: 29个
- ✅ 测试覆盖率: 99%+
- ✅ 参数覆盖率: 100%
- ✅ 测试执行时间: <10s (全contract suite)

### Qualitative Outcomes
- ✅ 每个参数都有清晰测试文档(docstring)
- ✅ 边界值测试防止未来回归
- ✅ 参数组合测试验证交互行为
- ✅ 新开发者可通过测试理解参数用法

---

## Next Steps (Post-Validation)

1. **Commit Changes**:
   ```bash
   git add tests/contract/
   git add specs/005-tool/
   git commit -m "test: add comprehensive parameter coverage for 11 MCP tools"
   ```

2. **Update Coverage Badge** (如有):
   更新README.md中的coverage badge链接

3. **Document Coverage** (可选):
   在项目根目录README.md添加"Test Coverage"章节说明100%参数覆盖

---

## Success Declaration

当所有7个步骤的Success Criteria都满足时,本feature验证完成。

**Final Validation Command**:
```bash
pytest tests/contract/ -v --cov=context_mcp.tools --cov-report=term && \
echo "✅ Feature 005-tool: 测试用例覆盖完整性增强 - VALIDATED"
```
