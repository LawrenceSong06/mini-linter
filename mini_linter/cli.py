"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Add init command for project templates
上次修改者: Agent Joe
文件设计: CLI entry
文件功能: Parse check command and print JSON result.
文件创建者: Agent Joe
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mini_linter import __version__
from mini_linter.config import load_config
from mini_linter.core import run_linter
from mini_linter.init_templates import create_init_template
from mini_linter.lang import LangCatalog
from mini_linter.models import Severity


def main(argv: list[str] | None = None) -> int:
    """运行 mini-linter CLI。

    输入: 可选 argv；为空时使用进程参数。
    输出: 进程退出码，0 表示通过，1 表示 lint 失败，2 表示命令错误。
    """

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        return _run_init(args)

    if args.command != "check":
        parser.print_help()
        return 2

    if args.config:
        config_path = Path(args.config)
    else:
        # else 条件: 用户没有显式传入 --config，使用默认配置文件查找逻辑。
        config_path = None

    config = load_config(config_path)
    fail_on: Severity = args.fail_on or config.fail_on
    config = config.__class__(
        root=config.root,
        paths=config.paths,
        exclude=config.exclude,
        lang=config.lang,
        plugins=config.plugins,
        fail_on=fail_on,
        rules=config.rules,
        architecture=config.architecture,
    )
    
    if args.lang:
        lang = LangCatalog.load(Path(args.lang).resolve())
    else:
        # else 条件: 用户没有显式传入 --lang，由 core 根据配置加载 lang。
        lang = None
        
    result = run_linter(config, tuple(args.paths), lang)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=False, ensure_ascii=False))

    if result.ok:
        return 0
    else:
        # else 条件: lint 结果未通过 fail_on 阈值，返回失败退出码。
        return 1


def _run_init(args: argparse.Namespace) -> int:
    """执行 init 子命令。

    输入: argparse 解析结果。
    输出: 0 表示创建成功，1 表示模板已存在。
    """

    result = create_init_template(Path.cwd(), force=args.force)
    print(result.message)

    if result.ok:
        for path in result.files:
            print(path.relative_to(Path.cwd()).as_posix())
        return 0
    else:
        # else 条件: init 默认拒绝覆盖已有模板。
        return 1


def _build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。

    输入: 无。
    输出: 支持 `init` 和 `check` 子命令的 ArgumentParser。
    """

    parser = argparse.ArgumentParser(
        prog="mini-linter",
        description="Check Python style, imports, architecture boundaries, and agent collaboration files.",
    )
    parser.add_argument("--version", action="version", version=f"mini-linter {__version__}")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    init = subparsers.add_parser(
        "init",
        help="Create a default linter_config.toml and linter template files.",
        description="Create mini-linter config, lang files, plugin example, and project README templates.",
    )
    init.add_argument("--force", action="store_true", help="Overwrite known mini-linter template files.")

    check = subparsers.add_parser(
        "check",
        help="Run lint checks and print a JSON result.",
        description="Scan given paths or configured paths, then run built-in and local plugin rules.",
    )
    check.add_argument("paths", nargs="*", help="Files or directories to check; defaults to configured paths.")
    check.add_argument("--config", help="Path to a linter_config.toml or pyproject.toml config file.")
    check.add_argument("--lang", help="Path to a lang JSON file that provides violation message and hint text.")
    check.add_argument("--format", choices=["json"], default="json", help="Output format; currently only json.")
    check.add_argument(
        "--fail-on",
        choices=["error", "warning", "info"],
        help="Failure threshold; this severity or higher returns exit code 1.",
    )
    
    return parser


if __name__ == "__main__":
    sys.exit(main())
