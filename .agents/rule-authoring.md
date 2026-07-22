# 规则编写指南

规则可以内置在 `mini_linter/rules/` 下，也可以从可信本地插件文件加载。

## 规则接口

每条规则都是一个类，包含：

- `id`：稳定的规则标识，例如 `style.file_too_long`。
- `default_severity`：`error`、`warning` 或 `info` 之一。
- `check(context)`：返回 violation 列表。

规则应该是确定性的，不应修改全局状态。

## Violation 要求

每个 violation 必须包含：

- `rule_id`
- `severity`
- `path`
- `line`
- `column`
- `message`
- `hint`
- `details`

项目级 finding 使用 line `1` 和 column `1`。

## Lang 文案

最终输出的 severity、message 和 hint 必须来自 lang JSON。规则类不应定义最终 message 和 hint 字段。lang JSON 文件必须按 rule id 提供文案：

```json
{
  "style.file_too_long": {
    "severity": "warning",
    "message": "File has {line_count} lines; max is {max_lines}.",
    "hint": "Split this file into smaller modules."
  }
}
```

新增或修改规则时，需要同步更新测试，证明：

- 缺少 lang severity 或文案时会失败；
- lang JSON 文案可以正确渲染；
- violation 始终包含 `severity`、`message` 和 `hint`。

## 内置规则要求

- 规则要小而聚焦。
- 能使用 AST 表达 Python 结构时，优先使用 AST。
- 文档和 Agent 模板规则使用路径级检查。
- 架构逻辑必须来自显式配置，不要依赖隐藏约定。

## 插件规则

插件文件是可信本地 Python 文件。插件规则类和内置规则使用同一接口。加载器会发现定义了 `id` 和 `check` 的类。
