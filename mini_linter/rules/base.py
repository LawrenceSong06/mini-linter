"""上次修改: 2026-07-14; 设计: 规则基础工具; 功能: 提供 violation 构造和模板渲染。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mini_linter.models import RuleContext, Severity, Violation


class BaseRule:
    """内置规则和插件规则的基础类。

    输入: 子类定义规则 id、默认 severity、message 和 hint。
    输出: 子类可复用 `violation` 构造标准 violation。
    """

    id = "base"
    default_severity: Severity = "warning"
    message = "Rule violation."
    hint = "Review this code and update it to satisfy the rule."

    def check(self, context: RuleContext) -> list[Violation]:
        """执行规则检查。

        输入: RuleContext。
        输出: violation 列表；基础类仅声明接口。
        """
        raise NotImplementedError

    def violation(
        self,
        context: RuleContext,
        *,
        path: Path | None = None,
        line: int = 1,
        column: int = 1,
        details: dict[str, Any] | None = None,
        severity: Severity | None = None,
    ) -> Violation:
        """构造标准 violation。

        输入: 上下文、可选位置、details 和 severity。
        输出: message/hint 已按 details 渲染的 Violation。
        """
        data = details or {}
        return Violation(
            rule_id=self.id,
            severity=severity or self.default_severity,
            path=_relative(context.root, path or context.path),
            line=line,
            column=column,
            message=_render(self.message, data),
            hint=_render(self.hint, data),
            details=data,
        )


def _render(template: str, details: dict[str, Any]) -> str:
    """渲染规则模板文本。

    输入: 模板字符串和 details。
    输出: 渲染文本；缺少字段时返回原模板。
    """
    try:
        return template.format(**details)
    except KeyError:
        return template


def _relative(root: Path, path: Path) -> str:
    """将路径转成相对 root 的 POSIX 字符串。

    输入: root 和待转换 path。
    输出: 相对路径；path 不在 root 下时返回原路径。
    """
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
