"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Cover exclude path pattern behavior
上次修改者: Agent Joe
文件设计: Rule context tests
文件功能: Verify rule pass and fail cases using sample programs.
文件创建者: Agent Joe
"""

from __future__ import annotations

import ast
import shutil
from pathlib import Path

from mini_linter.config import LinterConfig
from mini_linter.core import _discover_python_files
from mini_linter.models import RuleContext
from mini_linter.rules.agent import AgentsGuideExistsRule, AgentsTemplatesExistRule
from mini_linter.rules.imports import ForbiddenImportRule, LayerImportBoundaryRule
from mini_linter.rules.style import FileTooLongRule, FunctionTooLongRule, TestFileNamingRule


def _sets_root() -> Path:
    """返回规则样例数据根目录。

    输入: 无。
    输出: `tests/contexts/sets/rules` 的绝对路径。
    """
    return Path(__file__).resolve().parents[1] / "sets" / "rules"


def _copy_sample_tree(tmp_path: Path) -> Path:
    """复制样例程序到临时目录。

    输入: pytest tmp_path。
    输出: 临时项目根目录。
    """
    root = tmp_path / "project"
    shutil.copytree(_sets_root(), root)

    return root


def _file_context(root: Path, relative: str, config: LinterConfig) -> RuleContext:
    """为样例文件创建 RuleContext。

    输入: 项目根目录、相对文件路径和配置。
    输出: 带源码、AST 和文件列表的 RuleContext。
    """
    path = root / relative
    source = path.read_text(encoding="utf-8")
    files = tuple(sorted(root.rglob("*.py")))

    return RuleContext(root, path, source, ast.parse(source), config, files)


def _project_context(root: Path, config: LinterConfig) -> RuleContext:
    """为项目级规则创建 RuleContext。

    输入: 项目根目录和配置。
    输出: 标记为项目级的 RuleContext。
    """
    files = tuple(sorted(root.rglob("*.py")))
    return RuleContext(root, root, "", None, config, files, True)


def test_file_too_long_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证文件过长规则在样例程序上的 pass/fail。

    输入: style_file_pass.py 和 style_file_fail.py。
    输出: 断言 pass 样例无 violation，fail 样例有 violation。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root, rules={"style.file_too_long": {"max_lines": 10}})
    rule = FileTooLongRule()

    assert rule.check(_file_context(root, "style_file_pass.py", config)) == []
    
    violations = rule.check(_file_context(root, "style_file_fail.py", config))

    assert [item.rule_id for item in violations] == ["style.file_too_long"]


def test_function_too_long_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证函数过长规则在样例程序上的 pass/fail。

    输入: style_function_pass.py 和 style_function_fail.py。
    输出: 断言 pass 样例无 violation，fail 样例有 violation。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root, rules={"style.function_too_long": {"max_lines": 8}})
    rule = FunctionTooLongRule()

    assert rule.check(_file_context(root, "style_function_pass.py", config)) == []
    
    violations = rule.check(_file_context(root, "style_function_fail.py", config))

    assert [item.rule_id for item in violations] == ["style.function_too_long"]
    assert violations[0].details["name"] == "long_function"


def test_test_file_naming_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证测试文件命名规则在样例程序上的 pass/fail。

    输入: tests/test_naming_pass.py 和 tests/naming_fail.py。
    输出: 断言 pass 样例无 violation，fail 样例有 violation。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root)
    rule = TestFileNamingRule()

    assert rule.check(_file_context(root, "tests/test_naming_pass.py", config)) == []
    
    violations = rule.check(_file_context(root, "tests/naming_fail.py", config))

    assert [item.rule_id for item in violations] == ["style.test_file_naming"]


def test_forbidden_import_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证禁止 import 规则在样例程序上的 pass/fail。

    输入: import_forbidden_pass.py 和 import_forbidden_fail.py。
    输出: 断言 pass 样例无 violation，fail 样例有 violation。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root, rules={"imports.forbidden": {"modules": ["os"]}})
    rule = ForbiddenImportRule()

    assert rule.check(_file_context(root, "import_forbidden_pass.py", config)) == []
    
    violations = rule.check(_file_context(root, "import_forbidden_fail.py", config))

    assert [item.rule_id for item in violations] == ["imports.forbidden"]
    assert violations[0].details["module"] == "os.path"


def test_layer_import_boundary_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证层级架构规则在样例程序上的 pass/fail。

    输入: architecture/app/pass_service.py 和 architecture/app/fail_service.py。
    输出: 断言允许 import 无 violation，不允许 import 有 violation。
    """
    root = _copy_sample_tree(tmp_path) / "architecture"
    config = LinterConfig(
        root=root,
        architecture={
            "layers": [
                {"name": "app", "paths": ["app/*.py"], "may_import": ["domain"]},
                {"name": "infra", "paths": ["infra/*.py"], "may_import": []},
                {"name": "domain", "paths": ["domain/*.py"], "may_import": []},
            ]
        },
    )
    rule = LayerImportBoundaryRule()

    assert rule.check(_file_context(root, "app/pass_service.py", config)) == []
    
    violations = rule.check(_file_context(root, "app/fail_service.py", config))

    assert [item.rule_id for item in violations] == ["architecture.layers"]
    assert violations[0].details["target_layer"] == "infra"


def test_agents_guide_exists_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证 AGENTS.md 存在性规则的 pass/fail。

    输入: 临时项目根目录。
    输出: 断言缺失 AGENTS.md 时失败，创建后通过。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root)
    context = _project_context(root, config)
    rule = AgentsGuideExistsRule()

    violations = rule.check(context)
    assert [item.rule_id for item in violations] == ["agent.agents_guide_exists"]

    (root / "AGENTS.md").write_text("guide", encoding="utf-8")
    assert rule.check(context) == []


def test_agents_templates_exist_rule_context_pass_and_fail(tmp_path: Path) -> None:
    """验证 `.agents/` 模板存在性规则的 pass/fail。

    输入: 临时项目根目录。
    输出: 断言缺失模板时失败，创建后通过。
    """
    root = _copy_sample_tree(tmp_path)
    config = LinterConfig(root=root)
    context = _project_context(root, config)
    rule = AgentsTemplatesExistRule()

    violations = rule.check(context)
    assert {item.rule_id for item in violations} == {"agent.templates_exist"}

    agents = root / ".agents"
    agents.mkdir()
    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")

    assert rule.check(context) == []


def test_discover_python_files_uses_exclude_path_patterns(tmp_path: Path) -> None:
    """验证 exclude 使用路径模式排除目录。

    输入: 包含 src 和 .venv 的临时项目。
    输出: 断言 `**/.venv/**` 排除虚拟环境文件。
    """

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / ".venv" / "Lib").mkdir(parents=True)
    (tmp_path / ".venv" / "Lib" / "ignored.py").write_text("print('skip')\n", encoding="utf-8")
    config = LinterConfig(root=tmp_path, paths=(".",), exclude=("**/.venv/**",))

    files = _discover_python_files(config, config.paths)

    assert [path.relative_to(tmp_path).as_posix() for path in files] == ["src/app.py"]
