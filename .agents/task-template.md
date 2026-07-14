# Agent 任务模板

## 目标

说明具体的行为变化。

## 需要阅读的上下文

- `AGENTS.md`
- `.agents/context.md`
- 如果涉及规则或插件，阅读 `.agents/rule-authoring.md`
- 相关实现和测试

## 实现注意事项

- 运行时依赖保持标准库优先。
- 实现变更必须同步新增或更新测试。
- 保持 JSON-first CLI 输出。
- 确保每个 violation 都有 `message` 和 `hint`。

## 验证

- 对改动模块运行 focused pytest tests。
- 最终交付前运行完整 pytest suite。

## 交付说明

总结行为变化、已运行测试和任何已知限制。
