from pathlib import Path


def test_runtime_input_diagnostic_is_present():
    source = Path(
        "talentcopilot/ui/recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    assert "Job input stored in active session" in source
    assert "Candidate inputs stored in active session" in source
    assert "hashlib.sha256" in source
    assert '"required_skills"' in source
    assert '"years_experience"' in source
    assert '"skills"' in source
    assert '"raw_text"' in source
