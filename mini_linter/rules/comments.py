"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Add built-in comment rules
上次修改者: Agent Joe
文件设计: Comment rules
文件功能: Check file header metadata, public docstrings, and code block comments.
文件创建者: Agent Joe
"""

from __future__ import annotations

import ast

from mini_linter.models import RuleContext, Violation
from mini_linter.rules.base import BaseRule

HEADER_FIELDS = (
    "上次修改时间",
    "上次修改内容",
    "上次修改者",
    "文件设计",
    "文件功能",
    "文件创建者",
)


class FileHeaderRequiredRule(BaseRule):
    """检查 Python 文件头元信息。

    输入: RuleContext。
    输出: 缺少文件头字段时返回 violation。
    """

    id = "style.comments.file_header_required"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行文件头检查。

        输入: 当前文件上下文。
        输出: 缺失文件头 violation 列表。
        """
        if not _is_python_file(context):
            return []

        relative_path = context.relative_path
        if _is_test_path(relative_path) or relative_path.endswith("__init__.py"):
            return []

        header_text = "\n".join(context.source.splitlines()[:20])
        missing = [field for field in HEADER_FIELDS if field not in header_text]
        if not missing:
            return []

        return [
            self.violation(
                context,
                line=1,
                column=1,
                details={"filename": relative_path, "missing_fields": "、".join(missing)},
            )
        ]


class PublicDocstringRequiredRule(BaseRule):
    """检查公开函数、类和方法是否存在 docstring。

    输入: RuleContext。
    输出: 缺少 docstring 时返回 violation。
    """

    id = "style.comments.public_docstring_required"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行公开 docstring 检查。

        输入: 当前文件上下文。
        输出: docstring 缺失 violation 列表。
        """
        if not _is_python_file(context) or context.tree is None:
            return []

        relative_path = context.relative_path
        if _is_test_path(relative_path):
            return []

        violations: list[Violation] = []
        for node in ast.walk(context.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            # 没有被 continue 的情况: 当前节点是需要判断公开性的符号。

            name = getattr(node, "name", "")
            if name.startswith("_"):
                continue
            # 没有被 continue 的情况: 当前符号是公开符号，需要检查 docstring。

            if ast.get_docstring(node):
                continue
            # 没有被 continue 的情况: 当前公开符号缺少 docstring。

            violations.append(
                self.violation(
                    context,
                    line=_first_line_of(node),
                    column=1,
                    details={"filename": relative_path, "name": name, "kind": type(node).__name__},
                )
            )

        return violations


class CodeBlockCommentRequiredRule(BaseRule):
    """检查函数内部语义代码块前是否有说明注释。

    输入: RuleContext。
    输出: 代码块缺少说明注释时返回 violation。
    """

    id = "style.comments.code_block_comment_required"
    default_severity = "warning"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行代码块注释检查。

        输入: 当前文件上下文。
        输出: 缺少代码块注释 violation 列表。
        """
        if not _is_python_file(context) or context.tree is None:
            return []

        relative_path = context.relative_path
        if _is_test_path(relative_path):
            return []

        minimum_block_lines = _minimum_block_lines(context)
        lines = context.source.splitlines()
        violations: list[Violation] = []

        for node in ast.walk(context.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 没有被 continue 的情况: 当前节点是函数，需要检查函数体语义块。

            for statement_list in _statement_lists_inside_function(node):
                for statement in _block_start_statements(statement_list, lines, minimum_block_lines):
                    if _has_comment_before(lines, statement.lineno):
                        continue
                    # 没有被 continue 的情况: 当前语义块前没有说明注释。

                    violations.append(
                        self.violation(
                            context,
                            line=_first_line_of(statement),
                            column=1,
                            details={"filename": relative_path, "name": "block", "kind": "block_comment"},
                        )
                    )

        return violations


def _is_python_file(context: RuleContext) -> bool:
    """判断当前上下文是否是 Python 文件。

    输入: RuleContext。
    输出: 文件级 Python 上下文返回 True。
    """
    return not context.is_project and context.path.suffix == ".py"


def _is_test_path(path: str) -> bool:
    """判断路径是否位于 tests 目录。

    输入: POSIX 相对路径。
    输出: 位于 tests 目录时返回 True。
    """
    return path.startswith("tests/") or "/tests/" in path


def _first_line_of(node: ast.AST) -> int:
    """获取 AST 节点行号。

    输入: AST 节点。
    输出: 1-based 行号。
    """
    return getattr(node, "lineno", 1) or 1


def _minimum_block_lines(context: RuleContext) -> int:
    """读取需要代码块注释的最小代码行数。

    输入: RuleContext。
    输出: 至少为 1 的代码块行数。
    """
    configured_value = context.config.rule_options(CodeBlockCommentRequiredRule.id).get("min_block_lines", 1)
    try:
        minimum = int(configured_value)
    except (TypeError, ValueError):
        return 1

    return max(1, minimum)


def _statement_lists_inside_function(function_node: ast.AST) -> list[list[ast.stmt]]:
    """收集函数内部需要检查的语句列表。

    输入: 函数或异步函数节点。
    输出: 去除 docstring 后的函数体语句列表集合。
    """
    body = getattr(function_node, "body", [])
    statements = _without_docstring(body)

    return [statements] if statements else []


def _without_docstring(statements: list[ast.stmt]) -> list[ast.stmt]:
    """去除语句列表开头的 docstring。

    输入: AST 语句列表。
    输出: 去除 docstring 后的语句列表。
    """
    if not statements:
        return []

    first_statement = statements[0]
    if isinstance(first_statement, ast.Expr) and _string_value(getattr(first_statement, "value", None)) is not None:
        return statements[1:]
    else:
        # else 条件: 第一条语句不是 docstring，保留原语句列表。
        return statements


def _string_value(node: ast.AST | None) -> str | None:
    """提取 AST 字符串字面量。

    输入: AST 节点。
    输出: 字符串值；不是字符串时返回 None。
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    return None


def _block_start_statements(
    statements: list[ast.stmt],
    lines: list[str],
    minimum_block_lines: int,
) -> list[ast.stmt]:
    """返回语句列表中的代码块起始语句。

    输入: AST 语句列表、源码行列表、最小代码块行数。
    输出: 需要注释的语义块起始语句。
    """
    starts: list[ast.stmt] = []
    current_block: list[ast.stmt] = []
    previous_statement: ast.stmt | None = None

    for statement in statements:
        if previous_statement is None or _has_blank_between(lines, previous_statement, statement):
            _append_block_start_if_needed(starts, current_block, lines, minimum_block_lines)
            current_block = [statement]
        else:
            # else 条件: 当前语句与上一语句之间没有空行，属于同一语义块。
            current_block.append(statement)

        previous_statement = statement

    _append_block_start_if_needed(starts, current_block, lines, minimum_block_lines)

    return starts


def _append_block_start_if_needed(
    starts: list[ast.stmt],
    block: list[ast.stmt],
    lines: list[str],
    minimum_block_lines: int,
) -> None:
    """在代码块达到阈值时记录起始语句。

    输入: 起始语句列表、当前代码块、源码行列表、最小代码块行数。
    输出: 无。
    """
    if not block:
        return

    if _block_code_line_count(block, lines) >= minimum_block_lines:
        starts.append(block[0])


def _block_code_line_count(block: list[ast.stmt], lines: list[str]) -> int:
    """统计代码块中的实际代码行数。

    输入: 当前代码块和源码行列表。
    输出: 非空且非注释的代码行数量。
    """
    start_line = block[0].lineno
    end_line = getattr(block[-1], "end_lineno", block[-1].lineno)
    count = 0

    for line in lines[start_line - 1 : end_line]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1

    return count


def _has_blank_between(lines: list[str], previous_statement: ast.stmt, current_statement: ast.stmt) -> bool:
    """判断两个语句之间是否有空行。

    输入: 源码行列表、前一个语句、当前语句。
    输出: 存在空行时返回 True。
    """
    previous_end = getattr(previous_statement, "end_lineno", previous_statement.lineno)
    current_start = current_statement.lineno

    for index in range(previous_end, current_start - 1):
        if 0 <= index < len(lines) and not lines[index].strip():
            return True

    return False


def _has_comment_before(lines: list[str], line_number: int) -> bool:
    """判断指定行前是否有代码块说明注释。

    输入: 源码行列表和语句行号。
    输出: 最近非空上一行是注释时返回 True。
    """
    index = line_number - 2

    while index >= 0 and not lines[index].strip():
        index -= 1

    return index >= 0 and lines[index].lstrip().startswith("#")
