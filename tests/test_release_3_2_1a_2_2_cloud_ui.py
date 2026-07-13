from pathlib import Path


def test_upload_panel_uses_form_and_session_local_cache():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert 'st.form(' in source
    assert "form_submit_button" in source
    assert "talentcopilot_last_analysis_request_key" in source
    assert "st.cache_data" not in source
    assert "OFFICIAL_PIPELINE" in source


def test_upload_panel_records_execution_timings():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "extraction_seconds" in source
    assert "ranking_and_session_seconds" in source
    assert "total_analysis_seconds" in source


def test_app_surfaces_obsolete_session_notice():
    source = Path("app.py").read_text(encoding="utf-8")

    assert "consume_session_invalidation_notice" in source
    assert "st.warning(invalidation_notice)" in source
