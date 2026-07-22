"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Add project init template writer
上次修改者: Agent Joe
文件设计: Init template generation
文件功能: Create default config, lang files, plugin example, and README for target projects.
文件创建者: Agent Joe
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InitResult:
    """保存 init 命令执行结果。

    输入: ok、message 和生成文件路径。
    输出: CLI 根据该对象决定退出码和展示内容。
    """

    ok: bool
    message: str
    files: tuple[Path, ...] = ()


def create_init_template(root: Path, force: bool = False) -> InitResult:
    """在项目根目录创建 mini-linter 模板。

    输入: 项目根目录和是否覆盖已知模板文件。
    输出: InitResult，包含执行状态和生成文件。
    """

    project_root = root.resolve()
    known_files = _known_template_files(project_root)
    blocking_paths = _existing_template_paths(project_root, known_files)

    if blocking_paths and not force:
        names = ", ".join(path.relative_to(project_root).as_posix() for path in blocking_paths)
        return InitResult(False, f"Init template already exists: {names}. Use --force to overwrite known template files.")

    for directory in (project_root / "linter" / "lang", project_root / "linter" / "plugins"):
        directory.mkdir(parents=True, exist_ok=True)

    _write_text(project_root / "linter_config.toml", _config_template())
    _write_text(project_root / "linter" / "lang" / "zh_cn.json", _lang_template("zh_cn"))
    _write_text(project_root / "linter" / "lang" / "en_us.json", _lang_template("en_us"))
    _write_text(project_root / "linter" / "plugins" / "example.py", _plugin_template())
    _write_text(project_root / "mini-linter_README.md", _readme_template())

    return InitResult(True, "Created mini-linter init template.", known_files)


def _known_template_files(root: Path) -> tuple[Path, ...]:
    """返回 init 会创建或覆盖的已知文件。

    输入: 项目根目录。
    输出: 已知模板文件路径元组。
    """

    return (
        root / "linter_config.toml",
        root / "linter" / "lang" / "zh_cn.json",
        root / "linter" / "lang" / "en_us.json",
        root / "linter" / "plugins" / "example.py",
        root / "mini-linter_README.md",
    )


def _existing_template_paths(root: Path, known_files: tuple[Path, ...]) -> tuple[Path, ...]:
    """收集阻止默认 init 的已有路径。

    输入: 项目根目录和已知模板文件。
    输出: 已存在的阻塞路径；包含 `linter` 目录本身。
    """

    paths = [root / "linter", *known_files]
    return tuple(path for path in paths if path.exists())


def _write_text(path: Path, content: str) -> None:
    """写入 UTF-8 文本文件。

    输入: 目标路径和文本内容。
    输出: 无。
    """

    path.write_text(content, encoding="utf-8")


def _config_template() -> str:
    """返回默认 linter_config.toml 模板。

    输入: 无。
    输出: TOML 配置文本。
    """

    return """[tool.mini_linter]
paths = ["."]
exclude = ["**/.git/**", "**/__pycache__/**", "**/.pytest_cache/**", "**/build/**", "**/dist/**", "**/.venv/**", "**/linter/**"]
lang = "linter/lang/zh_cn.json"
plugins = ["linter/plugins/example.py"]
fail_on = "error"

[tool.mini_linter.rules."style.file_too_long"]
enabled = true
max_lines = 300

[tool.mini_linter.rules."style.function_too_long"]
enabled = true
max_lines = 50

[tool.mini_linter.rules."style.test_file_naming"]
enabled = true

[tool.mini_linter.rules."imports.forbidden"]
enabled = true
modules = []

[tool.mini_linter.rules."architecture.layers"]
enabled = true

[tool.mini_linter.rules."agent.agents_guide_exists"]
enabled = true

[tool.mini_linter.rules."agent.templates_exist"]
enabled = true

[tool.mini_linter.rules."plugin.hello_world"]
enabled = true
"""


def _lang_template(locale: str) -> str:
    """返回默认 lang JSON 模板。

    输入: locale，支持 zh_cn 和 en_us。
    输出: JSON 文本。
    """

    if locale == "en_us":
        entries = _en_us_entries()
    else:
        # else 条件: 非英文 locale 使用中文模板。
        entries = _zh_cn_entries()

    return json.dumps(entries, indent=2, ensure_ascii=False) + "\n"


def _zh_cn_entries() -> dict[str, dict[str, str]]:
    """返回中文规则文案。

    输入: 无。
    输出: 按 rule id 索引的 message 和 hint。
    """

    return {
        "style.file_too_long": {
            "message": "文件共有 {line_count} 行，超过限制 {max_lines} 行。",
            "hint": "将该文件拆分为职责更清晰的小模块，降低单个文件的阅读和维护成本。",
        },
        "style.function_too_long": {
            "message": "函数 `{name}` 共有 {line_count} 行，超过限制 {max_lines} 行。",
            "hint": "提取小的辅助函数，让控制流更清晰。",
        },
        "style.test_file_naming": {
            "message": "测试文件 `{filename}` 不符合命名约定。",
            "hint": "将测试文件命名为 `test_*.py`。",
        },
        "imports.forbidden": {
            "message": "禁止 import `{module}`。",
            "hint": "移除该依赖，或将相关能力移动到允许依赖该模块的边界层中。",
        },
        "architecture.layers": {
            "message": "层 `{source_layer}` 不能通过 `{module}` import 层 `{target_layer}`。",
            "hint": "将共享逻辑移动到允许依赖的层，或有意识地更新架构层级配置。",
        },
        "agent.agents_guide_exists": {
            "message": "缺少 `AGENTS.md`。",
            "hint": "添加 `AGENTS.md`，说明项目目标、代码风格、测试要求和 Agent 工作流程。",
        },
        "agent.templates_exist": {
            "message": "缺少 Agent 模板 `{template}`。",
            "hint": "创建缺失的 `.agents/` 文件，帮助后续 Agent 理解上下文并完成 review。",
        },
        "plugin.hello_world": {
            "message": "文件 `{filename}` 中缺少 `hello world!`。",
            "hint": "添加精确字符串 `hello world!`，或在配置中禁用 `plugin.hello_world` 示例规则。",
        },
    }


def _en_us_entries() -> dict[str, dict[str, str]]:
    """返回英文规则文案。

    输入: 无。
    输出: 按 rule id 索引的 message 和 hint。
    """

    return {
        "style.file_too_long": {
            "message": "This file has {line_count} lines, exceeding the limit of {max_lines} lines.",
            "hint": "Split this file into smaller modules with clearer responsibilities to reduce reading and maintenance cost.",
        },
        "style.function_too_long": {
            "message": "Function `{name}` has {line_count} lines, exceeding the limit of {max_lines} lines.",
            "hint": "Extract small helper functions to make the control flow clearer.",
        },
        "style.test_file_naming": {
            "message": "Test file `{filename}` does not follow the naming convention.",
            "hint": "Name test files as `test_*.py`.",
        },
        "imports.forbidden": {
            "message": "Importing `{module}` is forbidden.",
            "hint": "Remove this dependency, or move the related capability into a boundary layer that is allowed to depend on this module.",
        },
        "architecture.layers": {
            "message": "Layer `{source_layer}` cannot import layer `{target_layer}` through `{module}`.",
            "hint": "Move shared logic to a layer that is allowed to be imported, or intentionally update the architecture layer configuration.",
        },
        "agent.agents_guide_exists": {
            "message": "`AGENTS.md` is missing.",
            "hint": "Add `AGENTS.md` to describe the project goals, code style, testing requirements, and Agent workflow.",
        },
        "agent.templates_exist": {
            "message": "Agent template `{template}` is missing.",
            "hint": "Create the missing `.agents/` file to help future Agents understand the context and complete reviews.",
        },
        "plugin.hello_world": {
            "message": "File `{filename}` is missing `hello world!`.",
            "hint": "Add the exact string `hello world!`, or disable the `plugin.hello_world` example rule in the config.",
        },
    }


def _plugin_template() -> str:
    """返回示例插件模板。

    输入: 无。
    输出: Python 插件源码文本。
    """

    return '''"""
上次修改时间: 2026-07-22-00:00
上次修改内容: Create hello world example plugin
上次修改者: mini-linter init
文件设计: Example plugin rule
文件功能: Check whether each Python file contains hello world text.
文件创建者: mini-linter init
"""

from __future__ import annotations

from mini_linter.models import RuleContext, Violation
from mini_linter.rules.base import BaseRule


class HelloWorldRule(BaseRule):
    """检查 Python 文件是否包含 hello world 示例文本。

    输入: RuleContext。
    输出: 缺少 `hello world!` 时返回 error violation。
    """

    id = "plugin.hello_world"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行 hello world 示例检查。

        输入: 当前文件上下文。
        输出: 缺少精确字符串时返回 violation 列表。
        """
        if context.is_project or context.path.suffix != ".py":
            return []

        if "hello world!" in context.source:
            return []

        return [self.violation(context, details={"filename": context.path.name})]
'''


def _readme_template() -> str:
    """返回 init 生成的中文 README 模板。

    输入: 无。
    输出: Markdown 文本。
    """

    return """# mini-linter 初始化说明

您好，感谢您使用 `mini-linter`。这个文件由 `mini-linter init` 自动生成，用于说明本项目中新增的 lint 配置模板，以及后续如何运行和调整它。

## init 创建了什么

`mini-linter init` 会在项目根目录创建以下内容：

- `linter_config.toml`：mini-linter 的配置文件，需要保留在项目根目录。
- `linter/lang/zh_cn.json`：中文规则输出文案。
- `linter/lang/en_us.json`：英文规则输出文案。
- `linter/plugins/example.py`：本地插件规则示例。
- `mini-linter_README.md`：当前说明文件。

## 如何运行

在项目根目录运行：

```powershell
mini-linter check .
```

不传 `--config` 时，`mini-linter` 会优先读取根目录下的 `linter_config.toml`。如果您想显式指定配置文件，也可以运行：

```powershell
mini-linter check . --config linter_config.toml
```

## 示例插件说明

默认生成的 `linter/plugins/example.py` 包含一个示例规则：`plugin.hello_world`。它会逐个检查 Python 文件，如果文件中没有精确字符串 `hello world!`，就输出 error。

这个规则主要用于演示如何编写插件。正式使用时，您可以：

- 在 Python 文件中加入 `hello world!` 让示例规则通过。
- 修改 `linter/plugins/example.py`，改成自己的项目规则。
- 在 `linter_config.toml` 中将 `plugin.hello_world` 的 `enabled` 改为 `false`。

## 如何调整配置

请编辑项目根目录的 `linter_config.toml`。常见调整包括：

- 修改 `paths` 来决定检查哪些目录。
- 修改 `exclude` 来排除虚拟环境、构建产物或生成文件。排除文件夹时请写成 `**/文件夹/**`，例如 `**/.venv/**`，不要只写 `.venv`。
- 修改 `lang` 来切换中文或英文输出文案。
- 修改 `plugins` 来添加或移除本地插件文件。
- 修改 `[tool.mini_linter.rules]` 下的规则配置。

## 更多文档

您可以在 GitHub 仓库阅读完整文档：

- mini-linter 仓库：https://github.com/LawrenceSong06/mini-linter
- 用户指南：https://github.com/LawrenceSong06/mini-linter/blob/main/docs/user-guide.md
- 插件规则指南：https://github.com/LawrenceSong06/mini-linter/blob/main/docs/plugins.md
"""
