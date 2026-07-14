"""上次修改: 2026-07-14; 设计: 配置读取层; 功能: 从 pyproject.toml 构造 linter 配置。"""

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
    exclude: tuple[str, ...] = (".git", "__pycache__", ".pytest_cache", "build", "dist")
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
    """加载 pyproject.toml 中的 mini-linter 配置。

    输入: 可选配置路径和项目根目录。
    输出: LinterConfig；配置文件不存在时返回默认配置。
    """
    project_root = (root or Path.cwd()).resolve()
    path = (config_path or project_root / "pyproject.toml").resolve()
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
