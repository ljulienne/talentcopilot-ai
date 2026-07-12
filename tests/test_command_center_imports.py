def test_release_alpha_primary_navigation_imports():
    from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_enterprise_navigation

    sections = get_enterprise_navigation()
    assert "command" in sections

    pages = flatten_enterprise_pages()
    labels = [page.label for page in pages]
    assert "Executive Brief" in labels
    assert "Recruitment Command Center" not in labels

    for page in pages:
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label
