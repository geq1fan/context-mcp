# Data Model: 性能优化工具集成与降级策略

**Feature**: 003-rg-fd-eza | **Date**: 2025-10-04

## 概览

本特性主要涉及工具检测状态管理和命令参数映射,无需复杂数据模型。核心实体是工具检测器(ToolDetector)及其状态。

---

## 核心实体

### 1. ToolDetector (工具检测器)

**职责**: 检测系统中高性能CLI工具的可用性,缓存检测结果

**字段**:
| 字段名 | 类型 | 描述 | 验证规则 |
|--------|------|------|----------|
| `has_ripgrep` | bool | ripgrep是否可用 | 只读,启动时检测 |
| `has_fd` | bool | fd是否可用 | 只读,启动时检测 |
| `_ripgrep_path` | str \| None | ripgrep可执行文件路径 | 私有,通过shutil.which()获取 |
| `_fd_path` | str \| None | fd可执行文件路径 | 私有,通过shutil.which()获取 |

**状态转换**:
```
[未初始化] --init()--> [已检测]
                         ↓
                   (状态不再变化)
```

**不变量**:
- 检测结果在进程生命周期内不变 (单例模式)
- `has_*`属性必须反映实际工具可用性

**示例**:
```python
detector = ToolDetector()
# 启动时检测
assert isinstance(detector.has_ripgrep, bool)
assert isinstance(detector.has_fd, bool)

# 使用示例
if detector.has_ripgrep:
    use_ripgrep_command()
else:
    fallback_to_grep()
```

---

### 2. CommandMapper (命令参数映射器)

**职责**: 提供高性能工具到标准工具的参数映射

**类型**: 静态映射字典,无需实例化

**映射表结构**:
```python
# ripgrep -> grep 参数映射
RG_TO_GREP_PARAMS = {
    "--line-number": "-n",
    "--ignore-case": "-i",
    "--fixed-strings": "-F",
    "--regexp": "-E",
    # --glob 无直接等价,需在外层处理文件过滤
}

# fd -> find 参数映射
FD_TO_FIND_PARAMS = {
    "-e": "--name",  # 扩展名过滤
    "-i": "-iname",   # 忽略大小写
    "-t f": "-type f",  # 只查找文件
}
```

**使用方式**:
```python
# 构建grep命令时引用映射表
grep_args = [RG_TO_GREP_PARAMS.get(arg, arg) for arg in rg_args]
```

---

### 3. SearchResult (搜索结果) - 现有实体,无需修改

**描述**: `search_in_files`返回的结果结构

**字段**:
| 字段名 | 类型 | 描述 |
|--------|------|------|
| `matches` | list[dict] | 匹配结果列表,每项包含file_path/line_number/line_content |
| `total_matches` | int | 总匹配数 |
| `files_searched` | int | 搜索的文件数 (仅Python降级时填充) |
| `timed_out` | bool | 是否超时 |

**约束**: 无论使用ripgrep/grep/Python,返回格式必须一致 (FR-004要求)

---

### 4. FileListResult (文件列表结果) - 现有实体,无需修改

**描述**: `find_files_by_name`返回的结果结构

**字段**:
| 字段名 | 类型 | 描述 |
|--------|------|------|
| `files` | list[str] | 文件路径列表(相对PROJECT_ROOT) |
| `total_found` | int | 找到的文件总数 |

**约束**: 无论使用fd/find/Python,返回格式必须一致

---

## 数据流

### 工具检测流程

```
[应用启动]
    ↓
[ToolDetector初始化]
    ↓
[并行检测ripgrep/fd] (shutil.which + --version验证)
    ↓
[缓存检测结果到has_*属性]
    ↓
[记录WARN日志] (如果工具不可用)
    ↓
[ToolDetector单例可用于所有工具函数]
```

### 搜索工具选择流程

```
[search_in_files调用]
    ↓
[检查detector.has_ripgrep]
    ├─ True → [构建rg命令] → [执行subprocess] → [解析输出]
    └─ False → [检查grep可用性]
                ├─ True → [构建grep命令 + find过滤] → [执行subprocess] → [解析输出]
                └─ False → [Python rglob降级] → [逐文件search_in_file]
    ↓
[统一返回SearchResult格式]
```

### 文件查找工具选择流程

```
[find_files_by_name调用]
    ↓
[检查detector.has_fd]
    ├─ True → [构建fd命令] → [执行subprocess] → [解析输出]
    └─ False → [检查find可用性]
                ├─ True → [构建find命令] → [执行subprocess] → [解析输出]
                └─ False → [Python rglob降级]
    ↓
[统一返回FileListResult格式]
```

---

## 关系图

```
┌─────────────────┐
│  ToolDetector   │ (单例)
│  - has_ripgrep  │
│  - has_fd       │
└────────┬────────┘
         │ 被引用
         ↓
┌─────────────────────────────┐
│   search.py 工具函数        │
│  - search_in_files()        │
│  - find_files_by_name()     │
└─────────────────────────────┘
         │ 调用
         ↓
┌─────────────────────────────┐
│  subprocess.run()           │
│  执行 rg/grep/fd/find       │
└─────────────────────────────┘
         │ 返回
         ↓
┌─────────────────────────────┐
│  输出解析逻辑                │
│  (已存在于search.py)        │
└─────────────────────────────┘
         │ 生成
         ↓
┌─────────────────────────────┐
│  SearchResult/FileListResult│
│  (MCP工具返回格式)          │
└─────────────────────────────┘
```

---

## 验证规则

### ToolDetector验证

1. **初始化后状态稳定**: `has_*`属性值在初始化后不再改变
2. **路径有效性**: 如果`has_ripgrep=True`,则`_ripgrep_path`必须是有效可执行文件路径
3. **单例保证**: 多次获取ToolDetector必须返回同一实例

### 输出格式一致性验证

1. **SearchResult一致性**: 使用ripgrep/grep/Python实现时,返回的dict结构必须完全相同
2. **路径格式统一**: 所有file_path必须使用正斜杠`/`,相对于PROJECT_ROOT
3. **行号一致性**: line_number必须从1开始(与编辑器行号一致)

### 降级逻辑验证

1. **功能等价性**: 降级后的搜索结果必须与高性能工具结果一致(相同查询返回相同匹配)
2. **超时保护**: 所有subprocess调用必须设置timeout参数
3. **异常处理**: 工具执行失败时必须降级到下一层,不得抛出异常给MCP客户端

---

## 性能特性

### 检测性能

- ToolDetector初始化: <100ms (仅在启动时执行一次)
- 单个工具检测: <50ms (`shutil.which()` + `subprocess.run(["tool", "--version"])`)

### 缓存策略

- **检测结果缓存**: 永久缓存(单例模式),无需过期
- **无需缓存**: 搜索结果不缓存(MCP工具是无状态的)

### 降级性能影响

| 操作 | ripgrep | grep | Python rglob | 性能损失 |
|------|---------|------|--------------|----------|
| search_in_files (中型项目) | 180ms | 2400ms | 4200ms | 13x → 23x |
| find_files_by_name (中型项目) | 50ms | 450ms | 680ms | 9x → 13.6x |

**优化策略**: 优先使用性能最优的工具,降级仅在工具不可用时触发

---

## 扩展性考虑

### 未来可能扩展

1. **动态工具切换**: 支持运行时切换工具(当前设计不支持,需要改造)
2. **工具版本管理**: 支持多版本ripgrep/fd并选择最优版本(当前仅检测可用性)
3. **更多工具集成**: ag(The Silver Searcher), ugrep等

### 扩展点

- ToolDetector可扩展为支持更多工具检测(如`has_ag`, `has_ugrep`)
- CommandMapper可扩展新的参数映射表
- 工具选择逻辑可提取为策略模式(当前是简单if-else)

---

**Version**: 1.0 | **Status**: Complete
