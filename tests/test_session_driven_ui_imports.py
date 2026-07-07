def test_session_driven_ui_imports():
    imports = [
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
        ("talentcopilot.services.demo_session_factory", "DemoSessionFactory"),
    ]
    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
