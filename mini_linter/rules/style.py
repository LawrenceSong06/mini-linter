"""上次修改: 2026-07-14; 设计: 代码风格规则; 功能: 检查文件长度、函数长度和测试命名。"""

from __future__ import annotations

import ast

from mini_linter.models import RuleContext, Violation
from mini_linter.rules.base import BaseRule


class FileTooLongRule(BaseRule):
    """检查 Python 文件是否过长。

    输入: RuleContext，读取 `max_lines` 规则配置。
    输出: 文件超过行数限制时返回一个 violation。
    """

    id = "style.file_too_long"
    default_severity = "warning"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行文件长度检查。

        输入: 当前文件上下文。
        输出: 超长文件 violation 列表。
        """
        if context.is_project or context.path.suffix != ".py":
            return []
        
        max_lines = int(context.config.rule_options(self.id).get("max_lines", 300))
        line_count = len(context.source.splitlines())
        if line_count <= max_lines:
            return []
        
        return [self.violation(context, details={"line_count": line_count, "max_lines": max_lines})]


class FunctionTooLongRule(BaseRule):
    """检查函数或异步函数是否过长。

    输入: RuleContext，读取 AST 和 `max_lines` 配置。
    输出: 每个超长函数对应一个 violation。
    """

    id = "style.function_too_long"
    default_severity = "warning"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行函数长度检查。

        输入: 当前文件上下文。
        输出: 超长函数 violation 列表。
        """
        if context.is_project or context.tree is None:
            return []
        
        max_lines = int(context.config.rule_options(self.id).get("max_lines", 50))
        violations: list[Violation] = []
        lines = context.source.splitlines()

        for node in ast.walk(context.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                # Python 3.8+ 提供 end_lineno；Python 3.7 使用缩进 fallback。
                end_lineno = getattr(node, "end_lineno", None) or _function_end_lineno(lines, node)
                line_count = end_lineno - node.lineno + 1

                if line_count > max_lines:
                    violations.append(
                        self.violation(
                            context,
                            line=node.lineno,
                            column=node.col_offset + 1,
                            details={"name": node.name, "line_count": line_count, "max_lines": max_lines},
                        )
                    )

        return violations


class TestFileNamingRule(BaseRule):
    """检查 tests 目录下的测试文件命名。

    输入: RuleContext。
    输出: 不符合 pytest 命名约定时返回 violation。
    """

    id = "style.test_file_naming"
    default_severity = "info"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行测试文件命名检查。

        输入: 当前文件上下文。
        输出: 命名不合规 violation 列表。
        """
        if context.is_project or context.path.suffix != ".py":
            return []
        
        parts = set(context.path.relative_to(context.root).parts)
        if "tests" not in parts:
            return []
        
        filename = context.path.name
        if filename.startswith("test_") or filename.endswith("_test.py"):
            return []
        
        return [self.violation(context, details={"filename": filename})]


def _function_end_lineno(lines: list[str], node: ast.AST) -> int:
    """在 Python 3.7 中根据缩进估算函数结束行。

    输入: 源码行列表和函数 AST 节点。
    输出: 函数体最后一行的 1-based 行号。
    """
    
    start_index = getattr(node, "lineno", 1) - 1
    base_indent = getattr(node, "col_offset", 0)
    end_lineno = start_index + 1
    for index in range(start_index + 1, len(lines)):
        line = lines[index]

        if not line.strip():
            end_lineno = index + 1
            continue
        # 没有被 continue 的情况: 当前行非空，需要用缩进判断是否仍在函数体内。

        indent = len(line) - len(line.lstrip())
        if indent <= base_indent:
            break

        end_lineno = index + 1
    
    return end_lineno
