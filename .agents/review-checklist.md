# Agent Review Checklist

完成改动前使用这份 checklist。

## 行为

- 改动符合用户请求的范围。
- JSON 输出保持可解析且稳定。
- 每个 violation 都同时包含 `message` 和 `hint`。
- 规则严重级别必须是 `error`、`warning` 或 `info` 之一。

## 测试

- 新行为有 pytest 覆盖。
- 完整测试会输出 `mini_linter` 覆盖率。
- 每条新规则至少有一个 pass case 和一个 fail case。
- CLI 行为变化需要包含输出和退出码测试。
- 涉及规则文案时，需要覆盖 lang JSON 强制渲染行为。

## 注释与 README

- 每个 Python 文件头部都有简短文件元信息：上次修改时间、文件设计、文件功能。
- 每个函数和类都有 docstring，说明作用、输入和输出。
- 复杂逻辑有必要的解释说明。
- `else` 分支后说明剩余 condition。
- `if ...: continue` 后的可达分支前说明进入条件。
- 代码变更已同步更新相关注释。
- 用户可见行为、安装方式、命令参数、配置或规则能力变化时，`README.md` 已同步更新。

## 设计

- 运行时代码只使用标准库，Python <3.11 的 `tomli` fallback 除外。
- 模块保持小而聚焦。
- 插件加载保持隔离。
- 配置保持显式，并有文档说明。

## Agent 上下文

- `AGENTS.md` 保持准确。
- `.agents/context.md` 反映任何结构变化。
- `.agents/rule-authoring.md` 反映任何规则 API 变化。
- `.agents/review-checklist.md` 和 `.agents/task-template.md` 反映新的协作要求。
