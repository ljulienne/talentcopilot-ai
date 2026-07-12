from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label
from talentcopilot.ui.recruitment_decision_workspace import _find, _names


def test_recruitment_workspace_is_unified_primary_navigation():
    pages = {page.label: page for page in flatten_enterprise_pages()}
    page = pages["Recruitment Workspace"]
    assert page.module == "talentcopilot.ui.recruitment_decision_workspace"
    assert page.function == "render_recruitment_decision_workspace"


def test_recruitment_subpages_are_legacy_only():
    labels = {page.label for page in flatten_enterprise_pages()}
    for label in (
        "Candidate Workspace",
        "Comparison",
        "Interview Workspace",
        "Decision Board",
        "Executive Reporting",
    ):
        assert label not in labels
        assert get_page_by_label(label) is not None


def test_candidate_name_helpers_preserve_order_and_find_records():
    session = create_demo_recruitment_session()
    analyses = list(session.ranked_analyses)
    names = _names(analyses)
    assert names
    assert names[0] == analyses[0].candidate_name
    assert _find(analyses, names[0]) is analyses[0]
    assert _find(analyses, "Missing Candidate") is None
