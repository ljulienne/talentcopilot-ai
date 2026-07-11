import ast
from pathlib import Path


def test_organization_preview_defines_knowledge_insights_before_aggregation():
    path = Path("talentcopilot/ui/organization_intelligence_preview.py")
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)

    assigned_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (
            node.targets if isinstance(node, ast.Assign) else [node.target]
        )
        if isinstance(target, ast.Name)
    }

    assert "knowledge_insights" in assigned_names
    assert "combined_insights" in assigned_names
    assert "[*insights" not in text
    assert "return insights" in text
