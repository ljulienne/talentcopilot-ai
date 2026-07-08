from talentcopilot.services.candidate_workspace_v2_service import CandidateWorkspaceV2Service
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_candidate_workspace_v2_demo():
    report = CandidateWorkspaceV2Service().build_demo()

    assert report.status == "Ready"
    assert report.outputs
    assert report.outputs[0].profile.recommendation


def test_candidate_workspace_v2_imports():
    module = __import__("talentcopilot.ui.candidate_workspace_v2", fromlist=["render_candidate_workspace_v2"])
    assert hasattr(module, "render_candidate_workspace_v2")


def test_candidate_workspace_v2_navigation():
    page = get_page_by_label("Candidate Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.candidate_workspace_v2"
    assert page.function == "render_candidate_workspace_v2"
