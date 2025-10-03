## 1\. 概述

### 1.1. 原始需求

我现在想做一个mcp，功能是可以将任何项目通过mcp接入到context中，核心原来是采用claude code的方式，mcp提供list\_files，read\_files等能力，然后对指定项目进行执行，这样就可以让agent通过mcp阅读其他项目。

### 1.2. 核心设计原则

-   **轻量级与通用性**: 完全基于标准 Unix 系统命令 (`ls`, `find`, `rg`, `cat`, `sed`, `tail`) 实现，无需安装特定语言的解析器或复杂的运行时环境。
    
-   **原子化能力**: 每个 MCP API 都是单一、明确的原子操作，便于 LLM Agent 组合和推理。
    
-   **性能优先**: 优先选用 `ripgrep (rg)` 等高性能工具，确保在大型项目中的响应速度。
    
-   **安全边界**: 当前版本聚焦于**只读操作**，规避了代码执行和文件写入带来的安全风险。
    
-   **实用主义**: 功能设计源于真实开发场景，解决开发者日常痛点。
    

## 2\. 核心能力

MCP 的能力分为三大类：**导航 (Navigation)**、**搜索 (Search)** 和**读取 (Read)**。

### 2.1. 导航 (Navigation)

导航能力帮助 Agent 建立对项目宏观结构的认知。

| API 名称 | 参数  | 功能描述 | 实现命令 |
| --- | --- | --- | --- |
| `list_directory` | `path: string`,<br>`sort_by: "size"\|"name"\|"time" = "name"`,<br>`order: "asc"\|"desc" = "asc"`,<br>`limit: int = -1` | 列出目录内容，支持按文件大小、名称或修改时间排序，并可限制返回结果数量。 | `ls -la --block-size=1 <path> \| sort -k<col> -n<order_flag> \| head -n <limit>` |
| `show_tree` | `path: string`,<br>`max_depth: int` | 以树状结构展示项目的目录层级，便于快速概览。 | `tree -L <max_depth> <path>` |

### 2.2. 搜索 (Search)

搜索能力是 MCP 的核心，它允许 Agent 根据语义、文件名或时间属性进行精准定位。

| API 名称 | 参数  | 功能描述 | 实现命令 |
| --- | --- | --- | --- |
| `search_in_file` | `query: string`,<br>`file_path: string`,<br>`use_regex: bool = False` | 在单个文件中搜索指定文本或正则表达式模式。 | `rg -n --heading --color=never -e "<query>" <file_path>` |
| `search_in_files` | `query: string`,<br>`file_pattern: string`,<br>`path: string`,<br>`use_regex: bool = False`,<br>`exclude_query: string = ""` | 在指定目录下，递归搜索所有匹配文件名模式的文件内容。支持正则表达式和结果排除（“包含A但不包含B”）。 | `rg -n --glob "<file_pattern>" --heading --color=never -e "<query>" <path> \| rg -v "<exclude_query>"` |
| `find_files_by_name` | `name_pattern: string`,<br>`path: string` | 根据文件名模式（支持通配符）查找文件。 | `find <path> -name "<name_pattern>"` |
| `find_recently_modified_files` | `path: string`,<br>`file_pattern: string`,<br>`hours_ago: int` | 查找在过去 N 小时内被修改过的、且匹配指定文件名模式的文件。 | `find <path> -name "<file_pattern>" -mmin -<minutes> -type f` |

### 2.3. 读取 (Read)

读取能力提供对文件内容的精细化获取，避免不必要的全量加载。

| API 名称 | 参数  | 功能描述 | 实现命令 |
| --- | --- | --- | --- |
| `read_entire_file` | `file_path: string` | 读取整个文件的全部内容。 | `cat <file_path>` |
| `read_file_lines` | `file_path: string`,<br>`start_line: int`,<br>`end_line: int` | 读取文件中指定行号范围内的内容。 | `sed -n '<start_line>,<end_line>p' <file_path>` |
| `read_file_tail` | `file_path: string`,<br>`num_lines: int` | 读取文件末尾的 N 行内容（对日志文件非常有用）。 | `tail -n <num_lines> <file_path>` |
| `read_files` | `file_paths: string[]` | 批量读取多个文件的全部内容。 | `cat <file1> <file2> ...` |

## 3\. 技术选型

mcp框架：https://github.com/jlowin/fastmcp

python打包方式：uvx

## 4\. 应用场景

MCP 能力的组合可以解决多种复杂场景：

-   **快速上手新项目**: `show_tree` + `find_files_by_name("main.*")` + `read_entire_file`。
    
-   **精准配置审计**: `find_files_by_name("*.yml")` + `search_in_file("password", ...)`。
    
-   **安全密钥扫描**: `search_in_files("AKIA[0-9A-Z]{16}", use_regex=True, ...)`。
    
-   **故障排查**: `find_recently_modified_files(..., hours_ago=1)` + `read_file_tail("error.log", 50)`。
    
-   **代码影响分析**: `search_in_files("old_function_name", ...)` 以找到所有调用点。