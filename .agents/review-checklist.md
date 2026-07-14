# Agent Review Checklist

完成改动前使用这份 checklist。

## 行为

- 改动符合用户请求的范围。
- JSON 输出保持可解析且稳定。
- 每个 violation 都同时包含 `message` 和 `hint`。
- 规则严重级别必须是 `error`、`warning` 或 `info` 之一。

## 测试

- 新行为有 pytest 覆盖。
- 每条新规则至少有一个 pass case 和一个 fail case。
- CLI 行为变化需要包含输出和退出码测试。
- 涉及规则文案时，需要覆盖 lang fallback 行为。

## 设计

- 运行时代码只使用标准库，Python <3.11 的 `tomli` fallback 除外。
- 模块保持小而聚焦。
- 插件加载保持隔离。
- 配置保持显式，并有文档说明。

## Agent 上下文

- `AGENTS.md` 保持准确。
- `.agents/context.md` 反映任何结构变化。
- `.agents/rule-authoring.md` 反映任何规则 API 变化。
