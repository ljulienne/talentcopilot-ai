from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_enterprise_navigation, get_page_by_label


def test_navigation_no_legacy_decision_entries():
    assert get_page_by_label("Decision Center") is None
    assert get_page_by_label("Decision Workspace") is None


def test_navigation_uses_workspace_modules():
    expected = {
        "Candidate Workspace": "talentcopilot.ui.candidate_workspace",
        "Talent Intelligence": "talentcopilot.ui.talent_intelligence",
        "Comparison": "talentcopilot.ui.comparison_workspace",
        "Decision Board": "talentcopilot.ui.decision_board",
        "Recruiter Copilot": "talentcopilot.ui.recruiter_copilot_workspace",
        "Executive Reporting": "talentcopilot.ui.executive_reporting",
    }

    for label, module in expected.items():
        page = get_page_by_label(label)
        assert page is not None
        assert page.module == module


def test_navigation_has_manageable_size():
    pages = flatten_enterprise_pages()
    assert len(pages) <= 16


def test_navigation_sections_have_clear_purpose():
    sections = get_enterprise_navigation()
    for section in sections.values():
        assert section.description
        assert section.pages
