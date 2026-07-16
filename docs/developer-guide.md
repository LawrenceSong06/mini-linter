# mini-linter 开发者指南

本文档面向想要修改、测试、发布或扩展 `mini-linter` 的开发者。

## 本地开发环境

克隆仓库：

```powershell
git clone https://github.com/LawrenceSong06/mini-linter.git
cd mini-linter
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

以 editable 模式安装项目和测试依赖：

```powershell
pip install -e ".[test]"
```

确认 CLI 可用：

```powershell
mini-linter --version
mini-linter -h
```

## 项目结构

- `mini_linter/`：运行时代码包。
- `mini_linter/rules/`：内置 lint 规则。
- `mini_linter/lang/`：规则输出文案 JSON。
- `tests/`：pytest 测试套件。
- `docs/`：用户、开发者和插件文档。
- `pyproject.toml`：包元数据、依赖、pytest 配置和示例 linter 配置。
- `AGENTS.md`：面向 Codex 和其它 LLM Agent 的协作规则。

## 运行测试

运行完整测试：

```powershell
python -m pytest
```

项目默认启用 coverage，等价于：

```powershell
python -m pytest --cov=mini_linter --cov-report=term-missing
```

运行单个测试文件：

```powershell
python -m pytest tests/test_cli.py
```

## 代码分层

- `mini_linter.config`：读取 `pyproject.toml` 并生成 `LinterConfig`。
- `mini_linter.lang`：加载和渲染 lang JSON 文案。
- `mini_linter.plugins`：加载可信本地插件规则。
- `mini_linter.core`：发现文件、解析 AST、运行规则并聚合结果。
- `mini_linter.cli`：解析命令行参数、输出 JSON 和返回退出码。
- `mini_linter.models`：定义 `Violation`、`RuleContext` 和 `LintResult`。

## 新增或修改规则

新增规则时需要同步完成：

- 在 `mini_linter/rules/` 中实现规则。
- 为规则提供稳定的 `rule_id` 和 `default_severity`。
- 在 lang JSON 中添加 `message` 和 `hint`。
- 添加 pass case 和 fail case。
- 测试缺少 lang 文案时会失败，且最终输出包含渲染后的 `message` 和 `hint`。

规则编写细节见 [插件规则编写指南](plugins.md)。内置规则和插件规则使用同一套规则接口。

## 版本和发布

从 GitHub 安装时，pip 依赖包元数据判断当前安装版本。每次准备发布新版本时，请同步更新：

- `pyproject.toml` 中的 `[project].version`。
- `mini_linter/__init__.py` 中的 `__version__`。
- README 或文档中的版本示例 tag。

更新后确认版本一致：

```powershell
mini-linter --version
python -c "import mini_linter; print(mini_linter.__version__)"
```

建议发布流程：

```powershell
python -m pytest
git tag v0.1.1
git push origin main --tags
```

用户可以安装最新 GitHub 版本：

```powershell
pip install --upgrade --force-reinstall "git+https://github.com/LawrenceSong06/mini-linter.git"
```

也可以安装指定 tag：

```powershell
pip install "git+https://github.com/LawrenceSong06/mini-linter.git@v0.1.1"
```

## 文档维护

- `README.md` 只保留安装、快速开始和文档入口。
- `docs/user-guide.md` 放具体用户指南。
- `docs/developer-guide.md` 放开发、测试和发布说明。
- `docs/plugins.md` 放插件规则编写说明。

如果用户可见行为、安装方式、命令参数、配置或规则能力变化，需要同步更新相关文档。
