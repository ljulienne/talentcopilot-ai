def test_feature_restoration_components_import():
    module = __import__(
        "talentcopilot.ui.feature_restoration_components",
        fromlist=[
            "page_purpose",
            "session_required_hint",
            "candidate_kpi_strip",
            "decision_summary_for_analysis",
        ],
    )

    assert hasattr(module, "page_purpose")
    assert hasattr(module, "session_required_hint")
    assert hasattr(module, "candidate_kpi_strip")
    assert hasattr(module, "decision_summary_for_analysis")


def test_talent_pool_dependencies_import():
    imports = [
        ("talentcopilot.ai.talent_locator_engine", "TalentLocatorEngine"),
        ("talentcopilot.ui.talent_locator_cards", "render_talent_locator_results"),
        ("talentcopilot.services.streamlit_session_bridge", "get_streamlit_session"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
