from talentcopilot.ui.navigation import flattened_pages, get_navigation_sections


def test_navigation_sections_are_distinct():
    sections = get_navigation_sections()

    assert set(sections.keys()) == {"start", "analyze", "decide", "deliver", "admin"}
    assert sections["analyze"].label == "Analyze"
    assert sections["decide"].label == "Decide"


def test_navigation_pages_have_unique_labels():
    pages = flattened_pages()
    labels = [page.label for page in pages]

    assert len(labels) == len(set(labels))
    assert "Candidates" in labels
    assert "Talent Pool" in labels
    assert "Recruiter Copilot" in labels
    assert all("v2" not in label.lower() for label in labels)


def test_navigation_pages_have_purpose():
    for page in flattened_pages():
        assert page.purpose
        assert page.module.startswith("talentcopilot.ui.")
        assert page.function.startswith("render_")
