# Quickstart: 性能优化工具集成与降级策略

**Feature**: 003-rg-fd-eza | **Date**: 2025-10-04

## 目标

验证高性能工具(ripgrep/fd)集成和降级策略的功能正确性,确保在各种环境下MCP服务都能正常工作。

---

## 前置条件

1. **Python环境**: Python 3.11+
2. **项目依赖**: 已安装 fastmcp, chardet, pytest
3. **测试数据**: 使用项目本身作为测试数据集

---

## 快速验证步骤

### Step 1: 验证ToolDetector工具检测

```bash
# 运行单元测试
pytest tests/unit/test_tool_detector.py -v

# 预期输出:
# test_tool_detector.py::test_detector_singleton PASSED
# test_tool_detector.py::test_ripgrep_detection PASSED
# test_tool_detector.py::test_fd_detection PASSED
# test_tool_detector.py::test_detection_performance PASSED
```

**验证点**:
- ✅ ToolDetector单例模式正常工作
- ✅ 正确检测ripgrep/fd可用性
- ✅ 检测性能<100ms

---

### Step 2: 验证搜索工具降级逻辑

```bash
# 测试ripgrep优先使用
pytest tests/integration/test_tool_fallback.py::test_search_with_ripgrep -v

# 测试grep降级
pytest tests/integration/test_tool_fallback.py::test_search_fallback_to_grep -v

# 测试Python降级
pytest tests/integration/test_tool_fallback.py::test_search_fallback_to_python -v
```

**验证点**:
- ✅ ripgrep可用时优先使用
- ✅ ripgrep不可用时降级到grep
- ✅ grep不可用时降级到Python rglob
- ✅ 输出格式在所有降级层保持一致

---

### Step 3: 验证文件查找工具降级逻辑

```bash
# 测试fd优先使用
pytest tests/integration/test_tool_fallback.py::test_find_with_fd -v

# 测试find降级
pytest tests/integration/test_tool_fallback.py::test_find_fallback_to_find -v

# 测试Python降级
pytest tests/integration/test_tool_fallback.py::test_find_fallback_to_python -v
```

**验证点**:
- ✅ fd可用时优先使用
- ✅ fd不可用时降级到find
- ✅ find不可用时降级到Python rglob
- ✅ 输出格式在所有降级层保持一致

---

### Step 4: 验证跨平台兼容性

```bash
# Windows平台
pytest tests/integration/test_tool_fallback.py::test_windows_fallback -v

# Linux/macOS平台
pytest tests/integration/test_tool_fallback.py::test_unix_fallback -v
```

**验证点**:
- ✅ Windows环境下正确降级到Python
- ✅ Unix环境下正确使用系统工具

---

### Step 5: 验证启动日志输出

```bash
# 模拟ripgrep不可用环境启动服务
RG_UNAVAILABLE=1 python -m context_mcp.server

# 预期日志输出:
# WARN: ripgrep不可用,search_in_files将降级使用grep或Python实现。建议安装ripgrep: https://github.com/BurntSushi/ripgrep#installation

# 模拟fd不可用环境启动服务
FD_UNAVAILABLE=1 python -m context_mcp.server

# 预期日志输出:
# WARN: fd不可用,find_files_by_name将降级使用find或Python实现。建议安装fd: https://github.com/sharkdp/fd#installation
```

**验证点**:
- ✅ 启动时检测工具可用性
- ✅ 工具不可用时记录WARN日志(仅一次)
- ✅ 日志包含降级信息和安装指引链接

---

### Step 6: 验证MCP契约不变

```bash
# 运行现有的契约测试
pytest tests/contract/test_search_contract.py -v

# 预期: 所有测试PASS,无论使用哪个工具
```

**验证点**:
- ✅ search_in_files返回格式符合MCP契约
- ✅ find_files_by_name返回格式符合MCP契约
- ✅ 降级不影响MCP工具的对外接口

---

## 手动测试场景

### 场景1: ripgrep高性能搜索

```bash
# 确保ripgrep已安装
rg --version  # 验证ripgrep可用

# 启动MCP服务
uvx --from context-mcp context-mcp

# 在MCP客户端执行搜索
{
  "tool": "search_in_files",
  "arguments": {
    "query": "ToolDetector",
    "path": ".",
    "use_regex": false
  }
}

# 预期: 快速返回所有包含"ToolDetector"的文件和行
```

### 场景2: fd高性能文件查找

```bash
# 确保fd已安装
fd --version  # 验证fd可用

# 在MCP客户端执行文件查找
{
  "tool": "find_files_by_name",
  "arguments": {
    "name_pattern": "*.py",
    "path": "context_mcp"
  }
}

# 预期: 快速返回所有Python文件列表
```

### 场景3: 降级到标准工具

```bash
# 卸载ripgrep (或重命名可执行文件)
# 重启MCP服务

# 执行相同搜索
{
  "tool": "search_in_files",
  "arguments": {
    "query": "ToolDetector",
    "path": ".",
    "use_regex": false
  }
}

# 预期:
# 1. 启动时看到WARN日志: "ripgrep不可用,search_in_files将降级..."
# 2. 搜索仍然成功,但速度较慢
# 3. 返回格式与ripgrep版本完全一致
```

---

## 性能基准验证

### 小型项目性能测试

```bash
# 运行性能基准测试
python scripts/benchmark.py --project-size small

# 预期输出示例:
# === 小型项目性能基准 (<1000文件) ===
# search_in_files:
#   - ripgrep: 45ms
#   - grep: 320ms
#   - python: 580ms
#   - 加速比: 7.1x (ripgrep vs grep)
#
# find_files_by_name:
#   - fd: 12ms
#   - find: 85ms
#   - python: 120ms
#   - 加速比: 7.1x (fd vs find)
```

### 中型项目性能测试

```bash
# 克隆中型项目(如React)
git clone https://github.com/facebook/react.git /tmp/react-test

# 运行性能基准测试
python scripts/benchmark.py --project-path /tmp/react-test --project-size medium

# 预期输出示例:
# === 中型项目性能基准 (1000-10000文件) ===
# search_in_files:
#   - ripgrep: 180ms
#   - grep: 2400ms
#   - python: 4200ms
#   - 加速比: 13.3x (ripgrep vs grep)
```

---

## 故障排查

### 问题: ToolDetector检测不到已安装的ripgrep

**检查步骤**:
1. 确认ripgrep在PATH中: `which rg` (Unix) 或 `where rg` (Windows)
2. 手动执行版本检查: `rg --version`
3. 检查Python subprocess权限: `python -c "import subprocess; print(subprocess.run(['rg', '--version']))"`

**解决方案**:
- 将ripgrep路径添加到系统PATH
- 重启MCP服务

---

### 问题: 降级到grep但性能仍然很差

**检查步骤**:
1. 确认grep可用: `grep --version`
2. 查看日志确认使用的工具: `grep "tool_used" server.log`

**解决方案**:
- 如果降级到Python: 安装ripgrep或grep
- 如果使用grep: 这是预期行为(grep比ripgrep慢10-20倍)

---

### 问题: Windows环境下find命令失败

**检查步骤**:
1. 确认是否在Git Bash环境: `echo $SHELL`
2. 检查find命令可用性: `find . -name "*.py" | head -5`

**解决方案**:
- Windows CMD下会自动降级到Python rglob
- 推荐使用Git Bash或WSL环境以获得更好性能

---

## 成功标准

所有快速验证步骤通过,且满足以下条件:

- ✅ **功能完整性**: 搜索和查找功能在所有降级层都正常工作
- ✅ **性能提升**: ripgrep比grep快7-13倍,fd比find快7-9倍
- ✅ **降级透明**: 输出格式在所有工具间保持一致
- ✅ **日志完整**: 启动时正确记录工具检测结果
- ✅ **跨平台兼容**: Windows/Linux/macOS都能正常工作
- ✅ **契约遵守**: MCP工具接口不变,现有客户端无需修改

---

## 下一步

完成quickstart验证后:

1. ✅ 在README.md中添加性能对比章节
2. ✅ 添加工具安装指引(Windows/Linux/macOS)
3. ✅ 更新CHANGELOG.md记录新特性
4. ✅ 创建PR并在CI中运行完整测试套件

---

**Version**: 1.0 | **Status**: Ready for Testing
