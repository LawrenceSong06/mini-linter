# 插件规则编写指南

`mini-linter` 支持从可信本地 Python 文件加载插件规则。插件适合放项目专属规则，例如团队 import 约束、目录约定、文档检查或 Agent 协作规范。

## 插件加载方式

在目标项目的 `pyproject.toml` 中配置插件文件路径：

```toml
[tool.mini_linter]
paths = ["."]
lang = "lang/zh_cn.json"
plugins = ["tools/lint_rules.py"]
fail_on = "error"
```

`plugins` 中的路径相对于配置文件所在目录，也就是 mini-linter 的项目 root。

插件文件会作为可信本地 Python 代码执行。当前版本不提供沙箱隔离，因此不要加载不可信插件。

## 规则类接口

插件文件中直接定义的类，只要包含 `id` 和 `check`，就会被加载器发现并实例化。

推荐继承 `mini_linter.rules.base.BaseRule`：

```python
from mini_linter.rules.base import BaseRule


class NoPrintRule(BaseRule):
    """检查是否使用 print。

    输入: RuleContext。
    输出: 发现 print 调用时返回 violation。
    """

    id = "project.no_print"
    default_severity = "warning"
    def check(self, context):
        """执行 print 检查。

        输入: RuleContext。
        输出: violation 列表。
        """
        if context.is_project or context.tree is None:
            return []

        violations = []
        for node in context.tree.body:
            if getattr(node, "value", None) is None:
                continue
            # 没有被 continue 的情况: 当前节点可能是表达式语句，需要继续检查调用目标。
            call = node.value
            if getattr(getattr(call, "func", None), "id", None) == "print":
                violations.append(
                    self.violation(
                        context,
                        line=getattr(node, "lineno", 1),
                        column=getattr(node, "col_offset", 0) + 1,
                        details={"filename": context.path.name},
                    )
                )
        return violations
```

## 可用上下文

`check(context)` 会收到 `RuleContext`，常用字段包括：

- `context.root`：项目根目录。
- `context.path`：当前检查的路径。
- `context.relative_path`：相对项目根目录的 POSIX 路径。
- `context.source`：当前文件源码文本。
- `context.tree`：Python AST；语法错误或项目级上下文时可能为 `None`。
- `context.config`：当前 `LinterConfig`。
- `context.files`：本次发现的所有 Python 文件。
- `context.is_project`：是否为项目级上下文。

文件级规则通常跳过 `context.is_project`。项目级规则通常只在 `context.is_project` 为 `True` 时运行。

## 返回 violation

继承 `BaseRule` 后，优先使用 `self.violation(...)` 构造结果：

```python
return [
    self.violation(
        context,
        line=1,
        column=1,
        details={"name": "example"},
    )
]
```

每个最终输出的 violation 必须包含 `message` 和 `hint`。当前实现会强制从 lang JSON 中读取最终文案；规则类不应定义 `message` 和 `hint` 字段。

## 配置插件规则

插件规则和内置规则一样，可以在 `[tool.mini_linter.rules]` 下配置：

```toml
[tool.mini_linter.rules."project.no_print"]
enabled = true
```

规则内部可以通过以下方式读取参数：

```python
options = context.config.rule_options(self.id)
```

## 提供中文文案

插件规则必须通过 lang JSON 提供最终文案：

```json
{
  "project.no_print": {
    "message": "文件 `{filename}` 使用了 print。",
    "hint": "改用 logger，或返回结构化数据交给调用方处理。"
  }
}
```

## 测试建议

为每条插件规则至少准备：

- 一个 pass case：不应产生 violation。
- 一个 fail case：应产生目标 rule id 的 violation。
- 测试缺少 lang 文案时会失败。
- 测试 `message` 和 `hint` 是否由 lang JSON 正确渲染。

可以参考 `tests/test_plugins.py` 和 `tests/contexts/rules/test_rule_contexts.py` 的写法。
