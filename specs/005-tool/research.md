# Research: 测试用例覆盖完整性增强

**Feature**: 005-tool | **Date**: 2025-10-05

## Research Scope
本feature为纯测试增强,无新技术选型或架构决策。Research聚焦现有测试实践分析和覆盖缺口确认。

---

## 1. 当前测试现状分析

### Decision
保持现有pytest + contract/integration/unit三层测试架构,无需引入新框架。

### Rationale
- 现有测试覆盖率99.2%,基础设施成熟
- pytest fixtures机制足以支持参数化测试
- contract测试已有完整JSON Schema验证基础

### Alternatives Considered
- **pytest-parametrize扩展使用**: 考虑用`@pytest.mark.parametrize`减少代码重复
  - **Decision**: 有限使用,仅对真正重复的参数组合(如sort_by×order)
  - **Rejected**: 过度参数化会降低测试可读性,违反Simplicity原则

---

## 2. 测试覆盖缺口详细分析

### 2.1 导航工具(3个)

#### `list_directory`
**已覆盖**:
- 默认参数调用
- sort_by="name"/"size"/"time"各1个用例
- order="asc"/"desc"各1个用例
- limit=-1(无限制)
- 安全性:路径遍历、不存在目录

**缺口**:
- ❌ limit=0(边界值) - spec.md:122
- ❌ limit=1(最小有效limit)
- ❌ sort_by×order组合:缺6种(size+desc, size+asc, time+desc, time+asc, name+desc的完整验证)

#### `show_tree`
**已覆盖**:
- 默认max_depth=3
- max_depth=1(最小值)
- max_depth=10(最大值)
- 递归结构验证

**缺口**:
- ❌ max_depth=2~9中间值(非关键,可省略)
- ❌ max_depth=0(无效值,应拒绝) - 当前测试未验证
- ❌ max_depth=11(超出范围,应拒绝)

#### `read_project_context`
**已覆盖**: 全部8种场景(两文件存在/单文件存在/都不存在/空文件/权限错误/编码错误/大文件)
**缺口**: ✅ 无

### 2.2 搜索工具(4个)

#### `search_in_file`
**已覆盖**:
- query+file_path(必需参数)
- use_regex=False(默认值)
- 安全性:路径遍历、文件不存在

**缺口**:
- ❌ use_regex=True的正则模式搜索
- ❌ 特殊字符查询(如正则元字符在literal模式下)

#### `search_in_files`
**已覆盖**:
- 仅query必需参数调用(使用所有默认值)
- timeout最小值=1
- 安全性测试

**缺口**:
- ❌ file_pattern非"*"(如"*.py") - spec.md:127
- ❌ use_regex=True + exclude_query组合 - spec.md:128
- ❌ timeout边界行为(大值如3600)
- ❌ path参数指定子目录

#### `find_files_by_name`
**已覆盖**:
- name_pattern必需参数(多种扩展名)
- path默认值
- 安全性测试

**缺口**:
- ❌ 复杂glob模式(如"test_*.py")
- ❌ path参数指定非根目录

#### `find_recently_modified_files`
**已覆盖**:
- hours_ago必需参数(24小时)
- hours_ago最小值=1
- 默认path和file_pattern

**缺口**:
- ❌ file_pattern非"*"筛选 - spec.md:140
- ❌ hours_ago大值(如720=30天)
- ❌ path参数指定子目录

### 2.3 读取工具(4个)

#### `read_entire_file`
**已覆盖**:
- file_path必需参数
- 安全性:路径遍历、文件不存在

**缺口**: ✅ 无(单参数工具)

#### `read_file_lines`
**已覆盖**:
- 三个必需参数(file_path, start_line, end_line)
- start_line/end_line最小值=1
- 安全性测试

**缺口**:
- ❌ start_line=end_line(单行读取) - spec.md:132
- ❌ end_line超出文件总行数 - spec.md:133
- ❌ start_line=1, end_line=文件总行数(读全文边界)

#### `read_file_tail`
**已覆盖**:
- file_path必需参数
- num_lines默认值=10
- num_lines最小值=1

**缺口**:
- ❌ num_lines大于文件总行数 - spec.md:136
- ❌ num_lines=文件总行数(边界)

#### `read_files`
**已覆盖**:
- file_paths数组(成功/失败混合)
- 最小数组长度=1
- 批量操作一致性

**缺口**:
- ❌ 空数组(违反minItems=1约束,应测试拒绝)
- ❌ 大批量(如100个文件)性能特征

---

## 3. 测试设计模式选择

### Decision
采用"一测试一目的"模式,避免过度参数化。

### Rationale
遵循Constitution IV (Simplicity):
- 每个测试函数测试一个明确场景
- docstring清晰说明测试意图
- 失败时易于定位问题

### Pattern
```python
def test_list_directory_limit_zero():
    """Test that limit=0 returns empty list but correct total count."""
    result = list_directory(path=".", limit=0)
    assert result["entries"] == []
    assert result["total"] > 0  # Actual dir has files
    assert result["truncated"] is True
```

### Alternatives Considered
- **参数化测试表**: 所有sort_by×order组合放一个测试
  - **Rejected**: 9个组合失败时难以定位具体哪种组合有问题
- **Property-based testing (Hypothesis)**: 生成随机参数组合
  - **Rejected**: 增加复杂度,测试结果不可重复,违反Simplicity原则

---

## 4. 测试优先级

### High Priority (必须补充)
1. **边界值**: limit=0/1, max_depth边界, hours_ago大值
2. **参数组合**: use_regex+exclude_query, file_pattern+path
3. **单行场景**: start_line=end_line

### Medium Priority (建议补充)
1. sort_by×order完整组合(当前缺6种)
2. num_lines>total_lines行为验证
3. 复杂glob模式(test_*.py)

### Low Priority (可选)
1. 大批量操作性能测试(100+ files)
2. max_depth中间值(2~9)
3. 超大timeout值(3600s)

---

## 5. 潜在风险点

### Risk 1: 现有实现bug
**Scenario**: 补充测试后发现`limit=0`未正确处理
**Mitigation**:
- 遵循TDD: 测试失败→修复代码→测试通过
- 在tasks.md中为每个bug修复创建独立任务

### Risk 2: 测试执行时间增长
**Scenario**: 40-50个新测试导致CI时间显著增加
**Mitigation**:
- 每个测试保持<100ms(使用小测试文件)
- 避免真实文件系统操作的重复setup
- 复用现有fixtures(tmp_path, monkeypatch)

### Risk 3: 跨平台兼容性
**Scenario**: 路径分隔符在Windows/Unix差异导致测试失败
**Mitigation**:
- 使用`pathlib.Path`替代字符串拼接
- 现有测试已通过跨平台CI,复用相同模式

---

## Research Conclusion

✅ **All Technical Context fields confirmed** - 无NEEDS CLARIFICATION残留

**Key Findings**:
1. 现有测试架构成熟,无需新工具
2. 识别出40-50个具体测试缺口(按工具分类)
3. 采用简单测试模式,避免过度抽象
4. 测试优先级明确,可渐进补充

**Ready for Phase 1**: 设计测试覆盖清单(contracts/)和quickstart验证流程
