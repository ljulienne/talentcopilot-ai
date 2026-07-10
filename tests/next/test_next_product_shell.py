from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label


def test_next_entry_points_exist():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert "Executive Brief" in labels
    assert "Organization Intelligence" in labels
    assert len(labels) == 16


def test_runtime_navigation_contract():
    page = get_page_by_label("Organization Intelligence")
    assert page.icon
    assert page.module == "talentcopilot.ui.organization_intelligence_preview"
