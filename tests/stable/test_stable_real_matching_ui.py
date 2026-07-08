from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_real_matching_ui_imports():
    module = __import__("talentcopilot.ui.real_matching", fromlist=["render_real_matching"])
    assert hasattr(module, "render_real_matching")


def test_real_matching_navigation():
    page = get_page_by_label("Real Matching")
    assert page is not None
    assert page.module == "talentcopilot.ui.real_matching"
    assert page.function == "render_real_matching"
