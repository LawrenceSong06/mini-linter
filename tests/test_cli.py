"""上次修改: 2026-07-14; 设计: CLI 测试; 功能: 验证 JSON 输出、退出码和 lang 参数。"""

import json
from pathlib import Path

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
        '{"imports.forbidden": {"message": "No {module}", "hint": "Remove {module}"}}',
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
    输出: 断言 message 和 hint 由 lang JSON 提供。
    """

    (tmp_path / "bad.py").write_text("import os\n", encoding="utf-8")

    lang = tmp_path / "lang.json"
    lang.write_text(
        '{"imports.forbidden": {"message": "No {module}", "hint": "Remove {module}"}}',
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
