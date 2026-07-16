from pathlib import Path


def test_runtime_parity_check_compares_both_paths():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "Runtime parity check" in source
    assert "RecruitmentUploadSessionService().run(" in source
    assert "IsolatedRecruitmentUploadService().run(" in source
    assert '"direct_match"' in source
    assert '"isolated_match"' in source
    assert "talentcopilot_runtime_scoring_parity" in source
