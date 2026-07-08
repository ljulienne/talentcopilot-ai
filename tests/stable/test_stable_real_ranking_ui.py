from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_real_ranking_ui_imports():
    module = __import__("talentcopilot.ui.real_ranking", fromlist=["render_real_ranking"])
    assert hasattr(module, "render_real_ranking")


def test_real_ranking_navigation():
    page = get_page_by_label("Real Ranking")
    assert page is not None
    assert page.module == "talentcopilot.ui.real_ranking"
    assert page.function == "render_real_ranking"
