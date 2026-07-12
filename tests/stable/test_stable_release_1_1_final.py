from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label


def test_release_alpha_key_pages_present():
    labels = [page.label for page in flatten_enterprise_pages()]
    expected = [
        "Executive Brief",
        "Organization Intelligence",
        "Recruitment Workspace",
        "Candidate Workspace",
        "Comparison",
        "Interview Workspace",
        "Hiring Budget",
        "Decision Board",
        "Analytics Dashboard",
        "Executive Reporting",
        "Enterprise Demo Final",
    ]
    for label in expected:
        assert label in labels


def test_legacy_command_center_remains_importable_but_hidden():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert "Recruitment Command Center" not in labels
    page = get_page_by_label("Recruitment Command Center")
    assert page is not None
    module = __import__(page.module, fromlist=[page.function])
    assert hasattr(module, page.function)
