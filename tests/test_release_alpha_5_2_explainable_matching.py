from talentcopilot.models.candidate_workspace import (
    CandidateEvidence,
    CandidateRisk,
    CandidateSkill,
    CandidateWorkspaceReport,
)
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.ui.recruitment_decision_workspace import (
    ExplainableMatchView,
    _build_explainable_match,
)


def test_explainable_matching_preserves_existing_score_and_uses_report_data():
    session = create_demo_recruitment_session()
    report = CandidateWorkspaceService().build_all(session)[0]

    view = _build_explainable_match(report)

    assert isinstance(view, ExplainableMatchView)
    assert view.score == report.match_score
    assert view.evidence_quality in {"High", "Medium", "Limited"}
    assert view.drivers
    assert view.gaps
    assert "unchanged" in view.evidence_summary.lower()


def test_explainable_matching_is_defensive_with_sparse_data():
    report = CandidateWorkspaceReport(
        candidate_name="Sparse Candidate",
        rank=1,
        match_score=51,
        recommendation="Review",
        executive_summary="Limited data.",
        skills=[],
        evidence=[],
        risks=[],
        interview_focus=[],
    )

    view = _build_explainable_match(report)

    assert view is not None
    assert view.score == 51
    assert view.evidence_quality == "Limited"
    assert not view.drivers
    assert view.gaps
    assert not view.source_facts


def test_explainable_matching_orders_drivers_and_surfaces_risks():
    report = CandidateWorkspaceReport(
        candidate_name="Alice",
        rank=1,
        match_score=88,
        recommendation="Proceed",
        executive_summary="Strong fit.",
        skills=[
            CandidateSkill("Communication", 70, "Profile evidence"),
            CandidateSkill("Leadership", 95, "Led a global team"),
        ],
        evidence=[
            CandidateEvidence("Leadership", "Managed 40 people", "High"),
            CandidateEvidence("Delivery", "Delivered global rollout", "High"),
        ],
        risks=[CandidateRisk("Budget ownership", "Not evidenced", "Medium")],
        interview_focus=[],
    )

    view = _build_explainable_match(report)

    assert view.drivers[0][0] == "Leadership"
    assert view.drivers[0][1] == 95
    assert "Budget ownership" in view.gaps
    assert "Managed 40 people" in view.source_facts
