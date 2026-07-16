from pathlib import Path


def test_fit_component_trace_is_present():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "Fit component trace" in source
    assert "RealUploadRankingService().run(" in source
    assert '"skill_match"' in source
    assert '"experience_match"' in source
    assert '"achievement_signal"' in source
    assert '"minimum_years_experience"' in source
    assert "talentcopilot_fit_component_trace" in source
