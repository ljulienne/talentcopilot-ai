import importlib.util
from pathlib import Path


def test_app_defines_navigation_registry():
    app_path = Path("app.py")
    assert app_path.exists()

    text = app_path.read_text(encoding="utf-8")
    assert "def navigation_registry" in text
    assert "importlib.import_module" in text
    assert "selected_page = pages[page_label]" not in text


def test_navigation_modules_import():
    # app.py imports streamlit at module level, so avoid importing app directly in tests.
    expected = [
        ("talentcopilot.ui.home_v2", "render_home_v2"),
        ("talentcopilot.ui.dashboard_v2", "render_dashboard_v2"),
        ("talentcopilot.ui.decision_workspace", "render_decision_workspace"),
        ("talentcopilot.ui.candidates_v2", "render_candidates_v2"),
        ("talentcopilot.ui.talent_pool_v2", "render_talent_pool_v2"),
        ("talentcopilot.ui.recruiter_copilot_v2", "render_recruiter_copilot_v2"),
        ("talentcopilot.ui.comparison_v2", "render_comparison_v2"),
        ("talentcopilot.ui.reports_v2", "render_reports_v2"),
    ]

    for module_name, attr in expected:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr)
