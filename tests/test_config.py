"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Cover linter_config.toml default loading
上次修改者: Agent Joe
文件设计: Configuration tests
文件功能: Verify pyproject parsing and defaults.
文件创建者: Agent Joe
"""

from pathlib import Path

from mini_linter import __version__
from mini_linter.config import tomllib
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


def test_project_version_matches_package_version() -> None:
    """验证 pyproject 包版本和运行时版本一致。

    输入: 仓库根目录的 `pyproject.toml` 和包内 `__version__`。
    输出: 断言 pip 读取的项目版本与 CLI 使用的版本一致。
    """

    root = Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert data["project"]["version"] == __version__


def test_default_config_prefers_linter_config(tmp_path: Path, monkeypatch) -> None:
    """验证默认配置优先读取 linter_config.toml。

    输入: 同时包含 linter_config.toml 和 pyproject.toml 的目录。
    输出: 断言读取 linter_config.toml 中的配置。
    """

    monkeypatch.chdir(tmp_path)
    (tmp_path / "linter_config.toml").write_text(
        """
[tool.mini_linter]
paths = ["src"]
lang = "linter/lang/zh_cn.json"
""",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.mini_linter]
paths = ["tests"]
lang = "zh_cn.json"
""",
        encoding="utf-8",
    )

    config = load_config()

    assert config.paths == ("src",)
    assert config.lang == "linter/lang/zh_cn.json"


def test_default_config_falls_back_to_pyproject(tmp_path: Path, monkeypatch) -> None:
    """验证没有 linter_config.toml 时兼容 pyproject.toml。

    输入: 只有 pyproject.toml 的目录。
    输出: 断言读取旧配置文件。
    """

    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.mini_linter]
paths = ["legacy"]
""",
        encoding="utf-8",
    )

    assert load_config().paths == ("legacy",)
