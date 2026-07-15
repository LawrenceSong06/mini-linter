"""
上次修改时间: 2026-07-14-22:55
上次修改内容: Restore UTF-8 file header metadata
上次修改者: Agent Joe
文件设计: Agent collaboration rules
文件功能: Check AGENTS.md and .agents templates.
文件创建者: Agent Joe
"""

from __future__ import annotations

from mini_linter.models import RuleContext, Violation
from mini_linter.rules.base import BaseRule


class AgentsGuideExistsRule(BaseRule):
    """检查根目录是否存在 AGENTS.md。

    输入: 项目级 RuleContext。
    输出: 缺少 AGENTS.md 时返回 violation。
    """

    id = "agent.agents_guide_exists"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行 AGENTS.md 存在性检查。

        输入: RuleContext。
        输出: 缺失文件 violation 列表。
        """

        if not context.is_project:
            return []
        
        if (context.root / "AGENTS.md").exists():
            return []
        
        return [self.violation(context, path=context.root / "AGENTS.md")]


class AgentsTemplatesExistRule(BaseRule):
    """检查 `.agents/` 必需模板是否存在。

    输入: 项目级 RuleContext。
    输出: 每个缺失模板对应一个 violation。
    """

    id = "agent.templates_exist"
    default_severity = "error"
    required = (
        ".agents/context.md",
        ".agents/rule-authoring.md",
        ".agents/review-checklist.md",
        ".agents/task-template.md",
    )

    def check(self, context: RuleContext) -> list[Violation]:
        """执行 Agent 模板存在性检查。

        输入: RuleContext。
        输出: 缺失模板 violation 列表。
        """

        if not context.is_project:
            return []
        
        violations: list[Violation] = []
        for template in self.required:
            path = context.root / template

            if not path.exists():
                violations.append(self.violation(context, path=path, details={"template": template}))
                
        return violations
