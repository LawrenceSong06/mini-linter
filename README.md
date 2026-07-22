# mini-linter

您好，欢迎使用 `mini-linter`。

`mini-linter` 是一个面向 Agent 驱动项目的紧凑型 Python CLI linter。它用于检查 Python 代码风格、import 依赖、架构边界和 Agent 协作文件，并输出便于工具和 LLM Agent 直接解析的 JSON 结果。

## 安装

从 GitHub 安装最新版本：

```powershell
pip install "git+https://github.com/LawrenceSong06/mini-linter.git"
```

升级到 GitHub 最新版本：

```powershell
pip install --upgrade --force-reinstall "git+https://github.com/LawrenceSong06/mini-linter.git"
```

发布版本 tag 后，也可以安装指定版本：

```powershell
pip install "git+https://github.com/LawrenceSong06/mini-linter.git@v0.1.2"
```

检查已安装版本：

```powershell
mini-linter --version
pip show mini-linter
```

## 快速开始

在项目根目录初始化 mini-linter 配置模板：

```powershell
mini-linter init
```

`init` 会创建 `linter_config.toml`、`linter/` 模板目录和中文说明文件 `mini-linter_README.md`。

检查当前项目：

```powershell
mini-linter check .
```

使用项目配置：

```powershell
mini-linter check --config linter_config.toml
```

`mini-linter` 的配置文件需要放在被检查项目的根目录，推荐使用 `mini-linter init` 生成的 `linter_config.toml`。

将 warning 也视为失败：

```powershell
mini-linter check . --fail-on warning
```

## 文档

- [用户指南](docs/user-guide.md)：使用方式、配置、JSON 输出、内置规则和 CI 示例。
- [开发者指南](docs/developer-guide.md)：本地环境、测试、架构、发布/版本流程和贡献说明。
- [插件规则指南](docs/plugins.md)：编写和配置本地插件规则。

## 环境要求

- Python 3.7 或更高版本。
- Python 3.11+ 使用标准库 TOML 解析器。
- Python 3.7-3.10 会自动安装 `tomli` 作为 TOML 解析兼容依赖。

## 版本

包版本同时保存在 `pyproject.toml` 和 `mini_linter.__version__` 中。发布新版本或创建 GitHub release tag 前，请保持两处版本号同步，这样 pip 和用户才能检测到版本变化。
