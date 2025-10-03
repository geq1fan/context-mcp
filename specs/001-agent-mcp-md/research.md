# Research & Technical Decisions

**Feature**: MCP 项目上下文集成服务
**Date**: 2025-10-03

## 研究目标

基于技术上下文中的选型,研究最佳实践和实现模式:
1. FastMCP框架使用模式
2. Unix命令封装最佳实践
3. MCP工具函数设计规范
4. 路径安全验证策略
5. 二进制文件检测方法
6. 测试策略(契约、集成、单元)

---

## 决策记录

### 1. FastMCP框架使用

**决策**: 使用fastmcp的装饰器模式定义MCP工具函数

**理由**:
- fastmcp提供`@mcp.tool()`装饰器,简化工具注册
- 自动处理MCP协议序列化/反序列化
- 支持类型提示和参数验证
- 符合MCP标准规范

**替代方案**:
- 手动实现MCP协议 - 被拒绝,重复造轮子
- 使用其他MCP框架(如modelcontextprotocol官方SDK) - fastmcp更轻量,适合Python生态

**示例模式**:
```python
from fastmcp import FastMCP

mcp = FastMCP("agent-mcp")

@mcp.tool()
def list_directory(path: str, sort_by: str = "name", order: str = "asc", limit: int = -1):
    """列出目录内容"""
    # 实现逻辑
    pass
```

---

### 2. Unix命令封装

**决策**: 使用`subprocess.run()`封装Unix命令,设置超时和错误处理

**理由**:
- Python标准库支持,无额外依赖
- 支持超时控制(需求FR-024: 默认60秒)
- 可捕获stdout/stderr分别处理
- 跨平台兼容性(通过条件判断适配Windows)

**替代方案**:
- 使用`os.popen()` - 被拒绝,无超时控制
- 使用第三方库(如sh) - 被拒绝,增加依赖

**实现模式**:
```python
import subprocess

def _run_command(cmd: list[str], timeout: int = 60) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout}s")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e.stderr}")
```

---

### 3. 路径安全验证

**决策**: 使用`pathlib.Path.resolve()`规范化路径,然后检查是否在配置的根目录内

**理由**:
- `resolve()`自动处理符号链接和相对路径
- 可防止`../`等目录遍历攻击(需求FR-020)
- Python标准库,无额外依赖

**实现策略**:
```python
from pathlib import Path

class PathValidator:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()

    def validate(self, path: str) -> Path:
        target = Path(path).resolve()
        if not target.is_relative_to(self.root):
            raise SecurityError(f"Path outside root: {path}")
        return target
```

---

### 4. 二进制文件检测

**决策**: 读取文件前1024字节,检查是否包含NULL字节(`\x00`)

**理由**:
- NULL字节在文本文件中罕见,在二进制文件中常见
- 快速检测,无需读取完整文件
- 符合需求FR-018a(返回错误而非尝试读取)

**替代方案**:
- 使用`python-magic`库 - 被拒绝,增加C依赖
- 仅基于文件扩展名 - 被拒绝,不可靠

**实现**:
```python
def is_binary_file(path: Path) -> bool:
    with open(path, 'rb') as f:
        chunk = f.read(1024)
        return b'\x00' in chunk
```

---

### 5. 环境变量配置

**决策**: 使用`PROJECT_ROOT`环境变量指定项目根目录

**理由**:
- 符合需求FR-026(环境变量配置)
- 12-factor app原则
- 便于不同环境切换

**配置管理**:
```python
import os
from pathlib import Path

class Config:
    PROJECT_ROOT: Path = Path(os.getenv("PROJECT_ROOT", ".")).resolve()
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "60"))
    LOG_RETENTION_DAYS: int = 7
```

---

### 6. 日志策略

**决策**: 使用Python标准`logging`模块,配置`TimedRotatingFileHandler`

**理由**:
- 需求FR-025要求7天保留期
- 标准库支持,无额外依赖
- 支持自动日志轮转和清理

**配置**:
```python
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    handler = TimedRotatingFileHandler(
        'agent_mcp.log',
        when='D',
        interval=1,
        backupCount=7
    )
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

---

### 7. MCP响应格式

**决策**: 使用fastmcp自动生成的MCP标准响应格式

**理由**:
- 需求FR-028要求遵循MCP标准
- fastmcp框架自动处理序列化
- 确保与MCP客户端兼容性

**响应结构**:
- 成功: `{"content": [...]}` 包含结果数据
- 错误: `{"error": {"code": str, "message": str}}`

---

### 8. 测试策略

**决策**: 三层测试金字塔

**契约测试** (tests/contract/):
- 测试每个MCP工具的输入/输出契约
- 验证参数类型、必填项、返回格式
- 使用pytest参数化测试不同场景

**集成测试** (tests/integration/):
- 测试完整工作流(配置→调用→验证)
- 测试边界情况(需求Edge Cases)
- 使用临时目录和mock数据

**单元测试** (tests/unit/):
- 测试路径验证逻辑
- 测试二进制文件检测
- 测试配置加载

**工具选择**:
- pytest作为测试框架
- pytest-timeout用于超时测试
- pytest-mock用于mock subprocess调用

---

### 9. 打包与分发

**决策**: 使用uv作为包管理和打包工具

**理由**:
- 原始需求文档指定uvx打包方式
- uv是现代Python包管理工具,速度快
- 支持`uvx`直接运行,无需安装

**配置** (pyproject.toml):
```toml
[project]
name = "agent-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=0.1.0",
]

[project.scripts]
agent-mcp = "agent_mcp.server:main"
```

---

### 10. ripgrep (rg) 集成

**决策**: 优先使用ripgrep(rg),回退到grep

**理由**:
- rg性能优异(需求FR-023: 大型项目支持)
- 支持正则表达式(需求FR-007)
- 支持glob模式过滤(需求FR-009)
- 提供grep回退保证兼容性

**检测逻辑**:
```python
import shutil

def get_search_cmd() -> str:
    return 'rg' if shutil.which('rg') else 'grep'
```

---

## 技术风险与缓解

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| ripgrep未安装 | 搜索功能不可用 | 提供grep回退,文档说明安装步骤 |
| 跨平台命令差异 | Windows兼容性问题 | 使用subprocess统一接口,条件适配 |
| 大文件读取OOM | 内存溢出 | 实现流式读取,限制单次读取大小 |
| 符号链接循环 | 无限递归 | Path.resolve()自动处理,设置深度限制 |

---

## 待Phase 1验证的设计假设

1. **MCP协议兼容性**: fastmcp生成的响应格式是否满足所有MCP客户端?
2. **超时粒度**: 60秒超时是否需要按操作类型细化(列表vs搜索)?
3. **并发安全**: 多Agent并发访问时是否需要文件锁?(当前假设只读安全)
4. **日志大小**: 7天日志是否需要大小限制避免磁盘满?

---

## 研究完成状态

- [x] 所有技术选型有明确理由
- [x] 无NEEDS CLARIFICATION遗留项
- [x] 关键实现模式已验证
- [x] 风险已识别并有缓解方案
- [x] 准备进入Phase 1设计阶段
