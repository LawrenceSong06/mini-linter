"""上次修改: 2026-07-14; 设计: 配置测试; 功能: 验证 pyproject.toml 解析和默认回退。"""

from pathlib import Path

from mini_linter.config import load_config


def test_loads_pyproject_mini_linter_config(tmp_path: Path) -> None:
    """验证能从 pyproject.toml 读取 mini-linter 配置。

    输入: 临时 pyproject.toml。
    输出: 断言路径、插件、lang、fail_on 和规则参数。
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.mini_linter]
paths = ["src"]
exclude = ["build"]
lang = "lang/custom.json"
plugins = ["rules.py"]
fail_on = "warning"

[tool.mini_linter.rules."style.file_too_long"]
enabled = true
max_lines = 10
""",
        encoding="utf-8",
    )

    config = load_config(pyproject)

    assert config.root == tmp_path
    assert config.paths == ("src",)
    assert config.exclude == ("build",)
    assert config.lang == "lang/custom.json"
    assert config.plugins == ("rules.py",)
    assert config.fail_on == "warning"
    assert config.rule_options("style.file_too_long")["max_lines"] == 10


def test_invalid_fail_on_falls_back_to_error(tmp_path: Path) -> None:
    """验证非法 fail_on 回退到 error。

    输入: 包含非法 fail_on 的配置。
    输出: 断言配置对象使用 error。
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.mini_linter]\nfail_on = \"fatal\"\n", encoding="utf-8")

    assert load_config(pyproject).fail_on == "error"


def test_project_default_lang_is_chinese() -> None:
    """验证项目默认配置使用中文 lang 文件。

    输入: 仓库根目录的 `pyproject.toml`。
    输出: 断言默认 lang 名称为 `zh_cn.json`。
    """

    root = Path(__file__).resolve().parents[1]
    config = load_config(root / "pyproject.toml")
    
    assert config.lang == "zh_cn.json"
