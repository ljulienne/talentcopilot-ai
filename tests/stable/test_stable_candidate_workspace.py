from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_candidate_workspace_empty():
    reports = CandidateWorkspaceService().build_all(None)
    assert reports == []


def test_candidate_workspace_imports():
    module = __import__("talentcopilot.ui.candidate_workspace", fromlist=["render_candidate_workspace"])
    assert hasattr(module, "render_candidate_workspace")


def test_candidate_workspace_navigation():
    page = get_page_by_label("Candidate Workspace")
    assert page is not None
    assert page.module == "talentcopilot.ui.candidate_workspace"
    assert page.function == "render_candidate_workspace"
