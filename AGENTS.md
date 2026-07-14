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
- 新规则必须包含默认 lang fallback 文案和测试。

## 代码风格

- 公共函数和 dataclass 字段需要类型标注。
- 函数保持短小，副作用要明显。
- 避免隐式全局状态。
- 显式传递配置和上下文。
- 优先使用 dataclass 和简单接口，避免大型继承树。
- 插件加载逻辑必须隔离在 `mini_linter.plugins`。

## 测试要求

- 使用 `pytest`。
- 每条规则都需要 pass case 和 fail case。
- CLI 行为变化时，需要测试 JSON 输出和退出码。
- 规则文案变化时，需要测试 lang fallback 行为。
- 不允许新增没有对应 unit test 的功能。

## 修改流程

1. 先阅读 `.agents/context.md`，理解仓库结构。
2. 修改规则或插件前，先阅读 `.agents/rule-authoring.md`。
3. 实现和测试必须一起更新。
4. 先运行改动范围对应的 focused tests。
5. 完成前运行完整测试套件。

## Agent 边界

- 没有充分理由，不要引入新的运行时依赖；`tomli` 是唯一允许的 Python <3.11 兼容例外。
- 初版不实现自动修复。
- 不要随意改变 JSON 输出结构；测试必须保护该契约。
- 除非具体规则确实需要，不要加入宽泛的框架式抽象。
