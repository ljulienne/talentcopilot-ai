def test_enterprise_navigation_imports():
    from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_enterprise_navigation

    sections = get_enterprise_navigation()
    assert "Command" in sections

    pages = flatten_enterprise_pages()
    assert any(page.label == "Recruitment Command Center" for page in pages)

    for page in pages:
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label
