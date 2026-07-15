# mini-linter 用户文档

`mini-linter` 是一个轻量级 Python CLI linter，适合用于 Agent 驱动的代码仓库。它关注 Python 代码风格、import 依赖、架构边界和 Agent 协作文件，并默认输出 JSON，方便 Codex 或其它 LLM Agent 直接读取检查结果。

## 适用场景

`mini-linter` 适合以下场景：

- 希望用统一规则检查 Python 项目结构。
- 希望让 CI 或 Agent 自动读取 lint 结果。
- 希望限制某些 import 依赖，避免模块边界变乱。
- 希望用 `AGENTS.md` 和 `.agents/` 模板维护 Agent 协作上下文。
- 希望通过本地插件添加项目专属规则。

当前版本不提供自动修复，不解析非 Python 语言，也不会对本地插件代码做沙箱隔离。

## 环境要求

- Python 3.7 或更高版本。
- Python 3.11 以下版本会自动使用 `tomli` 作为 TOML 解析兼容依赖。
- 测试依赖为 `pytest` 和 `pytest-cov`。

## 安装

建议在项目根目录使用虚拟环境安装。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

如果需要运行测试或参与开发，可以安装测试依赖：

```powershell
pip install ".[test]"
```

开发时可以使用 editable install：

```powershell
pip install -e ".[test]"
```

安装完成后，命令行中会提供 `mini-linter` 命令。

## 快速开始

检查当前目录：

```powershell
mini-linter check .
```

检查多个目录：

```powershell
mini-linter check mini_linter tests
```

使用指定配置文件：

```powershell
mini-linter check --config pyproject.toml
```

使用指定 lang 文案文件：

```powershell
mini-linter check . --lang mini_linter/lang/zh_cn.json
```

将 warning 和 error 都作为失败条件：

```powershell
mini-linter check . --fail-on warning
```

## 命令格式

`mini-linter` 当前提供 `check` 子命令：

```powershell
mini-linter check [paths...] [--config PATH] [--lang PATH] [--format json] [--fail-on error|warning|info]
```

参数说明：

- `paths...`：要检查的文件或目录。不传时使用配置文件中的 `paths`。
- `--config PATH`：指定 `pyproject.toml` 配置文件路径。不传时从当前目录查找 `pyproject.toml`。
- `--lang PATH`：指定 lang JSON 文件，用于提供 violation 的 `message` 和 `hint`。
- `--format json`：输出格式。当前只支持 `json`。
- `--fail-on error|warning|info`：设置失败阈值。

退出码：

- `0`：检查通过。
- `1`：发现达到 `fail_on` 阈值的 violation。
- `2`：命令用法错误。

## 配置文件

在 `pyproject.toml` 中添加 `[tool.mini_linter]` 配置：

```toml
[tool.mini_linter]
paths = ["mini_linter", "tests"]
exclude = [".git", "__pycache__", ".pytest_cache", "build", "dist", ".venv"]
lang = "zh_cn.json"
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

[tool.mini_linter.rules."architecture.layers"]
enabled = true

[[tool.mini_linter.architecture.layers]]
name = "core"
paths = ["mini_linter/*.py"]
may_import = ["rules"]

[[tool.mini_linter.architecture.layers]]
name = "rules"
paths = ["mini_linter/rules/*.py"]
may_import = ["core"]
```

常用字段：

- `paths`：默认检查路径。
- `exclude`：文件发现时跳过的目录或文件名。
- `lang`：默认 lang JSON 文案文件。
- `plugins`：可信本地插件文件列表。
- `fail_on`：默认失败阈值，可以是 `error`、`warning` 或 `info`。
- `rules`：按 rule id 配置规则开关和参数。
- `architecture.layers`：配置项目内模块层级和允许依赖关系。

## JSON 输出

`mini-linter` 默认输出 JSON。顶层结构包含 `ok`、`summary` 和 `violations`。

示例：

```json
{
  "ok": false,
  "summary": {
    "error": 1,
    "warning": 0,
    "info": 0,
    "total": 1
  },
  "violations": [
    {
      "rule_id": "imports.forbidden",
      "severity": "error",
      "location": "mini_linter/example.py:1:1",
      "message": "禁止 import `requests`。",
      "hint": "移除该依赖，或将相关能力移动到允许依赖该模块的边界层中。",
      "details": {
        "module": "requests"
      }
    }
  ]
}
```

每条 violation 都包含：

- `rule_id`：触发的规则 id。
- `severity`：严重级别，可能是 `error`、`warning` 或 `info`。
- `location`：文件路径和位置。
- `message`：面向用户的检查说明。
- `hint`：修复建议。
- `details`：规则提供的结构化细节。

## Lang JSON 文案

Lang 文件用于为每条规则提供最终展示的 `message` 和 `hint`。如果启用的规则缺少对应文案，检查会失败。

示例：

```json
{
  "style.file_too_long": {
    "message": "文件共有 {line_count} 行，超过限制 {max_lines} 行。",
    "hint": "将该文件拆分为职责更清晰的小模块。"
  }
}
```

文案中的占位符来自规则的 `details`。例如 `line_count`、`max_lines`、`module` 等字段会在输出前被渲染到 `message` 或 `hint` 中。

## 内置规则

| Rule id | 默认级别 | 作用 |
| --- | --- | --- |
| `style.file_too_long` | `warning` | 检查 Python 文件是否超过 `max_lines`。 |
| `style.function_too_long` | `warning` | 检查函数或异步函数是否超过 `max_lines`。 |
| `style.test_file_naming` | `info` | 检查 `tests` 目录下测试文件是否符合命名约定。 |
| `imports.forbidden` | `error` | 检查是否 import 了被禁止的模块。 |
| `architecture.layers` | `error` | 检查项目内 import 是否违反层级边界。 |
| `agent.agents_guide_exists` | `error` | 检查项目根目录是否存在 `AGENTS.md`。 |
| `agent.templates_exist` | `error` | 检查 `.agents/` 下必需模板是否存在。 |

## 插件规则

可以通过 `plugins` 配置加载可信本地 Python 文件中的自定义规则。

```toml
[tool.mini_linter]
plugins = ["tools/lint_rules.py"]
```

插件文件中的规则应提供 `id` 和 `check(context)`，并建议继承 `mini_linter.rules.base.BaseRule`。插件规则也必须在 lang JSON 中提供对应的 `message` 和 `hint`。

更多插件写法请阅读 [插件规则编写指南](plugins.md)。

## 在 CI 中使用

CI 中通常直接运行：

```powershell
mini-linter check . --fail-on error
```

如果希望 warning 也阻塞合并，可以使用：

```powershell
mini-linter check . --fail-on warning
```

由于输出是 JSON，CI 或 Agent 可以直接解析 `summary.total`、`ok` 和 `violations`，再把结果展示到评论、报告或后续自动修复流程中。

## 运行测试

安装测试依赖后，在项目根目录运行：

```powershell
python -m pytest
```

项目默认集成 coverage，当前配置等价于：

```powershell
python -m pytest --cov=mini_linter --cov-report=term-missing
```

## 常见问题

### 为什么输出只有 JSON？

项目优先支持 Agent 和自动化流程。JSON 输出稳定、结构化，便于程序读取和后续处理。

### 为什么每条 violation 都必须有 message 和 hint？

`message` 用于说明发现了什么问题，`hint` 用于说明下一步怎么处理。这样无论结果展示给人还是交给 Agent，都能保留足够的上下文。

### 可以自动修复代码吗？

当前版本不实现自动修复。`mini-linter` 只负责发现问题并给出结构化提示。

### 插件安全吗？

插件是可信本地 Python 代码，加载时会被执行。不要加载来源不明或不可信的插件文件。
