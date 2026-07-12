from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.ui.recruitment_decision_workspace import (
    ExecutiveDecisionView,
    _build_executive_decision,
)


def test_executive_decision_uses_existing_reports_without_recalculation():
    session = create_demo_recruitment_session()
    candidate = CandidateWorkspaceService().build_all(session)[0]
    decision = DecisionBoardService().build(session)

    view = _build_executive_decision(candidate, decision)

    assert isinstance(view, ExecutiveDecisionView)
    assert view.candidate_name == candidate.candidate_name
    assert view.match_score == candidate.match_score
    assert view.recommendation
    assert view.confidence_label in {"High", "Medium", "Limited"}
    assert view.next_actions


def test_executive_decision_is_defensive_when_candidate_is_missing():
    session = create_demo_recruitment_session()
    decision = DecisionBoardService().build(session)
    assert _build_executive_decision(None, decision) is None
