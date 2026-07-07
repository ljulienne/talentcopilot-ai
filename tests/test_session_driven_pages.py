def test_session_driven_pages_import():
    imports = [
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        ("talentcopilot.ui.session_driven_components", "session_action_bar"),
        ("talentcopilot.ui.session_driven_components", "ranked_candidates_table"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
