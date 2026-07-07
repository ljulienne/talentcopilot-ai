def test_enterprise_integration_imports():
    imports = [
        ("talentcopilot.models.recruitment_session", "RecruitmentSession"),
        ("talentcopilot.models.recruitment_session", "CandidateAnalysisState"),
        ("talentcopilot.ai.enterprise_pipeline", "EnterprisePipeline"),
        ("talentcopilot.services.session_store", "SessionStore"),
        ("talentcopilot.ui.enterprise_integration_cards", "render_recruitment_session_overview"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
