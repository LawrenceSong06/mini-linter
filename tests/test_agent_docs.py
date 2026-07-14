"""上次修改: 2026-07-14; 设计: Agent 文档测试; 功能: 验证协作文档存在且包含关键要求。"""

from pathlib import Path


def test_agent_collaboration_docs_exist() -> None:
    """验证 Agent 协作文档都存在且非空。

    输入: 仓库根目录文件。
    输出: 断言必需文档可读取。
    """
    root = Path(__file__).resolve().parents[1]
    required = [
        "AGENTS.md",
        ".agents/context.md",
        ".agents/rule-authoring.md",
        ".agents/review-checklist.md",
        ".agents/task-template.md",
    ]

    for entry in required:
        path = root / entry

        assert path.exists(), entry
        assert path.read_text(encoding="utf-8").strip()


def test_agent_docs_require_message_hint_and_tests() -> None:
    """验证 Agent 文档包含 violation 和测试要求。

    输入: `AGENTS.md` 和规则编写指南。
    输出: 断言关键约束文本存在。
    """

    root = Path(__file__).resolve().parents[1]
    guide = (root / "AGENTS.md").read_text(encoding="utf-8")
    rules = (root / ".agents/rule-authoring.md").read_text(encoding="utf-8")

    assert "message" in guide
    assert "hint" in guide
    assert "unit test" in guide
    assert "每个 violation 必须包含" in rules


def test_agent_docs_require_comment_and_readme_updates() -> None:
    """验证 Agent 文档包含注释和 README 同步要求。

    输入: `AGENTS.md`、review checklist 和任务模板。
    输出: 断言注释规则和 README 更新要求存在。
    """
    
    root = Path(__file__).resolve().parents[1]
    guide = (root / "AGENTS.md").read_text(encoding="utf-8")
    checklist = (root / ".agents/review-checklist.md").read_text(encoding="utf-8")
    template = (root / ".agents/task-template.md").read_text(encoding="utf-8")

    assert "上次修改时间" in guide
    assert "docstring" in guide
    assert "else" in guide
    assert "continue" in guide
    assert "README.md" in guide
    assert "README.md" in checklist
    assert "相关注释" in template
