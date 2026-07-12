from pathlib import Path


def test_active_recruitment_workspace_embeds_real_upload_panel():
    source = Path("talentcopilot/ui/recruitment_decision_workspace.py").read_text(encoding="utf-8")

    assert "render_recruitment_upload_panel" in source
    assert "session = render_recruitment_upload_panel(session)" in source


def test_upload_panel_uses_real_services_and_official_session_bridge():
    source = Path("talentcopilot/ui/recruitment_upload_panel.py").read_text(encoding="utf-8")

    assert "UploadTextReaderService" in source
    assert "RecruitmentUploadSessionService" in source
    assert "set_streamlit_session(session)" in source
    assert "Analyze uploaded candidates" in source
    assert "Load sample data" in source
