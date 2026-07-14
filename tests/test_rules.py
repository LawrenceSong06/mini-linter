"""上次修改: 2026-07-14; 设计: 内置规则测试; 功能: 验证每条规则的 pass/fail 行为。"""

from __future__ import annotations

import ast
from pathlib import Path

from mini_linter.config import LinterConfig
from mini_linter.models import RuleContext
from mini_linter.rules.agent import AgentsGuideExistsRule, AgentsTemplatesExistRule
from mini_linter.rules.imports import ForbiddenImportRule, LayerImportBoundaryRule
from mini_linter.rules.style import FileTooLongRule, FunctionTooLongRule, TestFileNamingRule


def context(tmp_path: Path, path: Path, source: str, config: LinterConfig | None = None) -> RuleContext:
    """创建测试用 RuleContext。

    输入: 临时根目录、文件路径、源码和可选配置。
    输出: 带 AST 的 RuleContext。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return RuleContext(
        root=tmp_path,
        path=path,
        source=source,
        tree=ast.parse(source),
        config=config or LinterConfig(root=tmp_path),
        files=(path,),
    )


def test_file_too_long_pass_and_fail(tmp_path: Path) -> None:
    """验证文件长度规则的通过和失败场景。

    输入: max_lines 配置和两个临时文件。
    输出: 断言超长文件产生 violation。
    """
    config = LinterConfig(root=tmp_path, rules={"style.file_too_long": {"max_lines": 1}})
    rule = FileTooLongRule()

    assert rule.check(context(tmp_path, tmp_path / "ok.py", "x = 1\n", config)) == []
    violations = rule.check(context(tmp_path, tmp_path / "bad.py", "x = 1\ny = 2\n", config))

    assert violations[0].rule_id == "style.file_too_long"
    assert violations[0].hint


def test_function_too_long_pass_and_fail(tmp_path: Path) -> None:
    """验证函数长度规则的通过和失败场景。

    输入: max_lines 配置和函数源码。
    输出: 断言超长函数记录函数名。
    """
    config = LinterConfig(root=tmp_path, rules={"style.function_too_long": {"max_lines": 2}})
    rule = FunctionTooLongRule()

    assert rule.check(context(tmp_path, tmp_path / "ok.py", "def ok():\n    pass\n", config)) == []
    violations = rule.check(context(tmp_path, tmp_path / "bad.py", "def bad():\n    x = 1\n    y = 2\n", config))

    assert violations[0].details["name"] == "bad"


def test_test_file_naming_pass_and_fail(tmp_path: Path) -> None:
    """验证测试文件命名规则。

    输入: tests 目录下的合规和不合规文件名。
    输出: 断言不合规命名产生 violation。
    """
    rule = TestFileNamingRule()

    assert rule.check(context(tmp_path, tmp_path / "tests" / "test_ok.py", "x = 1\n")) == []
    violations = rule.check(context(tmp_path, tmp_path / "tests" / "bad.py", "x = 1\n"))

    assert violations[0].rule_id == "style.test_file_naming"


def test_forbidden_import_pass_and_fail(tmp_path: Path) -> None:
    """验证禁止 import 规则。

    输入: 禁止模块配置和 import 源码。
    输出: 断言禁止模块产生 violation。
    """
    config = LinterConfig(root=tmp_path, rules={"imports.forbidden": {"modules": ["os"]}})
    rule = ForbiddenImportRule()

    assert rule.check(context(tmp_path, tmp_path / "ok.py", "import sys\n", config)) == []
    violations = rule.check(context(tmp_path, tmp_path / "bad.py", "import os.path\n", config))

    assert violations[0].details["module"] == "os.path"


def test_layer_import_boundary_pass_and_fail(tmp_path: Path) -> None:
    """验证层级 import 边界规则。

    输入: 三层架构配置和跨层 import 源码。
    输出: 断言未允许的 infra import 被报告。
    """
    config = LinterConfig(
        root=tmp_path,
        architecture={
            "layers": [
                {"name": "app", "paths": ["app/*.py"], "may_import": ["domain"]},
                {"name": "infra", "paths": ["infra/*.py"], "may_import": []},
                {"name": "domain", "paths": ["domain/*.py"], "may_import": []},
            ]
        },
    )
    app = tmp_path / "app" / "service.py"
    infra = tmp_path / "infra" / "db.py"
    domain = tmp_path / "domain" / "model.py"
    infra.parent.mkdir()
    infra.write_text("x = 1\n", encoding="utf-8")
    domain.parent.mkdir()
    domain.write_text("x = 1\n", encoding="utf-8")
    ctx = context(tmp_path, app, "import infra.db\nimport domain.model\n", config)
    ctx = RuleContext(ctx.root, ctx.path, ctx.source, ctx.tree, ctx.config, (app, infra, domain))

    violations = LayerImportBoundaryRule().check(ctx)

    assert len(violations) == 1
    assert violations[0].details["target_layer"] == "infra"


def test_agent_rules_pass_and_fail(tmp_path: Path) -> None:
    """验证 Agent 文档规则的缺失和通过场景。

    输入: 临时项目根目录。
    输出: 断言缺失文档会报错，补齐后通过。
    """
    project_context = RuleContext(tmp_path, tmp_path, "", None, LinterConfig(root=tmp_path), (), True)
    assert AgentsGuideExistsRule().check(project_context)
    assert len(AgentsTemplatesExistRule().check(project_context)) == 4

    (tmp_path / "AGENTS.md").write_text("guide", encoding="utf-8")
    agents = tmp_path / ".agents"
    agents.mkdir()
    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")

    assert AgentsGuideExistsRule().check(project_context) == []
    assert AgentsTemplatesExistRule().check(project_context) == []
