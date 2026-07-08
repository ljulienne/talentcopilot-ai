from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_interview_workspace_empty():
    reports = InterviewWorkspaceService().build_all(None)
    assert reports == []


def test_interview_workspace_imports():
    module = __import__("talentcopilot.ui.interview_workspace", fromlist=["render_interview_workspace"])
    assert hasattr(module, "render_interview_workspace")


def test_interview_workspace_navigation():
    page = get_page_by_label("Interview Workspace")
    assert page is not None
    assert page.module == "talentcopilot.ui.interview_workspace"
    assert page.function == "render_interview_workspace"
