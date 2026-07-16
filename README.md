# mini-linter

`mini-linter` is a compact Python CLI linter for Agent-driven projects. It checks Python style, import dependencies, architecture boundaries, and Agent collaboration files, then prints JSON output that tools and LLM Agents can parse directly.

## Installation

Install the latest version from GitHub:

```powershell
pip install "git+https://github.com/LawrenceSong06/mini-linter.git"
```

Upgrade to the latest GitHub version:

```powershell
pip install --upgrade --force-reinstall "git+https://github.com/LawrenceSong06/mini-linter.git"
```

Install a specific Git tag when releases are tagged:

```powershell
pip install "git+https://github.com/LawrenceSong06/mini-linter.git@v0.1.1"
```

Verify the installed version:

```powershell
mini-linter --version
pip show mini-linter
```

## Quick Start

Run checks against the current project:

```powershell
mini-linter check .
```

Use a project config:

```powershell
mini-linter check --config pyproject.toml
```

Treat warnings as failures:

```powershell
mini-linter check . --fail-on warning
```

## Documentation

- [User Guide](docs/user-guide.md): usage, configuration, JSON output, built-in rules, and CI examples.
- [Developer Guide](docs/developer-guide.md): local setup, tests, architecture, release/version workflow, and contribution notes.
- [Plugin Rule Guide](docs/plugins.md): writing and configuring local plugin rules.

## Requirements

- Python 3.7 or newer.
- Python 3.11+ uses the standard-library TOML parser.
- Python 3.7-3.10 installs `tomli` automatically as the TOML parser fallback.

## Versioning

The package version is stored in both `pyproject.toml` and `mini_linter.__version__`. Keep them synchronized before publishing or tagging a new GitHub release so pip and users can detect version changes.
