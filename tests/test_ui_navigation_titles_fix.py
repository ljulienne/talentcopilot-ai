from pathlib import Path


def test_ui_pages_import_with_clean_titles():
    imports = [
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)


def test_visible_titles_do_not_contain_v2():
    ui_path = Path("talentcopilot/ui")
    files = [
        "home_v2.py",
        "dashboard_v2.py",
        "candidates_v2.py",
        "talent_pool_v2.py",
        "recruiter_copilot_v2.py",
        "comparison_v2.py",
        "reports_v2.py",
    ]

    for filename in files:
        text = (ui_path / filename).read_text(encoding="utf-8")
        title_lines = [line for line in text.splitlines() if "st.title(" in line]
        assert title_lines
        for line in title_lines:
            assert "V2" not in line
            assert "v2" not in line
