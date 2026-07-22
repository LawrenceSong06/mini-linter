"""
上次修改时间: 2026-07-14-22:55
上次修改内容: Restore UTF-8 file header metadata
上次修改者: Agent Joe
文件设计: Lint orchestration core
文件功能: Discover files, run rules, and aggregate results.
文件创建者: Agent Joe
"""

from __future__ import annotations

import ast
import fnmatch
from pathlib import Path

from mini_linter.config import LinterConfig
from mini_linter.lang import LangCatalog
from mini_linter.models import LintResult, Rule, RuleContext, Violation
from mini_linter.plugins import load_plugin_rules
from mini_linter.rules import built_in_rules

def run_linter(config: LinterConfig, paths: tuple[str, ...] = (), lang: LangCatalog | None = None) -> LintResult:
    """执行一次 lint 检查。

    输入: LinterConfig、可选扫描路径和可选 lang catalog。
    输出: 聚合后的 LintResult。
    """

    files = tuple(_discover_python_files(config, paths or config.paths))
    catalog = lang or LangCatalog.load(_lang_path(config))
    rules = _enabled_rules([*built_in_rules(), *load_plugin_rules(config.root, config.plugins)], config)
    violations: list[Violation] = []

    # 项目级规则只需要根目录和文件列表，不绑定具体源码文件。
    project_context = RuleContext(
        root=config.root,
        path=config.root,
        source="",
        tree=None,
        config=config,
        files=files,
        is_project=True,
    )

    for rule in rules:
        violations.extend(rule.check(project_context))

    for file_path in files:
        source = file_path.read_text(encoding="utf-8")
        tree = _parse_python(source)
        context = RuleContext(config.root, file_path, source, tree, config, files)

        for rule in rules:
            violations.extend(rule.check(context))

    rendered = tuple(catalog.apply(item) for item in violations)

    return LintResult(violations=rendered, fail_on=config.fail_on)


def _enabled_rules(rules: list[Rule], config: LinterConfig) -> list[Rule]:
    """过滤被配置禁用的规则。

    输入: 规则列表和配置。
    输出: 仍需执行的规则列表。
    """
    return [rule for rule in rules if config.rule_enabled(rule.id)]


def _discover_python_files(config: LinterConfig, paths: tuple[str, ...]) -> list[Path]:
    """发现需要扫描的 Python 文件。

    输入: 配置和扫描路径。
    输出: 去重、排序后的 `.py` 文件列表。
    """
    files: list[Path] = []

    for entry in paths:
        path = (config.root / entry).resolve()

        if path.is_file() and path.suffix == ".py" and not _excluded(config, path):
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*.py"):
                if not _excluded(config, child):
                    files.append(child)

    return sorted(set(files))


def _excluded(config: LinterConfig, path: Path) -> bool:
    """判断路径是否被排除。

    输入: 配置和候选路径。
    输出: 匹配 exclude 路径模式时返回 True。
    """
    relative = path.relative_to(config.root).as_posix()
    
    return any(_matches_exclude_pattern(relative, pattern) for pattern in config.exclude)


def _matches_exclude_pattern(relative: str, pattern: str) -> bool:
    """判断相对路径是否匹配 exclude 模式。

    输入: POSIX 相对路径和路径模式。
    输出: 匹配时返回 True；`**/name/**` 同时支持根目录下的 `name/**`。
    """

    if fnmatch.fnmatch(relative, pattern):
        return True

    if pattern.startswith("**/") and fnmatch.fnmatch(relative, pattern[3:]):
        return True
    else:
        # else 条件: 当前模式不是根目录兼容模式，或根目录兼容匹配失败。
        return False


def _parse_python(source: str) -> ast.AST | None:
    """解析 Python 源码。

    输入: 源码字符串。
    输出: AST；语法错误时返回 None，让依赖 AST 的规则自行跳过。
    """
    try:
        return ast.parse(source)
    except SyntaxError:
        return None


def _lang_path(config: LinterConfig) -> Path | None:
    """解析 lang 文件路径。

    输入: LinterConfig。
    输出: 绝对路径；未配置 lang 时返回 None。
    """
    if not config.lang:
        return Path(__file__).resolve().parent / "lang" / "zh_cn.json"
    configured = Path(config.lang)
    if configured.parts == ("lang", "zh_cn.json") or config.lang == "zh_cn.json":
        return Path(__file__).resolve().parent / "lang" / "zh_cn.json"
    return (config.root / configured).resolve()
