# Contract: ToolDetector

**Module**: `context_mcp.utils.tool_detector`
**Type**: Internal API (非MCP工具)
**Version**: 1.0

## 职责

检测系统中高性能CLI工具(ripgrep/fd)的可用性,并缓存检测结果供MCP工具函数使用。

---

## API契约

### 类: ToolDetector

**单例模式**: 同一进程中多次实例化返回相同对象

#### 属性

| 属性名 | 类型 | 只读 | 描述 |
|--------|------|------|------|
| `has_ripgrep` | bool | ✅ | ripgrep是否可用 |
| `has_fd` | bool | ✅ | fd是否可用 |

#### 方法

##### `__init__() -> ToolDetector`

**行为**:
1. 检测ripgrep可用性: `shutil.which("rg")` + 执行`rg --version`验证
2. 检测fd可用性: `shutil.which("fd")` + 执行`fd --version`验证
3. 缓存检测结果到`has_*`属性
4. 单例模式: 后续调用返回已缓存实例

**性能**: <100ms

**异常**: 不抛出异常,检测失败时对应`has_*`属性为False

---

## 行为契约

### 前置条件

- 无(可在任何时候实例化)

### 后置条件

1. `has_ripgrep`和`has_fd`属性必须为布尔值
2. 属性值在实例生命周期内不变
3. 如果`has_ripgrep=True`,则系统中必须有可执行的`rg`命令
4. 如果`has_fd=True`,则系统中必须有可执行的`fd`命令

### 不变量

1. **单例性**: `ToolDetector() is ToolDetector()` 必须为True
2. **状态稳定性**: 一旦初始化,`has_*`属性值永不改变
3. **一致性**: 如果`has_ripgrep=True`,执行`subprocess.run(["rg", "--version"])`不会抛出FileNotFoundError

---

## 使用示例

### 正常流程

```python
from context_mcp.utils.tool_detector import ToolDetector

# 获取检测器实例(首次调用会执行检测)
detector = ToolDetector()

# 检查工具可用性
if detector.has_ripgrep:
    print("ripgrep可用,使用高性能搜索")
    result = subprocess.run(["rg", "pattern", "path"])
else:
    print("ripgrep不可用,使用降级方案")
    # 降级到grep或Python
```

### 单例验证

```python
detector1 = ToolDetector()
detector2 = ToolDetector()

assert detector1 is detector2  # 必须是同一实例
assert detector1.has_ripgrep == detector2.has_ripgrep  # 状态一致
```

---

## 测试契约

### 单元测试要求

1. **检测正确性测试**:
   - Mock `shutil.which()`返回路径,验证`has_*=True`
   - Mock `shutil.which()`返回None,验证`has_*=False`

2. **版本验证测试**:
   - Mock `subprocess.run()`返回成功,验证`has_*=True`
   - Mock `subprocess.run()`抛出异常,验证`has_*=False`

3. **单例模式测试**:
   - 多次实例化,验证`id(detector1) == id(detector2)`

4. **性能测试**:
   - 验证初始化耗时<100ms

### 测试数据

```python
# 测试用例: ripgrep可用
mock_which.return_value = "/usr/bin/rg"
mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
# 期望: detector.has_ripgrep == True

# 测试用例: ripgrep不可用(未安装)
mock_which.return_value = None
# 期望: detector.has_ripgrep == False

# 测试用例: ripgrep存在但无法执行
mock_which.return_value = "/usr/bin/rg"
mock_run.side_effect = FileNotFoundError
# 期望: detector.has_ripgrep == False
```

---

## 错误处理

### 异常策略

**原则**: 检测失败不抛出异常,静默降级

| 错误场景 | 处理方式 |
|---------|---------|
| `shutil.which()`返回None | 设置`has_*=False` |
| `subprocess.run()`抛出FileNotFoundError | 捕获异常,设置`has_*=False` |
| `subprocess.run()`超时 | 捕获TimeoutExpired,设置`has_*=False` |
| `subprocess.run()`返回非0退出码 | 设置`has_*=False` |

**理由**: 工具检测失败不应导致MCP服务启动失败,应降级到标准工具

---

## 性能要求

| 指标 | 目标 |
|------|------|
| 单个工具检测耗时 | <50ms |
| 总初始化耗时 | <100ms |
| 内存开销 | <1KB (仅存储2个bool值) |

---

## 依赖关系

### 外部依赖

- `shutil` (Python标准库)
- `subprocess` (Python标准库)

### 被依赖

- `context_mcp.tools.search` (search_in_files, find_files_by_name)
- `context_mcp.server` (启动时日志记录)

---

**Version**: 1.0 | **Last Updated**: 2025-10-04
