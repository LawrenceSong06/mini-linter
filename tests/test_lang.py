"""上次修改: 2026-07-14; 设计: lang 测试; 功能: 验证文案强制渲染和缺失报错。"""

from pathlib import Path

import pytest

from mini_linter.config import LinterConfig
from mini_linter.core import _lang_path
from mini_linter.core import run_linter
from mini_linter.lang import LangCatalog
from mini_linter.models import Violation
from mini_linter.rules import built_in_rules


def test_lang_catalog_renders_message_and_hint(tmp_path: Path) -> None:
    """验证 lang JSON 渲染 message 和 hint。

    输入: 临时 lang 文件和 violation。
    输出: 断言模板按 details 渲染。
    """

    lang = tmp_path / "lang.json"
    lang.write_text(
        '{"demo.rule": {"message": "Hello {name}", "hint": "Fix {name}"}}',
        encoding="utf-8",
    )
    violation = Violation("demo.rule", "warning", "x.py", 1, 1, "Default", "Default hint", {"name": "code"})

    rendered = LangCatalog.load(lang).apply(violation)

    assert rendered.message == "Hello code"
    assert rendered.hint == "Fix code"


def test_lang_catalog_requires_message_and_hint(tmp_path: Path) -> None:
    """验证没有 lang 条目时不允许输出文案。

    输入: 不存在的 lang 路径和 violation。
    输出: 断言缺少 message/hint 会抛出 ValueError。
    """
    violation = Violation("demo.rule", "warning", "x.py", 1, 1, "Default", "Default hint", {})

    with pytest.raises(ValueError, match="demo.rule"):
        LangCatalog.load(tmp_path / "missing.json").apply(violation)


def test_run_linter_rejects_incomplete_lang_for_output_violation(tmp_path: Path) -> None:
    """验证 run_linter 拒绝不完整 lang 文案。

    输入: 会触发禁止 import 的临时项目，并提供缺少该 rule id 的 lang。
    输出: 断言缺少 rule id 文案会抛出 ValueError。
    """
    (tmp_path / "AGENTS.md").write_text("guide", encoding="utf-8")
    agents = tmp_path / ".agents"
    agents.mkdir()

    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")

    (tmp_path / "bad.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / "lang.json").write_text("{}", encoding="utf-8")
    config = LinterConfig(
        root=tmp_path,
        paths=("bad.py",),
        lang="lang.json",
        rules={"imports.forbidden": {"modules": ["os"]}},
    )

    with pytest.raises(ValueError, match="imports.forbidden"):
        run_linter(config)


def test_default_chinese_lang_file_renders_builtin_rule() -> None:
    """验证默认中文 lang 文件可渲染内置规则文案。

    输入: 包内的 `mini_linter/lang/zh_cn.json` 和内置规则 violation。
    输出: 断言中文 message 和 hint 被应用。
    """
    lang = Path(__file__).resolve().parents[1] / "mini_linter" / "lang" / "zh_cn.json"
    violation = Violation(
        "style.file_too_long",
        "warning",
        "x.py",
        1,
        1,
        "Default",
        "Default hint",
        {"line_count": 10, "max_lines": 5},
    )

    rendered = LangCatalog.load(lang).apply(violation)

    assert rendered.message == "文件共有 10 行，超过限制 5 行。"
    assert "拆分" in rendered.hint


def test_default_chinese_lang_file_covers_all_builtin_rules() -> None:
    """验证默认中文 lang 文件覆盖所有内置规则。

    输入: 内置规则列表和 `mini_linter/lang/zh_cn.json`。
    输出: 断言每个 rule id 都有 message 和 hint。
    """
    lang = LangCatalog.load(Path(__file__).resolve().parents[1] / "mini_linter" / "lang" / "zh_cn.json")
    for rule in built_in_rules():
        entry = lang.entries.get(rule.id)
        assert entry is not None, rule.id
        assert entry.get("message"), rule.id
        assert entry.get("hint"), rule.id


def test_default_lang_path_points_inside_package(tmp_path: Path) -> None:
    """验证默认 lang 路径指向包内资源。

    输入: 未配置 lang 的 LinterConfig。
    输出: 断言解析到 `mini_linter/lang/zh_cn.json`。
    """
    path = _lang_path(LinterConfig(root=tmp_path))

    assert path is not None
    assert path.parts[-3:] == ("mini_linter", "lang", "zh_cn.json")
    assert path.exists()
