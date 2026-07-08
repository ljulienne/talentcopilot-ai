from talentcopilot.services.release_1_1_summary_service import Release11SummaryService
from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label


def test_release_1_1_summary_service():
    summary = Release11SummaryService().build()

    assert "Release 1.1" in summary.title
    assert len(summary.modules) >= 8
    assert summary.blueprint_readiness
    assert summary.next_steps


def test_release_1_1_summary_imports():
    module = __import__("talentcopilot.ui.release_1_1_summary", fromlist=["render_release_1_1_summary"])
    assert hasattr(module, "render_release_1_1_summary")


def test_release_1_1_summary_navigation():
    page = get_page_by_label("Release 1.1 Summary")
    assert page is not None
    assert page.module == "talentcopilot.ui.release_1_1_summary"
    assert page.function == "render_release_1_1_summary"


def test_release_1_1_key_pages_present():
    labels = [page.label for page in flatten_enterprise_pages()]
    expected = [
        "Product Overview",
        "Recruitment Command Center",
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
