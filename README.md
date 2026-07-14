# mini-linter

一个面向 Agent 驱动项目的轻量 Python linter。

`mini-linter` 用于检查 Python 代码风格、import 依赖、架构边界和 Agent 协作文件。项目刻意保持小而清晰：运行时代码优先使用 Python 标准库，Python <3.11 使用 `tomli` 作为 TOML 解析兼容依赖，测试使用 `pytest`。

## 安装

在项目根目录执行：

```powershell
pip install .
```

也可以直接安装项目所需依赖：

```powershell
pip install -r requirements.txt
```

如果需要运行测试：

```powershell
pip install ".[test]"
```

开发时也可以使用 editable install：

```powershell
pip install -e ".[test]"
```

安装后会提供 `mini-linter` 命令。

## 快速使用

```powershell
mini-linter check .
```

默认输出为 JSON，方便 Codex 和其它 LLM Agent 直接解析检查结果。

## 命令参数

`mini-linter` 当前提供 `check` 子命令：

```powershell
mini-linter check [paths...] [--config PATH] [--lang PATH] [--format json] [--fail-on error|warning|info]
```

查看顶层帮助：

```powershell
mini-linter -h
```

查看 `check` 子命令帮助：

```powershell
mini-linter check -h
```

参数说明：

- `paths...`：要检查的文件或目录；不传时使用配置文件中的 `paths`。
- `--config PATH`：指定 `pyproject.toml` 配置文件路径；不传时从当前目录查找 `pyproject.toml`。
- `--lang PATH`：指定 lang JSON 文件，用于提供 violation 的 `message` 和 `hint`。
- `--format json`：输出格式；当前只支持 `json`。
- `--fail-on error|warning|info`：设置失败阈值；例如 `warning` 表示 warning 和 error 都会让命令返回失败码。

退出码：

- `0`：检查通过。
- `1`：发现达到 `fail_on` 阈值的 violation。
- `2`：命令用法错误。

## 使用示例

检查当前目录：

```powershell
mini-linter check .
```

检查指定目录：

```powershell
mini-linter check mini_linter tests
```

使用指定配置文件：

```powershell
mini-linter check --config pyproject.toml
```

使用自定义 lang 文案：

```powershell
mini-linter check . --lang lang/zh_cn.json
```

把 warning 也作为失败条件：

```powershell
mini-linter check . --fail-on warning
```

## 配置示例

在 `pyproject.toml` 中添加：

```toml
[tool.mini_linter]
paths = ["mini_linter", "tests"]
exclude = [".git", "__pycache__", ".pytest_cache", "build", "dist"]
lang = "lang/zh_cn.json"
plugins = []
fail_on = "error"

[tool.mini_linter.rules."style.file_too_long"]
enabled = true
max_lines = 300

[tool.mini_linter.rules."style.function_too_long"]
enabled = true
max_lines = 50

[tool.mini_linter.rules."imports.forbidden"]
enabled = true
modules = ["requests"]
```

## Lang JSON 示例

Lang 文件必须按 rule id 提供 violation 文案：

```json
{
  "style.file_too_long": {
    "message": "文件共有 {line_count} 行，超过限制 {max_lines} 行。",
    "hint": "将该文件拆分为职责更清晰的小模块。"
  }
}
```

每个最终输出的 violation 都会包含来自 lang JSON 的 `message` 和 `hint`。如果某条规则缺少对应 lang 文案，检查会失败。

## 设计重点

- CLI 优先，适合 Agent 自动调用。
- 支持通过 `pyproject.toml` 配置规则。
- 支持本地 Python 插件规则。
- 强制使用 lang JSON 提供 violation 的 `message` 和 `hint`。
- 每个功能和内置规则都有对应 unit test。

## 更多文档

- [插件规则编写指南](docs/plugins.md)
