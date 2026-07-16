from pathlib import Path


def test_environment_fingerprint_is_present():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "Runtime environment fingerprint" in source
    assert "_module_fingerprint" in source
    assert "importlib.metadata.version" in source
    assert "fit_intelligence_engine" in source
    assert "recruitment_upload_session_service" in source
    assert '"configuration_names"' in source
