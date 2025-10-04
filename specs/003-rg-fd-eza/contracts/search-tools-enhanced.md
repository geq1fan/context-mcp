# Contract: Enhanced Search Tools

**Module**: `context_mcp.tools.search`
**Type**: MCP工具增强
**Version**: 2.0 (从1.0升级)

## 变更摘要

在现有`search_in_files`和`find_files_by_name`基础上,添加高性能工具优先和降级策略,保持MCP工具接口不变。

---

## 工具1: search_in_files (增强)

### MCP接口 (不变)

**输入参数**:
| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `query` | string | ✅ | - | 搜索文本或正则表达式 |
| `file_pattern` | string | ❌ | "*" | 文件名glob模式 |
| `path` | string | ❌ | "." | 起始目录(相对PROJECT_ROOT) |
| `use_regex` | boolean | ❌ | false | 是否使用正则表达式 |
| `exclude_query` | string | ❌ | "" | 排除包含此模式的匹配 |
| `timeout` | integer | ❌ | 60 | 超时秒数 |

**输出格式** (不变):
```json
{
  "matches": [
    {
      "file_path": "src/server.py",
      "line_number": 42,
      "line_content": "def search_in_files(query, ...):"
    }
  ],
  "total_matches": 1,
  "files_searched": 10,
  "timed_out": false
}
```

### 增强行为契约

#### 工具选择策略

```
1. 检查 ToolDetector.has_ripgrep
   ├─ True → 使用ripgrep (当前实现已存在)
   └─ False → 继续
2. 检查 shutil.which("grep")
   ├─ True → 使用grep + find组合
   └─ False → 使用Python rglob (当前降级实现)
```

#### ripgrep命令构建 (已实现,无变更)

```bash
rg --line-number --no-heading \
   [--regexp|--fixed-strings] \
   [--glob <file_pattern>] \
   <query> <path>
```

#### grep命令构建 (新增)

```bash
# Step 1: 使用find查找匹配文件
find <path> -type f -name '<file_pattern>'

# Step 2: 对每个文件执行grep
grep -n [-E|-F] <query> <file>
```

**参数映射**:
| search_in_files参数 | grep参数 |
|---------------------|----------|
| `use_regex=True` | `-E` (扩展正则) |
| `use_regex=False` | `-F` (固定字符串) |
| `query` | 最后一个参数 |

#### Python rglob降级 (已实现,无变更)

当grep也不可用时,使用当前实现:
```python
for file in abs_path.rglob(file_pattern):
    result = search_in_file(query, file, use_regex)
    # 合并结果
```

### 性能契约

| 工具 | 中型项目耗时目标 | 小型项目耗时目标 |
|------|------------------|------------------|
| ripgrep | <200ms | <50ms |
| grep | <3000ms | <400ms |
| Python rglob | <5000ms | <800ms |

---

## 工具2: find_files_by_name (增强)

### MCP接口 (不变)

**输入参数**:
| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `name_pattern` | string | ✅ | - | 文件名模式(支持通配符) |
| `path` | string | ❌ | "." | 起始目录 |

**输出格式** (不变):
```json
{
  "files": [
    "src/server.py",
    "tests/test_server.py"
  ],
  "total_found": 2
}
```

### 增强行为契约

#### 工具选择策略

```
1. 检查 ToolDetector.has_fd
   ├─ True → 使用fd
   └─ False → 继续
2. 检查 shutil.which("find")
   ├─ True → 使用find
   └─ False → 使用Python rglob (当前实现)
```

#### fd命令构建 (新增)

```bash
fd --type f <name_pattern> <path>
```

**参数处理**:
- `name_pattern`中的通配符`*`和`?`直接传递给fd
- fd默认支持.gitignore过滤,无需额外参数

#### find命令构建 (新增)

```bash
find <path> -type f -name '<name_pattern>'
```

**跨平台注意**:
- Unix/Linux/macOS: 使用`find`
- Windows: `find`不可用,直接降级到Python rglob

#### Python rglob降级 (已实现,无变更)

```python
for file in abs_path.rglob(name_pattern):
    if file.is_file():
        files.append(str(file.relative_to(config.root_path)))
```

### 性能契约

| 工具 | 中型项目耗时目标 | 小型项目耗时目标 |
|------|------------------|------------------|
| fd | <100ms | <20ms |
| find | <500ms | <100ms |
| Python rglob | <800ms | <150ms |

---

## 通用契约

### 输出格式一致性

**要求**: 无论使用哪个工具,输出JSON格式必须完全一致

**验证方法**:
```python
# 对相同输入,不同工具的输出必须等价
result_rg = search_in_files("test", tool="rg")
result_grep = search_in_files("test", tool="grep")
result_py = search_in_files("test", tool="python")

assert result_rg["total_matches"] == result_grep["total_matches"] == result_py["total_matches"]
assert sorted(result_rg["matches"]) == sorted(result_grep["matches"]) == sorted(result_py["matches"])
```

### 路径格式规范

1. 所有`file_path`必须是相对路径(相对PROJECT_ROOT)
2. 使用正斜杠`/`作为路径分隔符(包括Windows)
3. 示例: `"src/server.py"`, `"tests/unit/test_search.py"`

### 超时处理

1. ripgrep/grep/fd命令必须设置`timeout`参数
2. 超时时,设置`timed_out=true`,返回已收集的部分结果
3. Python降级实现使用`time.time()`手动检查超时

### 错误处理

| 错误场景 | 行为 |
|---------|------|
| 工具执行失败(非0退出码) | 降级到下一层工具 |
| 工具不存在(FileNotFoundError) | 降级到下一层工具 |
| 超时 | 返回部分结果,`timed_out=true` |
| 路径不存在 | 抛出`FileNotFoundError` (保持现有行为) |
| 二进制文件 | 跳过该文件(ripgrep/grep默认行为,Python需检测) |

---

## 测试契约

### 集成测试要求

1. **工具降级测试**:
   - Mock `ToolDetector.has_ripgrep=False`,验证降级到grep
   - Mock `ToolDetector.has_fd=False`,验证降级到find
   - Mock所有工具不可用,验证降级到Python

2. **输出一致性测试**:
   - 在有ripgrep/fd的环境执行测试
   - 记录输出结果
   - Mock工具不可用,重新执行
   - 验证输出结果一致(匹配数量、文件路径)

3. **性能回归测试**:
   - 验证ripgrep/fd路径耗时满足性能契约
   - 验证grep/find路径耗时不超过3倍ripgrep/fd
   - 验证Python降级路径耗时不超过5倍ripgrep/fd

### 单元测试要求

1. **命令构建测试**:
   - 验证ripgrep命令参数正确
   - 验证grep命令参数正确
   - 验证fd/find命令参数正确

2. **输出解析测试**:
   - 测试ripgrep输出解析(已有)
   - 测试grep输出解析(新增)
   - 测试fd/find输出解析(新增)

---

## 向后兼容性

**保证**: 100%向后兼容

1. MCP工具接口不变(输入参数、输出格式)
2. 现有调用代码无需修改
3. 在没有ripgrep/fd的环境,行为与v1.0完全一致(使用Python降级)

---

## 性能回归保护

### 基准

- 当前v1.0在ripgrep可用时的性能作为基准
- v2.0在ripgrep可用时性能不得低于v1.0

### 监控

- 在CI中运行性能测试,记录各工具路径耗时
- 如果任一路径耗时增加>10%,测试失败

---

**Version**: 2.0 | **Last Updated**: 2025-10-04
**Breaking Changes**: None (向后兼容)
