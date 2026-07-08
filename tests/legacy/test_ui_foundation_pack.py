from talentcopilot.ui.app_layout import render_page_shell, render_copilot_panel
from talentcopilot.ui.dashboard_v2 import render_dashboard_v2


def test_layout_components_are_callable():
    assert callable(render_page_shell)
    assert callable(render_copilot_panel)


def test_dashboard_v2_is_callable():
    assert callable(render_dashboard_v2)
