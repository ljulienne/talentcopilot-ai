def test_ui_modules_import():
    imports = [
        ("talentcopilot.ui.theme", "apply_theme"),
        ("talentcopilot.ui.premium_theme", "apply_premium_ui"),
        ("talentcopilot.ui.premium_theme", "premium_sidebar_brand"),
        ("talentcopilot.ui.sidebar", "render_sidebar_brand"),
        ("talentcopilot.ui.sidebar", "render_sidebar_context"),
        ("talentcopilot.ui.sidebar", "render_sidebar_workflow"),
        ("talentcopilot.ui.home", "render_home"),
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard", "render_dashboard"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.comparison", "render_candidate_comparison"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.reports", "render_reports"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        ("talentcopilot.ui.settings", "render_settings"),
        ("talentcopilot.ui.candidates", "render_candidates"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.recruitment_wizard", "render_new_recruitment"),
        ("talentcopilot.ui.open_recruitment", "render_open_recruitment"),
        ("talentcopilot.ui.talent_pool", "render_talent_pool"),
        ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        ("talentcopilot.ui.recruiter_copilot", "render_recruiter_copilot"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.session_health", "render_session_health"),
        ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
        ("talentcopilot.ui.app_layout", "render_page_shell"),
        ("talentcopilot.ui.components", "footer"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
