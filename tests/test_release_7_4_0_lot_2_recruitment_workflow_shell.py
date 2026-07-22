from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def _session(analyzed=True):
    status = CandidateAnalysisStatus.ANALYZED if analyzed else CandidateAnalysisStatus.PENDING
    return RecruitmentSession(
        session_id="workflow-test",
        job={"title": "HRIS Manager", "description": "Lead HRIS transformation"},
        candidates=[{"candidate_id": "c1", "name": "Candidate One"}],
        analyses=[CandidateAnalysisState(candidate_id="c1", candidate_name="Candidate One", status=status, match_score=78, rank=1)],
        status=SessionStatus.COMPLETED if analyzed else SessionStatus.ANALYZING,
    )


def test_workflow_resolves_canonical_session_steps_without_touching_scores():
    session = _session(analyzed=True)
    original_score = session.analyses[0].match_score
    states = RecruitmentWorkflowService().resolve_steps(session, RecruitmentWorkflowContext())
    assert [item.key for item in states[:4]] == ["setup", "role", "candidates", "analysis"]
    assert all(item.completed for item in states[:4])
    assert states[4].key == "candidate"
    assert session.analyses[0].match_score == original_score


def test_selected_candidate_persists_and_unlocks_candidate_review():
    session = _session(analyzed=True)
    context = RecruitmentWorkflowContext()
    context.select_candidate("c1", "Candidate One")
    states = RecruitmentWorkflowService().resolve_steps(session, context, current_page="Candidate Intelligence")
    candidate = next(item for item in states if item.key == "candidate")
    assert candidate.completed is True
    assert candidate.current is True


def test_incomplete_prerequisites_block_later_steps():
    session = RecruitmentSession(session_id="draft", job={}, candidates=[], analyses=[])
    states = RecruitmentWorkflowService().resolve_steps(session, RecruitmentWorkflowContext())
    role = next(item for item in states if item.key == "role")
    candidates = next(item for item in states if item.key == "candidates")
    assert role.current is True
    assert candidates.available is False
    assert candidates.reason


def test_previous_and_next_route_resolution():
    session = _session(analyzed=True)
    context = RecruitmentWorkflowContext(selected_candidate_id="c1", selected_candidate_name="Candidate One")
    states = RecruitmentWorkflowService().resolve_steps(session, context, current_page="Candidate Intelligence")
    previous = RecruitmentWorkflowService.previous_step(states)
    next_step = RecruitmentWorkflowService.next_step(states)
    assert previous is not None and previous.page_label == "Recruitment Workspace"
    assert next_step is not None and next_step.page_label == "Interview Intelligence"


def test_primary_workflow_routes_are_reachable():
    for label in ["Recruitment Workspace", "Candidate Intelligence", "Interview Intelligence", "Comparison", "Decision Board"]:
        assert get_page_by_label(label) is not None
