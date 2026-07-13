import ast
from pathlib import Path


WORKSPACE = Path("talentcopilot/ui/recruitment_decision_workspace.py")


def test_workspace_uses_presentation_cockpit_service():
    source = WORKSPACE.read_text(encoding="utf-8")
    assert "RecruitmentCockpitService" in source
    assert "_render_cockpit(cockpit_view)" in source
    assert "official match" in source


def test_workspace_does_not_assign_official_score_or_rank():
    tree = ast.parse(WORKSPACE.read_text(encoding="utf-8"))
    forbidden = {"match_score", "ranked_analyses", "rank"}

    assigned_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_names.add(target.id)

    assert not (assigned_names & forbidden)
