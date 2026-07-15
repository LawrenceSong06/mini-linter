# Agent 指南

本仓库包含 `mini-linter`：一个小型 Python linter，面向使用 Codex 或其它 LLM Agent 进行开发的项目。

## 项目目标

构建一个聚焦的 CLI 工具，用于检查 Python 项目的代码风格、import 依赖、架构边界和 Agent 协作问题。实现必须保持小而明确，方便后续 Agent 阅读和修改。

## 开发原则

- 运行时代码优先使用 Python 标准库；`tomli` 仅作为 Python <3.11 的 TOML 兼容依赖。
- 模块职责要窄，命名要直接。
- 每个功能和每条内置规则都必须有 unit test。
- 保持面向 Agent 的 JSON-first 输出契约。
- 每个 violation 必须同时包含 `message` 和 `hint`。
- 新规则必须在 lang JSON 中提供 `message` 和 `hint` 文案，并包含对应测试。

## 代码风格

- 公共函数和 dataclass 字段需要类型标注。
- 函数保持短小，副作用要明显。
- 避免隐式全局状态。
- 显式传递配置和上下文。
- 优先使用 dataclass 和简单接口，避免大型继承树。
- 插件加载逻辑必须隔离在 `mini_linter.plugins`。

## 注释规则

- 使用中文进行注释
- 每个 Python 文件头部必须有文件元信息，包含：上次修改时间（yyyy-MM-dd-HH:mm）、上次修改内容、上次修改者、文件设计、文件功能、文件创建者，每一条换行。
- 每个函数、类前面必须有 docstring，简短说明函数作用、输入参数和输出参数。
- 在逻辑复杂的地方添加解释说明。
- 使用 `if ... else` 语句时，需要在 `else` 后注释剩下的 condition 是什么。
- 使用 `if ...: continue` 结构后，需要在没有被 `continue` 的分支前注释什么情况会进入该分支。
- 更新代码时必须同步检查并更新相关注释，避免注释和实现不一致。

## 测试要求

- 使用 `pytest`。
- 测试默认集成 coverage，覆盖率目标包是 `mini_linter`。
- 测试coverage需要达到90%以上
- 每条规则都需要 pass case 和 fail case。
- CLI 行为变化时，需要测试 JSON 输出和退出码。
- 规则文案变化时，需要测试 lang JSON 强制渲染行为。
- 不允许新增没有对应 unit test 的功能。

## 修改流程

1. 先阅读 `.agents/context.md`，理解仓库结构。
2. 修改代码前，先检查所有文件被修改的内容
3. 修改规则或插件前，先阅读 `.agents/rule-authoring.md`。
4. 实现、测试、相关注释必须一起更新。
5. 如果用户可见行为、安装方式、命令参数、配置或规则能力变化，必须同步更新 `README.md`。
6. 先运行改动范围对应的 focused tests。
7. 完成前运行完整测试套件。

## Agent 边界

- 没有充分理由，不要引入新的运行时依赖；`tomli` 是唯一允许的 Python <3.11 兼容例外。
- 初版不实现自动修复。
- 不要随意改变 JSON 输出结构；测试必须保护该契约。
- 除非具体规则确实需要，不要加入宽泛的框架式抽象。
