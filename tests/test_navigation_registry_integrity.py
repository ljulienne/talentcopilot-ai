from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages


def test_all_navigation_targets_import():
    for page in flatten_enterprise_pages():
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label


def test_no_v2_in_navigation_labels():
    for page in flatten_enterprise_pages():
        assert "v2" not in page.label.lower()
