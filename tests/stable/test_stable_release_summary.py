from talentcopilot.services.release_summary_service import ReleaseSummaryService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_release_summary_service():
    summary = ReleaseSummaryService().build()

    assert "Release 1.0" in summary.release_name
    assert summary.workspaces
    assert summary.next_release_focus


def test_release_summary_imports():
    module = __import__("talentcopilot.ui.release_summary", fromlist=["render_release_summary"])
    assert hasattr(module, "render_release_summary")


def test_release_summary_navigation():
    page = get_page_by_label("Release Summary")
    assert page is not None
    assert page.module == "talentcopilot.ui.release_summary"
    assert page.function == "render_release_summary"
