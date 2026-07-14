"""上次修改: 2026-07-14; 设计: 插件加载边界; 功能: 从可信本地 Python 文件加载规则类。"""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from mini_linter.models import Rule


def load_plugin_rules(root: Path, plugin_paths: tuple[str, ...]) -> list[Rule]:
    """加载本地插件规则。

    输入: 项目 root 和插件路径列表。
    输出: 实例化后的规则列表；插件无法导入时抛出 ValueError。
    """
    rules: list[Rule] = []
    for index, plugin_path in enumerate(plugin_paths):
        path = (root / plugin_path).resolve()
        module_name = f"mini_linter_plugin_{index}_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load plugin: {path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for _, item in inspect.getmembers(module, inspect.isclass):
            if item.__module__ != module.__name__:
                continue
            # 没有被 continue 的情况: 当前类是在插件文件中直接定义的类，不包含导入类。

            if hasattr(item, "id") and hasattr(item, "check"):
                rules.append(item())
    return rules
