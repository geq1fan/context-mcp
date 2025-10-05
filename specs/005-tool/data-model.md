# Data Model: 测试用例覆盖完整性增强

**Feature**: 005-tool | **Date**: 2025-10-05

## Overview
本feature为测试增强,不涉及新数据实体。此文档定义测试覆盖清单的数据结构,用于追踪测试补充进度。

---

## Entity: TestCoverageItem

### Purpose
追踪单个测试缺口的补充状态

### Fields
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| tool_name | str | 工具函数名称 | Enum: 11个工具名 |
| parameter | str | 参数名称 | 对应工具函数签名 |
| scenario | str | 测试场景描述 | 简短描述(如"limit=0边界值") |
| priority | str | 优先级 | Enum: High/Medium/Low |
| status | str | 补充状态 | Enum: Pending/Completed |
| test_file | str | 测试文件路径 | 相对于tests/contract/ |
| test_function | str | 测试函数名 | pytest命名规范(test_xxx) |

### Example
```python
TestCoverageItem(
    tool_name="list_directory",
    parameter="limit",
    scenario="limit=0边界值测试",
    priority="High",
    status="Pending",
    test_file="test_navigation_contract.py",
    test_function="test_list_directory_limit_zero"
)
```

---

## Entity: ToolParameterSpec

### Purpose
定义工具函数的参数规格,用于生成测试覆盖清单

### Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| tool_name | str | 工具函数名称 | "list_directory" |
| parameter_name | str | 参数名 | "sort_by" |
| parameter_type | str | 参数类型 | "Literal['name', 'size', 'time']" |
| default_value | Any | 默认值(如有) | "name" |
| constraints | dict | 约束条件 | {"enum": ["name", "size", "time"]} |
| is_required | bool | 是否必需 | False |

### Derived Properties
- `boundary_values`: 从constraints推导的边界测试值
  - min/max约束 → [min-1, min, max, max+1]
  - enum约束 → 所有枚举值
- `test_scenarios`: 需补充的测试场景列表

---

## Relationships

```
ToolParameterSpec (11 tools × avg 4 params = ~44 specs)
    ↓ generates
TestCoverageItem (40-50 items)
    ↓ groups by
test_file (3 files: test_navigation/search/read_contract.py)
```

---

## State Transitions

### TestCoverageItem.status
```
Pending → Completed
  ↑          ↓
  └── Reverted (if test removed)
```

**Triggers**:
- `Pending → Completed`: 测试函数已实现且通过
- `Completed → Reverted`: 测试被重构或删除(罕见)

---

## Validation Rules

### ToolParameterSpec
1. **Constraint Consistency**: 如果parameter_type包含Literal,constraints.enum必须匹配
2. **Default Value Type**: default_value类型必须符合parameter_type
3. **Required Parameters**: is_required=True时,default_value必须为None

### TestCoverageItem
1. **Unique Test Function**: 同一test_file内test_function不可重复
2. **Valid Tool Reference**: tool_name必须在11个已知工具中
3. **Priority Alignment**: High priority项应优先完成(status=Completed)

---

## Coverage Metrics

### Target Metrics
- **Parameter Coverage**: 每个参数至少1个专门测试
  - Formula: `covered_params / total_params >= 100%`
- **Enum Coverage**: 所有枚举值都被测试
  - Formula: `tested_enum_values / total_enum_values = 100%`
- **Boundary Coverage**: 所有约束边界都被测试
  - Formula: `tested_boundaries / total_boundaries >= 90%`

### Current vs Target
| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Parameter Coverage | ~60% | 100% | +40个测试 |
| Enum Coverage | ~50% | 100% | +6个sort_by×order组合 |
| Boundary Coverage | ~70% | 90% | +10个边界测试 |

---

## Non-Functional Data Constraints

### Test Execution Time
- **Per Test**: <100ms (使用小测试文件,避免真实文件IO)
- **Per Test Class**: <1s (3-5个测试/类)
- **Full Contract Suite**: <10s (现有+新增共100+测试)

### Test Data Files
- 测试使用临时文件(pytest tmp_path fixture)
- 无持久化测试数据文件需求
- Mock PROJECT_ROOT环境变量

---

## Conclusion

数据模型极简,仅定义测试覆盖追踪实体。真实测试数据由pytest fixtures动态生成,无需持久化存储。
