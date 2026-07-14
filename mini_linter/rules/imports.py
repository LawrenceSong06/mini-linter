"""上次修改: 2026-07-14; 设计: import 和架构规则; 功能: 检查禁用依赖和层级边界。"""

from __future__ import annotations

import ast
import fnmatch
from pathlib import Path

from mini_linter.models import RuleContext, Violation
from mini_linter.rules.base import BaseRule


class ForbiddenImportRule(BaseRule):
    """检查源码中是否 import 了禁止模块。

    输入: RuleContext，读取 `modules` 规则配置。
    输出: 每个禁止 import 对应一个 violation。
    """

    id = "imports.forbidden"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行禁用 import 检查。

        输入: 当前文件上下文。
        输出: 禁用 import violation 列表。
        """
        if context.is_project or context.tree is None:
            return []
        
        modules = set(context.config.rule_options(self.id).get("modules", []))
        if not modules:
            return []
        
        violations: list[Violation] = []
        for node in ast.walk(context.tree):
            imported = _imported_module(node)
            if imported and _matches_forbidden(imported, modules):
                violations.append(
                    self.violation(
                        context,
                        line=getattr(node, "lineno", 1),
                        column=getattr(node, "col_offset", 0) + 1,
                        details={"module": imported},
                    )
                )
        return violations


class LayerImportBoundaryRule(BaseRule):
    """检查文件所属层级是否 import 了不允许的层级。

    输入: RuleContext 和 architecture.layers 配置。
    输出: 违反层级边界的 import violation 列表。
    """

    id = "architecture.layers"
    default_severity = "error"

    def check(self, context: RuleContext) -> list[Violation]:
        """执行层级 import 边界检查。

        输入: 当前文件上下文。
        输出: 跨层违规 import violation 列表。
        """
        if context.is_project or context.tree is None:
            return []
        
        layers = list(context.config.architecture.get("layers", []))
        if not layers:
            return []
        
        source_layer = _layer_for_path(context.root, context.path, layers)
        if source_layer is None:
            return []
        
        allowed = set(source_layer.get("may_import", [])) | {source_layer["name"]}
        violations: list[Violation] = []

        for node in ast.walk(context.tree):
            module = _imported_module(node)

            if not module:
                continue
            # 没有被 continue 的情况: 当前 AST 节点是可解析的 import。

            target_path = _module_to_path(context.root, module, context.files)

            if target_path is None:
                continue
            # 没有被 continue 的情况: import 指向项目内可定位的 Python 文件。

            target_layer = _layer_for_path(context.root, target_path, layers)
            if target_layer is None or target_layer["name"] in allowed:
                continue
            # 没有被 continue 的情况: 目标层存在，且不在当前层允许 import 的集合中。
            violations.append(
                self.violation(
                    context,
                    line=getattr(node, "lineno", 1),
                    column=getattr(node, "col_offset", 0) + 1,
                    details={
                        "source_layer": source_layer["name"],
                        "target_layer": target_layer["name"],
                        "module": module,
                    },
                )
            )
        return violations


def _imported_module(node: ast.AST) -> str | None:
    """从 AST import 节点提取模块名。

    输入: AST 节点。
    输出: 模块名；非 import 节点返回 None。
    """
    if isinstance(node, ast.Import) and node.names:
        return node.names[0].name
    if isinstance(node, ast.ImportFrom):
        if node.level:
            return "." * node.level + (node.module or "")
        return node.module
    return None


def _matches_forbidden(module: str, forbidden: set[str]) -> bool:
    """判断模块是否命中禁用列表。

    输入: import 模块名和禁用模块集合。
    输出: 完全匹配或子模块匹配时返回 True。
    """
    return any(module == item or module.startswith(f"{item}.") for item in forbidden)


def _layer_for_path(root: Path, path: Path, layers: list[dict[str, object]]) -> dict[str, object] | None:
    """查找路径所属架构层。

    输入: 项目根目录、文件路径和层级配置。
    输出: 匹配到的 layer 字典；未匹配时返回 None。
    """

    relative = path.relative_to(root).as_posix()
    for layer in layers:
        patterns = layer.get("paths", [])
        if isinstance(patterns, list) and any(fnmatch.fnmatch(relative, pattern) for pattern in patterns):
            return layer
    
    return None


def _module_to_path(root: Path, module: str, files: tuple[Path, ...]) -> Path | None:
    """将 import 模块名解析为项目内文件路径。

    输入: 项目根目录、模块名和已发现文件列表。
    输出: 匹配的 Python 文件路径；外部或相对 import 返回 None。
    """

    if module.startswith("."):
        return None
    
    module_path = module.replace(".", "/")
    candidates = {
        root / f"{module_path}.py",
        root / module_path / "__init__.py",
    }

    for file_path in files:
        if file_path in candidates:
            return file_path
        
    return None
