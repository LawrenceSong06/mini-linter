"""上次修改: 2026-07-14; 设计: 插件测试; 功能: 验证可信本地插件规则加载和执行。"""

from pathlib import Path

from mini_linter.config import LinterConfig
from mini_linter.core import run_linter


def test_loads_and_runs_local_plugin_rule(tmp_path: Path) -> None:
    """验证本地插件规则能被加载并产生 violation。

    输入: 临时项目、插件文件和 LinterConfig。
    输出: 断言插件 violation 出现在 lint 结果中。
    """
    (tmp_path / "AGENTS.md").write_text("guide", encoding="utf-8")
    agents = tmp_path / ".agents"
    agents.mkdir()
    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")
    (tmp_path / "sample.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "plugin_rules.py").write_text(
        """
from mini_linter.rules.base import BaseRule

class DemoPluginRule(BaseRule):
    \"\"\"测试用插件规则。

    输入: RuleContext。
    输出: 非项目级上下文返回一个 violation。
    \"\"\"

    id = "plugin.demo"
    default_severity = "warning"
    message = "Plugin saw {filename}."
    hint = "Use this pattern for local custom rules."

    def check(self, context):
        \"\"\"执行测试插件检查。

        输入: RuleContext。
        输出: 插件 violation 列表。
        \"\"\"
        if context.is_project:
            return []
        return [self.violation(context, details={"filename": context.path.name})]
""",
        encoding="utf-8",
    )
    config = LinterConfig(root=tmp_path, paths=("sample.py",), plugins=("plugin_rules.py",), fail_on="warning")

    result = run_linter(config)

    assert not result.ok
    assert result.violations[0].rule_id == "plugin.demo"
    assert result.violations[0].message == "Plugin saw sample.py."
