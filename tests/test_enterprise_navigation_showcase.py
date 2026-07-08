from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_enterprise_navigation, get_page_by_label


def test_ui_showcase_is_in_navigation():
    page = get_page_by_label("UI Showcase")
    assert page is not None
    assert page.module == "talentcopilot.ui.ui_showcase"
    assert page.function == "render_ui_showcase"


def test_navigation_sections_have_descriptions():
    sections = get_enterprise_navigation()
    assert sections
    for section in sections.values():
        assert section.description
        assert section.pages


def test_navigation_labels_are_unique():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert len(labels) == len(set(labels))
