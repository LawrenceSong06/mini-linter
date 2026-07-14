"""上次修改: 2026-07-14; 设计: lang 测试; 功能: 验证文案覆盖和默认 fallback。"""

from pathlib import Path

from mini_linter.lang import LangCatalog
from mini_linter.models import Violation


def test_lang_catalog_overrides_message_and_hint(tmp_path: Path) -> None:
    """验证 lang JSON 覆盖 message 和 hint。

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


def test_lang_catalog_keeps_default_text_when_rule_missing(tmp_path: Path) -> None:
    """验证没有 lang 条目时保留默认文案。

    输入: 不存在的 lang 路径和 violation。
    输出: 断言默认 message 和 hint 不变。
    """
    violation = Violation("demo.rule", "warning", "x.py", 1, 1, "Default", "Default hint", {})
    rendered = LangCatalog.load(tmp_path / "missing.json").apply(violation)
    assert rendered.message == "Default"
    assert rendered.hint == "Default hint"
