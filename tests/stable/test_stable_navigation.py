from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_enterprise_navigation


def test_navigation_has_required_sections():
    sections = get_enterprise_navigation()
    assert "command" in sections
    assert "analysis" in sections
    assert "decision" in sections
    assert "administration" in sections


def test_navigation_targets_import():
    for page in flatten_enterprise_pages():
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label


def test_navigation_labels_are_clean():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert len(labels) == len(set(labels))
    assert all("v2" not in label.lower() for label in labels)
