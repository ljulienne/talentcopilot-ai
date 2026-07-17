from pathlib import Path


def test_official_score_propagation_trace_is_present():
    source = Path(
        "talentcopilot/ui/"
        "recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    assert "Official score propagation trace" in source
    assert "Active RecruitmentSession" in source
    assert "ComparisonWorkspaceService output" in source
    assert "Propagation comparison" in source
    assert '"session_match_score"' in source
    assert '"comparison_match_score"' in source
    assert '"delta"' in source


def test_trace_does_not_modify_scores():
    source = Path(
        "talentcopilot/ui/"
        "recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    trace = source[
        source.index(
            "Official score propagation trace"
        ):
    ]

    assert ".match_score =" not in trace
    assert "official_match_score =" not in trace
