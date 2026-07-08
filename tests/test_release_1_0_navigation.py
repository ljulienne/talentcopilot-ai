from talentcopilot.ui.design_system.navigation import (
    flatten_enterprise_pages,
    get_enterprise_navigation,
)


def test_enterprise_navigation_sections():
    sections = get_enterprise_navigation()

    assert "Command" in sections
    assert "Recruitment" in sections
    assert "Analysis" in sections
    assert "Decision" in sections
    assert "Reporting" in sections
    assert "Administration" in sections


def test_enterprise_navigation_pages_are_importable():
    for page in flatten_enterprise_pages():
        module = __import__(page.module, fromlist=[page.function])
        assert hasattr(module, page.function), page.label


def test_enterprise_navigation_has_no_v2_labels():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert all("v2" not in label.lower() for label in labels)
    assert "Recruitment Command Center" in labels
