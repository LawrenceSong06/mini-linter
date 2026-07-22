# 项目上下文

`mini-linter` 是一个紧凑的 Python CLI linter，面向 Agent 驱动的代码仓库。

## 仓库结构

- `AGENTS.md`：Codex 和其它 LLM Agent 的根入口指南。
- `.agents/`：协作模板和更详细的 Agent 文档。
- `mini_linter/`：运行时代码包。
- `mini_linter/rules/`：内置 lint 规则。
- `tests/`：pytest 测试套件。
- `pyproject.toml`：包元数据、测试配置和 mini-linter 示例配置。

## 核心概念

- `Violation` 表示一条检查结果，必须包含 `severity`、`message` 和 `hint`。
- `RuleContext` 是传给每条规则的输入，包含项目路径、文件文本、可用时的 AST、配置和完整文件列表。
- 规则是一个类，包含 `id`、`default_severity` 和 `check(context)`。
- Lang JSON 文件按 rule id 提供规则最终输出的 `severity`、`message` 和 `hint`；缺失时检查会失败。
- CLI 输出 JSON，Agent 不需要解析终端文本就能读取结果。

## 实现分层

- `mini_linter.config` 负责解析 `pyproject.toml`。
- `mini_linter.lang` 负责加载和渲染 lang 文案。
- `mini_linter.plugins` 负责加载可信本地插件。
- `mini_linter.core` 负责文件发现、AST 解析、规则执行和结果聚合。
- `mini_linter.cli` 负责参数解析、JSON 输出和退出码。

## 初版非目标

- 不做自动修复。
- 不解析非 Python 语言。
- 不为本地插件代码做沙箱隔离。
- 不做 rich terminal UI。
- 除 Python <3.11 的 `tomli` TOML parser fallback 外，不引入其它运行时依赖。
