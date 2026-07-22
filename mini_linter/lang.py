"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Read severity from lang catalog
上次修改者: Agent Joe
文件设计: Required language catalog
文件功能: Load lang JSON and render violation text.
文件创建者: Agent Joe
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mini_linter.models import SEVERITY_ORDER, Violation


@dataclass(frozen=True)
class LangCatalog:
    """保存按 rule id 索引的强制输出文案和严重度。

    输入: lang JSON 解析后的 entries。
    输出: 对 violation 应用必需的 severity、message 和 hint。
    """

    entries: dict[str, dict[str, str]]

    @classmethod
    def load(cls, path: Path | None) -> "LangCatalog":
        """加载 lang JSON 文件。

        输入: 可选 JSON 文件路径。
        输出: LangCatalog；路径为空或不存在时返回空 catalog。
        """

        if path is None or not path.exists():
            return cls(entries={})
        
        raw = json.loads(path.read_text(encoding="utf-8"))
        entries = {key: value for key, value in raw.items() if isinstance(value, dict)}

        return cls(entries=entries)

    def apply(self, violation: Violation) -> Violation:
        """将 lang JSON 文案应用到 violation。

        输入: 原始 violation。
        输出: lang JSON 渲染后的 violation；缺少字段时抛出 ValueError。
        """
        entry = self.entries.get(violation.rule_id)
        if not entry or "severity" not in entry or "message" not in entry or "hint" not in entry:
            raise ValueError(f"Missing lang severity/message/hint for rule: {violation.rule_id}")

        severity = entry["severity"]
        if severity not in SEVERITY_ORDER:
            raise ValueError(f"Invalid lang severity for rule: {violation.rule_id}")
        
        message = _render(entry["message"], violation.details)
        hint = _render(entry["hint"], violation.details)
        
        return Violation(
            rule_id=violation.rule_id,
            severity=severity,
            path=violation.path,
            line=violation.line,
            column=violation.column,
            message=message,
            hint=hint,
            details=violation.details,
        )


def _render(template: str, details: dict[str, Any]) -> str:
    """使用 violation details 渲染模板。

    输入: 模板字符串和 details。
    输出: 渲染后的字符串；缺少字段时保留原模板。
    """
    try:
        return template.format(**details)
    except KeyError:
        return template
