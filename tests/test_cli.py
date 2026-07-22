"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Cover init command behavior
上次修改者: Agent Joe
文件设计: CLI tests
文件功能: Verify JSON output, exit codes, help, and lang behavior.
文件创建者: Agent Joe
"""

import json
from pathlib import Path

from mini_linter import __version__
from mini_linter.cli import main


def test_cli_outputs_json_and_exit_code(tmp_path: Path, capsys) -> None:
    """验证 CLI 在发现 error 时输出 JSON 并返回失败码。

    输入: 临时项目、禁止 import 配置和 pytest capsys。
    输出: 断言退出码和 JSON violation 内容。
    """
    (tmp_path / "AGENTS.md").write_text("guide", encoding="utf-8")
    agents = tmp_path / ".agents"
    agents.mkdir()

    for name in ["context.md", "rule-authoring.md", "review-checklist.md", "task-template.md"]:
        (agents / name).write_text("doc", encoding="utf-8")
        
    (tmp_path / "bad.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / "lang.json").write_text(
        '{"imports.forbidden": {"severity": "error", "message": "No {module}", "hint": "Remove {module}"}}',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.mini_linter]
paths = ["bad.py"]
lang = "lang.json"
fail_on = "error"

[tool.mini_linter.rules."imports.forbidden"]
modules = ["os"]

[tool.mini_linter.rules."style.comments.file_header_required"]
enabled = false

[tool.mini_linter.rules."style.comments.public_docstring_required"]
enabled = false

[tool.mini_linter.rules."style.comments.code_block_comment_required"]
enabled = false
""",
        encoding="utf-8",
    )

    exit_code = main(["check", "--config", str(tmp_path / "pyproject.toml")])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert output["ok"] is False
    assert output["violations"][0]["rule_id"] == "imports.forbidden"


def test_cli_accepts_custom_lang(tmp_path: Path, capsys) -> None:
    """验证 CLI 可以使用自定义 lang JSON。

    输入: 临时项目、lang 文件和配置文件。
    输出: 断言 severity、message 和 hint 由 lang JSON 提供。
    """

    (tmp_path / "bad.py").write_text("import os\n", encoding="utf-8")

    lang = tmp_path / "lang.json"
    lang.write_text(
        '{"imports.forbidden": {"severity": "error", "message": "No {module}", "hint": "Remove {module}"}}',
        encoding="utf-8",
    )

    config = tmp_path / "pyproject.toml"
    config.write_text(
        """
[tool.mini_linter]
paths = ["bad.py"]
fail_on = "error"

[tool.mini_linter.rules."imports.forbidden"]
modules = ["os"]

[tool.mini_linter.rules."agent.agents_guide_exists"]
enabled = false

[tool.mini_linter.rules."agent.templates_exist"]
enabled = false

[tool.mini_linter.rules."style.comments.file_header_required"]
enabled = false

[tool.mini_linter.rules."style.comments.public_docstring_required"]
enabled = false

[tool.mini_linter.rules."style.comments.code_block_comment_required"]
enabled = false
""",
        encoding="utf-8",
    )

    main(["check", "--config", str(config), "--lang", str(lang)])
    
    output = json.loads(capsys.readouterr().out)

    assert output["violations"][0]["message"] == "No os"
    assert output["violations"][0]["hint"] == "Remove os"


def test_cli_help_outputs_usage(capsys) -> None:
    """验证顶层 `-h` 会输出帮助信息。

    输入: `-h` 参数和 pytest capsys。
    输出: 断言 argparse 以 0 退出并包含 check 子命令。
    """

    try:
        main(["-h"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out

    assert "usage: mini-linter" in output
    assert "check" in output
    assert "init" in output
    assert "--version" in output


def test_cli_version_outputs_package_version(capsys) -> None:
    """验证顶层 `--version` 输出包版本。

    输入: `--version` 参数和 pytest capsys。
    输出: 断言 argparse 以 0 退出并包含当前包版本。
    """

    try:
        main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out

    assert output.strip() == f"mini-linter {__version__}"


def test_cli_check_help_outputs_arguments(capsys) -> None:
    """验证 `check -h` 会输出子命令参数说明。

    输入: `check -h` 参数和 pytest capsys。
    输出: 断言 argparse 以 0 退出并包含关键参数。
    """
    
    try:
        main(["check", "-h"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out
    assert "--config" in output
    assert "--fail-on" in output


def test_cli_init_creates_template_files(tmp_path: Path, monkeypatch, capsys) -> None:
    """验证 init 会在项目根目录创建模板文件。

    输入: 临时项目目录和 pytest monkeypatch。
    输出: 断言 init 退出码、输出和生成文件。
    """

    monkeypatch.chdir(tmp_path)

    exit_code = main(["init"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Created mini-linter init template." in output
    assert (tmp_path / "linter_config.toml").exists()
    assert (tmp_path / "linter" / "lang" / "zh_cn.json").exists()
    assert (tmp_path / "linter" / "lang" / "en_us.json").exists()
    assert (tmp_path / "linter" / "plugins" / "example.py").exists()
    assert (tmp_path / "mini-linter_README.md").exists()
    assert "您好" in (tmp_path / "mini-linter_README.md").read_text(encoding="utf-8")
    assert "style.comments.file_header_required" in (tmp_path / "linter_config.toml").read_text(encoding="utf-8")
    zh_lang = json.loads((tmp_path / "linter" / "lang" / "zh_cn.json").read_text(encoding="utf-8"))
    en_lang = json.loads((tmp_path / "linter" / "lang" / "en_us.json").read_text(encoding="utf-8"))

    for catalog in (zh_lang, en_lang):
        for rule_id, entry in catalog.items():
            assert entry.get("severity") in {"error", "warning", "info"}, rule_id
            assert entry.get("message"), rule_id
            assert entry.get("hint"), rule_id


def test_cli_init_refuses_existing_template_by_default(tmp_path: Path, monkeypatch, capsys) -> None:
    """验证 init 默认拒绝覆盖已有模板。

    输入: 已存在 linter_config.toml 的临时项目。
    输出: 断言退出码为 1 且文件未被覆盖。
    """

    monkeypatch.chdir(tmp_path)
    (tmp_path / "linter_config.toml").write_text("existing", encoding="utf-8")

    exit_code = main(["init"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "Use --force" in output
    assert (tmp_path / "linter_config.toml").read_text(encoding="utf-8") == "existing"


def test_cli_init_force_overwrites_known_template_files(tmp_path: Path, monkeypatch, capsys) -> None:
    """验证 init --force 会覆盖已知模板文件。

    输入: 已存在模板文件的临时项目。
    输出: 断言文件内容被替换为默认模板。
    """

    monkeypatch.chdir(tmp_path)
    (tmp_path / "linter_config.toml").write_text("existing", encoding="utf-8")

    exit_code = main(["init", "--force"])
    capsys.readouterr()

    assert exit_code == 0
    assert "[tool.mini_linter]" in (tmp_path / "linter_config.toml").read_text(encoding="utf-8")


def test_cli_init_help_outputs_force(capsys) -> None:
    """验证 init -h 会输出 force 参数。

    输入: `init -h` 参数和 pytest capsys。
    输出: 断言 argparse 以 0 退出并包含 --force。
    """

    try:
        main(["init", "-h"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out

    assert "--force" in output
