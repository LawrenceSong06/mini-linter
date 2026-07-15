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
- 实现变更必须同步检查和更新相关注释。
- 用户可见行为、安装方式、命令参数、配置或规则能力变化时，必须同步更新 `README.md`。
- 保持 JSON-first CLI 输出。
- 确保每个 violation 都有 `message` 和 `hint`。
- 遵守 `AGENTS.md` 中的注释规则，特别是文件头部元信息、函数/类 docstring、`else` 和 `continue` 分支说明。

## 验证

- 对改动模块运行 focused pytest tests。
- 最终交付前运行完整 pytest suite，并确认 coverage 输出正常。

## 交付说明

总结行为变化、已运行测试和任何已知限制。
