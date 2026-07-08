from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_recruitment_workspace_empty_report():
    report = RecruitmentWorkspaceService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.pipeline
    assert report.next_actions


def test_recruitment_workspace_page_imports():
    module = __import__("talentcopilot.ui.recruitment_workspace", fromlist=["render_recruitment_workspace"])
    assert hasattr(module, "render_recruitment_workspace")


def test_recruitment_workspace_in_navigation():
    page = get_page_by_label("Recruitment Workspace")

    assert page is not None
    assert page.module == "talentcopilot.ui.recruitment_workspace"
    assert page.function == "render_recruitment_workspace"
