from pathlib import Path


def test_runtime_parity_contains_input_sha256():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert '"job_sha256"' in source
    assert '"candidate_sha256"' in source
    assert "hashlib.sha256" in source
    assert 'text.encode("utf-8")' in source
    assert '"job_characters"' in source
    assert '"candidate_characters"' in source
