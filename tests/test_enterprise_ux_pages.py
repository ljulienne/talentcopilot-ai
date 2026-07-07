def test_enterprise_pages_import():
    imports = [
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
        ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)


def test_enterprise_pages_have_distinct_titles():
    from pathlib import Path

    expected = {
        "home_v2.py": "TalentCopilot-AI",
        "dashboard_v2.py": "Decision Center",
        "candidates_v2.py": "Candidates",
        "talent_pool_v2.py": "Talent Pool",
        "recruiter_copilot_v2.py": "Recruiter Copilot",
        "comparison_v2.py": "Comparison",
        "reports_v2.py": "Reports",
        "decision_workspace.py": "Decision Workspace",
    }

    ui_path = Path("talentcopilot/ui")
    for filename, title in expected.items():
        text = (ui_path / filename).read_text(encoding="utf-8")
        assert title in text
        assert " V2" not in text
        assert " v2" not in text
