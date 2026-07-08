from talentcopilot.ui.navigation import flattened_pages


def test_all_navigation_pages_import():
    for page in flattened_pages():
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label
