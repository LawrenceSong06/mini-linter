"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Cover init generated example plugin
上次修改者: Agent Joe
文件设计: Plugin tests
文件功能: Verify trusted local plugin loading and execution.
文件创建者: Agent Joe
"""

from pathlib import Path

from mini_linter.config import LinterConfig
from mini_linter.config import load_config
from mini_linter.core import run_linter
from mini_linter.init_templates import create_init_template


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
    (tmp_path / "lang.json").write_text(
        '{"plugin.demo": {"message": "Plugin saw {filename}.", "hint": "Use this pattern for local custom rules."}}',
        encoding="utf-8",
    )
    
    config = LinterConfig(
        root=tmp_path,
        paths=("sample.py",),
        lang="lang.json",
        plugins=("plugin_rules.py",),
        fail_on="warning",
    )

    result = run_linter(config)

    assert not result.ok
    assert result.violations[0].rule_id == "plugin.demo"
    assert result.violations[0].message == "Plugin saw sample.py."


def test_init_generated_example_plugin_checks_hello_world(tmp_path: Path) -> None:
    """验证 init 生成的示例插件可以执行。

    输入: init 模板、缺少和包含 hello world 的 Python 文件。
    输出: 断言缺少精确字符串时失败，包含时通过。
    """

    create_init_template(tmp_path)
    (tmp_path / "AGENTS.md").write_text("guide", encoding="utf-8")
    agents = tmp_path / ".agents"
    agents.mkdir()
    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")

    (tmp_path / "bad.py").write_text("print('missing')\n", encoding="utf-8")
    config = load_config(tmp_path / "linter_config.toml")

    fail_result = run_linter(config)

    assert not fail_result.ok
    assert fail_result.violations[0].rule_id == "plugin.hello_world"
    assert fail_result.violations[0].details["filename"] == "bad.py"

    (tmp_path / "bad.py").write_text("print('hello world!')\n", encoding="utf-8")
    pass_result = run_linter(config)

    assert pass_result.ok
    assert pass_result.violations == ()
