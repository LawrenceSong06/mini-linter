"""
上次修改时间: 2026-07-14-22:55
上次修改内容: Restore UTF-8 file header metadata
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

from mini_linter.config import load_config
from mini_linter.core import run_linter
from mini_linter.lang import LangCatalog
from mini_linter.models import Severity


def main(argv: list[str] | None = None) -> int:
    """运行 mini-linter CLI。

    输入: 可选 argv；为空时使用进程参数。
    输出: 进程退出码，0 表示通过，1 表示 lint 失败，2 表示命令错误。
    """

    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "check":
        parser.print_help()
        return 2

    if args.config:
        config_path = Path(args.config)
    else:
        # else 条件: 用户没有显式传入 --config，使用默认 pyproject.toml 查找逻辑。
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


def _build_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器。

    输入: 无。
    输出: 支持 `check` 子命令的 ArgumentParser。
    """

    parser = argparse.ArgumentParser(
        prog="mini-linter",
        description="Check Python style, imports, architecture boundaries, and agent collaboration files.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    check = subparsers.add_parser(
        "check",
        help="Run lint checks and print a JSON result.",
        description="Scan given paths or configured paths, then run built-in and local plugin rules.",
    )
    check.add_argument("paths", nargs="*", help="Files or directories to check; defaults to configured paths.")
    check.add_argument("--config", help="Path to a pyproject.toml config file.")
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
