from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_comparison_workspace_empty_report():
    report = ComparisonWorkspaceService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.candidates == []
    assert report.differentiators


def test_comparison_workspace_imports():
    module = __import__("talentcopilot.ui.comparison_workspace", fromlist=["render_comparison_workspace"])
    assert hasattr(module, "render_comparison_workspace")


def test_comparison_workspace_navigation():
    page = get_page_by_label("Comparison")
    assert page is not None
    assert page.module == "talentcopilot.ui.comparison_workspace"
    assert page.function == "render_comparison_workspace"
