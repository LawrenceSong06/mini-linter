"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Register built-in comment rules
上次修改者: Agent Joe
文件设计: Built-in rule registry
文件功能: Return built-in rule instances.
文件创建者: Agent Joe
"""

from __future__ import annotations

from mini_linter.models import Rule
from mini_linter.rules.agent import AgentsGuideExistsRule, AgentsTemplatesExistRule
from mini_linter.rules.comments import CodeBlockCommentRequiredRule, FileHeaderRequiredRule, PublicDocstringRequiredRule
from mini_linter.rules.imports import ForbiddenImportRule, LayerImportBoundaryRule
from mini_linter.rules.style import FileTooLongRule, FunctionTooLongRule, TestFileNamingRule


def built_in_rules() -> list[Rule]:
    """返回内置规则实例。

    输入: 无。
    输出: 默认规则实例列表。
    """
    
    return [
        FileTooLongRule(),
        FunctionTooLongRule(),
        TestFileNamingRule(),
        FileHeaderRequiredRule(),
        PublicDocstringRequiredRule(),
        CodeBlockCommentRequiredRule(),
        ForbiddenImportRule(),
        LayerImportBoundaryRule(),
        AgentsGuideExistsRule(),
        AgentsTemplatesExistRule(),
    ]
