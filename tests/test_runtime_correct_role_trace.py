from pathlib import Path


def test_runtime_trace_uses_real_role_profile_structure():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert '"role_profile"' in source
    assert '"job_analysis"' in source
    assert '"required_skills"' in source
    assert '"minimum_years_experience"' in source
    assert '"extraction_status"' in source
    assert '"profile_fit_score"' in source
    assert '"fit_summary"' in source
    assert "Skill match=" in source
    assert "experience match=" in source
    assert "achievement signal=" in source
