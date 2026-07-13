import ast
from pathlib import Path


PAGE = Path("talentcopilot/ui/candidate_workspace.py")


def test_candidate_intelligence_page_uses_presentation_service():
    source = PAGE.read_text(encoding="utf-8")

    assert "CandidateIntelligenceViewService" in source
    assert "_render_candidate_decision_brief" in source
    assert '"Candidate Intelligence"' in source
    assert "Official session score" in source
    assert "Official session ranking" in source


def test_candidate_intelligence_ui_does_not_assign_official_results():
    tree = ast.parse(PAGE.read_text(encoding="utf-8"))

    forbidden_names = {
        "match_score",
        "official_match_score",
        "rank",
        "official_rank",
        "ranked_analyses",
    }

    assigned = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)

    assert not (assigned & forbidden_names)


def test_candidate_intelligence_page_does_not_call_matching_or_demo_pipeline():
    source = PAGE.read_text(encoding="utf-8")

    assert ".run_demo(" not in source
    assert "FitIntelligenceEngine(" not in source
    assert "MatchingEngine(" not in source
    assert "CandidateDecisionProfileService(" not in source
