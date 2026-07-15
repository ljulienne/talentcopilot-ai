from pathlib import Path


def test_runtime_score_diagnostic_is_present():
    source = Path(
        "talentcopilot/ui/recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    assert "Runtime score diagnostic" in source
    assert "raw_match_score" in source
    assert "official_match_score" in source
    assert "comparison_match" in source
    assert "deployed_commit" in source
    assert "metadata.get(\"source\")" in source
