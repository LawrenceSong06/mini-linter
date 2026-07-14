"""上次修改: 2026-07-14; 设计: 轻量数据模型; 功能: 定义规则输入、输出和结果序列化。"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Severity = str
SEVERITY_ORDER: dict[Severity, int] = {"info": 0, "warning": 1, "error": 2}


@dataclass(frozen=True)
class Violation:
    """表示一条 lint 发现。

    输入: 规则 id、严重级别、位置、message、hint 和 details。
    输出: 可通过 `to_dict` 转为 JSON 友好的字典。
    """

    rule_id: str
    severity: Severity
    path: str
    line: int
    column: int
    message: str
    hint: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """将 violation 转成 JSON 可序列化字典。

        输入: 当前 violation 实例。
        输出: 包含定位、文案和 details 的字典。
        """
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "hint": self.hint,
            "details": self.details,
        }


@dataclass(frozen=True)
class RuleContext:
    """保存规则执行所需上下文。

    输入: 项目根目录、当前路径、源码、AST、配置和文件列表。
    输出: 规则通过该对象读取检查所需数据。
    """

    root: Path
    path: Path
    source: str
    tree: ast.AST | None
    config: Any
    files: tuple[Path, ...]
    is_project: bool = False

    @property
    def relative_path(self) -> str:
        """返回相对项目根目录的路径。

        输入: 当前上下文路径。
        输出: POSIX 风格相对路径；根外路径返回原始 POSIX 路径。
        """
        try:
            return self.path.relative_to(self.root).as_posix()
        except ValueError:
            return self.path.as_posix()


@dataclass(frozen=True)
class LintResult:
    """保存一次 lint 的聚合结果。

    输入: violations 和 fail_on 阈值。
    输出: ok、summary 和 JSON 友好的结果字典。
    """

    violations: tuple[Violation, ...]
    fail_on: Severity = "error"

    @property
    def ok(self) -> bool:
        """判断结果是否通过。

        输入: 当前 violations 和 fail_on 阈值。
        输出: 没有达到失败阈值的 violation 时返回 True。
        """
        threshold = SEVERITY_ORDER[self.fail_on]
        return not any(SEVERITY_ORDER[item.severity] >= threshold for item in self.violations)

    def summary(self) -> dict[str, int]:
        """统计各严重级别数量。

        输入: 当前 violations。
        输出: 包含 error、warning、info 和 total 的计数字典。
        """
        counts = {"error": 0, "warning": 0, "info": 0}
        for item in self.violations:
            counts[item.severity] += 1
        counts["total"] = len(self.violations)
        return counts

    def to_dict(self) -> dict[str, Any]:
        """将 lint 结果转成 JSON 可序列化字典。

        输入: 当前 lint 结果。
        输出: 包含 ok、summary 和 violations 的字典。
        """
        return {
            "ok": self.ok,
            "summary": self.summary(),
            "violations": [item.to_dict() for item in self.violations],
        }


class Rule:
    """规则接口基类。

    输入: 子类提供 id、severity、文案和 check 实现。
    输出: `check` 返回 violation 列表。
    """

    id: str
    default_severity: Severity
    message: str
    hint: str

    def check(self, context: RuleContext) -> list[Violation]:
        """执行规则检查。

        输入: RuleContext。
        输出: violation 列表；基类仅声明接口。
        """
        raise NotImplementedError
