from pathlib import Path


def test_upload_panel_captures_exact_input_contract():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "runtime_input_contract" in source
    assert '"upload_sha256"' in source
    assert '"text_sha256"' in source
    assert "hashlib.sha256" in source
    assert (
        '"runtime_input_contract": runtime_input_contract'
        in source
    )


def test_workspace_compares_runtime_and_session_hashes():
    source = Path(
        "talentcopilot/ui/recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    assert "Production input contract" in source
    assert '"job_hashes_equal"' in source
    assert '"hashes_equal"' in source
    assert '"text_sha256_before_worker"' in source
    assert '"text_sha256_from_session"' in source


def test_diagnostic_does_not_modify_scores():
    source = Path(
        "talentcopilot/ui/recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    trace = source[
        source.index("Production input contract"):
    ]

    assert ".match_score =" not in trace
    assert "official_match_score =" not in trace
