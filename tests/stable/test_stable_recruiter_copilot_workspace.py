from talentcopilot.services.recruiter_copilot_workspace_service import RecruiterCopilotWorkspaceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_recruiter_copilot_workspace_empty_report():
    report = RecruiterCopilotWorkspaceService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.candidates == []
    assert report.global_actions


def test_recruiter_copilot_workspace_imports():
    module = __import__(
        "talentcopilot.ui.recruiter_copilot_workspace",
        fromlist=["render_recruiter_copilot_workspace"],
    )
    assert hasattr(module, "render_recruiter_copilot_workspace")


def test_recruiter_copilot_workspace_navigation():
    page = get_page_by_label("Recruiter Copilot")
    assert page is not None
    assert page.module == "talentcopilot.ui.recruiter_copilot_workspace"
    assert page.function == "render_recruiter_copilot_workspace"
