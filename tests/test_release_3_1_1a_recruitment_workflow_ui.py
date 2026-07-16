from pathlib import Path


def test_active_recruitment_workspace_embeds_real_upload_panel():
    source = Path("talentcopilot/ui/recruitment_decision_workspace.py").read_text(encoding="utf-8")

    assert "render_recruitment_upload_panel" in source
    assert "session = render_recruitment_upload_panel(session)" in source


def test_upload_panel_uses_real_services_and_official_session_bridge():
    """Release 3.4 executes canonical scoring in an isolated process."""

    panel_source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    worker_source = Path(
        "talentcopilot/services/"
        "isolated_recruitment_upload_worker.py"
    ).read_text(encoding="utf-8")

    assert "UploadTextReaderService" in panel_source
    assert "IsolatedRecruitmentUploadService" in panel_source
    assert "set_streamlit_session(session)" in panel_source
    assert "Analyze uploaded candidates" in panel_source
    assert "Load sample data" in panel_source

    # The canonical service remains the actual scoring implementation,
    # but it now runs inside the isolated worker rather than directly
    # in the Streamlit process.
    assert "RecruitmentUploadSessionService" in worker_source
    assert "RecruitmentUploadSessionService().run(" in worker_source
