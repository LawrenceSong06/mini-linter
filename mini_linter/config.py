"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Prefer linter_config.toml as default config
上次修改者: Agent Joe
文件设计: Configuration reader
文件功能: Build linter configuration from linter_config.toml or pyproject.toml.
文件创建者: Agent Joe
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mini_linter.models import Severity

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - covered on Python <3.11
    import tomli as tomllib


@dataclass(frozen=True)
class LinterConfig:
    """保存 mini-linter 的运行配置。

    输入: 项目根目录、扫描路径、规则配置、插件和架构配置。
    输出: 提供规则启用状态和规则参数查询。
    """

    root: Path
    paths: tuple[str, ...] = (".",)
    exclude: tuple[str, ...] = (
        "**/.git/**",
        "**/__pycache__/**",
        "**/.pytest_cache/**",
        "**/build/**",
        "**/dist/**",
        "**/.venv/**",
    )
    lang: str | None = None
    plugins: tuple[str, ...] = ()
    fail_on: Severity = "error"
    rules: dict[str, dict[str, Any]] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)

    def rule_enabled(self, rule_id: str) -> bool:
        """判断规则是否启用。

        输入: rule_id。
        输出: 未配置时默认返回 True。
        """
        return bool(self.rules.get(rule_id, {}).get("enabled", True))

    def rule_options(self, rule_id: str) -> dict[str, Any]:
        """读取某条规则的配置项。

        输入: rule_id。
        输出: 规则配置字典；未配置时返回空字典。
        """
        return self.rules.get(rule_id, {})


def load_config(config_path: Path | None = None, root: Path | None = None) -> LinterConfig:
    """加载 TOML 文件中的 mini-linter 配置。

    输入: 可选配置路径和项目根目录。
    输出: LinterConfig；配置文件不存在时返回默认配置。
    """
    
    project_root = (root or Path.cwd()).resolve()
    path = _default_config_path(project_root) if config_path is None else config_path.resolve()
    if not path.exists():
        return LinterConfig(root=project_root)

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    tool_data = data.get("tool", {}).get("mini_linter", {})
    if config_path is not None:
        project_root = path.parent

    fail_on = tool_data.get("fail_on", "error")
    if fail_on not in {"error", "warning", "info"}:
        fail_on = "error"

    return LinterConfig(
        root=project_root,
        paths=tuple(tool_data.get("paths", ["."])),
        exclude=tuple(tool_data.get("exclude", LinterConfig.exclude)),
        lang=tool_data.get("lang"),
        plugins=tuple(tool_data.get("plugins", [])),
        fail_on=fail_on,
        rules=dict(tool_data.get("rules", {})),
        architecture=dict(tool_data.get("architecture", {})),
    )


def _default_config_path(project_root: Path) -> Path:
    """返回默认配置文件路径。

    输入: 项目根目录。
    输出: 优先返回 `linter_config.toml`，否则兼容 `pyproject.toml`。
    """

    linter_config = project_root / "linter_config.toml"
    if linter_config.exists():
        return linter_config.resolve()
    else:
        # else 条件: 新配置文件不存在，继续兼容旧 pyproject.toml 配置。
        return (project_root / "pyproject.toml").resolve()
