"""上次修改: 2026-07-14; 设计: 内置规则注册表; 功能: 汇总默认启用的规则实例。"""

from __future__ import annotations

from mini_linter.models import Rule
from mini_linter.rules.agent import AgentsGuideExistsRule, AgentsTemplatesExistRule
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
        ForbiddenImportRule(),
        LayerImportBoundaryRule(),
        AgentsGuideExistsRule(),
        AgentsTemplatesExistRule(),
    ]
