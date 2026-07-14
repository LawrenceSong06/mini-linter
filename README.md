# mini-linter

A compact Python linter for agent-driven projects.

`mini-linter` checks Python style, import dependencies, architecture boundaries, and agent collaboration files. It is intentionally small: runtime code uses the Python standard library, while tests use `pytest`.

```powershell
mini-linter check .
```

The default output is JSON so Codex and other LLM agents can parse findings directly.
