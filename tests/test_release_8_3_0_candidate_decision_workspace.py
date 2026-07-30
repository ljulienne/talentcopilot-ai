from pathlib import Path
from types import SimpleNamespace

from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.candidate_decision_workspace_service import (
    CandidateDecisionWorkspaceService,
)
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
import talentcopilot.services.recruitment_workflow_state as workflow_state


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_UI = (ROOT / "talentcopilot/ui/candidate_workspace.py").read_text(encoding="utf-8")
COMPARISON_UI = (ROOT / "talentcopilot/ui/comparison_workspace.py").read_text(encoding="utf-8")
DECISION_UI = (ROOT / "talentcopilot/ui/decision_board.py").read_text(encoding="utf-8")
SERVICE_SOURCE = (ROOT / "talentcopilot/services/candidate_decision_workspace_service.py").read_text(encoding="utf-8")
PDF_SOURCE = (ROOT / "talentcopilot/services/recruitment_pdf_service.py").read_text(encoding="utf-8")


def _competency(name, *, required, pre, post=None, evidence="Strong evidence"):
    return SimpleNamespace(
        is_job_requirement=True,
        competency_name=name,
        required_level=required,
        ai_estimated_level=pre,
        interviewer_level=post,
        evidence_status=evidence,
        confidence="High",
        interview_priority="Confirm" if pre >= required else "Validate",
        validation_status="Validated" if post is not None else "Pending",
        evidence=f"Evidence for {name}",
    )


class _CompetencyService:
    def build(self, report, session):
        return SimpleNamespace(
            status="post_interview",
            active_competencies=lambda: [
                _competency("Enterprise negotiation", required=4.0, pre=3.0, post=4.2),
                _competency("Team leadership", required=4.0, pre=2.5, post=None, evidence="Limited evidence"),
            ],
        )


class _CompensationService:
    def load_expectation(self, session, *, candidate_id, candidate_name):
        return SimpleNamespace(
            documented=True,
            currency="EUR",
            expected_salary=95000.0,
            availability_date="2026-10-01",
            notice_period_weeks=8,
            flexibility="Moderate",
        )

    def load_budget(self, session):
        return SimpleNamespace()


class _BudgetService:
    def build(self, session, budget):
        return SimpleNamespace(
            assessments=[
                SimpleNamespace(
                    candidate_name="Alex Morgan",
                    budget_recommendation="Balanced negotiation",
                )
            ]
        )


def _workspace_view():
    report = SimpleNamespace(
        candidate_id="candidate-alex",
        candidate_name="Alex Morgan",
        official_match_score=78.0,
        match_score=78.0,
        official_rank=1,
        rank=1,
        recommendation_label="Proceed with human validation",
        recommendation="Proceed",
        score_breakdown={"confidence": 84},
        skills=[SimpleNamespace(name="Enterprise negotiation", level=82)],
        risks=[
            SimpleNamespace(
                title="Team leadership depth requires validation",
                detail="The CV does not establish the size of the directly managed team.",
                related_requirement="Team leadership",
            )
        ],
        interview_focus=["Validate direct team size and reporting lines."],
        executive_summary="Strong commercial profile with leadership evidence to validate.",
    )
    session = SimpleNamespace(role_title="Senior Sales Manager")
    context = RecruitmentWorkflowContext(
        interview_assessed_candidate_ids=["candidate-alex"],
        interview_evaluations={
            "candidate-alex": {
                "recommendation": "Proceed with conditions",
                "evidence_coverage": 80,
                "remaining_risks": ["Confirm direct people-management scope."],
            }
        },
        decision_recorded=True,
        final_decision_candidate_id="candidate-alex",
        final_decision_recommendation="Hire",
        final_decision_rationale="Commercial evidence and interview results support the hire.",
        final_decision_actor="Hiring Manager",
        final_decision_timestamp="2026-07-30T20:00:00+00:00",
        decision_history=[
            {
                "candidate_id": "candidate-alex",
                "recommendation": "Hire",
                "actor": "Hiring Manager",
                "timestamp": "2026-07-30T20:00:00+00:00",
            }
        ],
    )
    brief = SimpleNamespace(
        confidence_score=84,
        evidence_coverage=72,
        recommendation_label="Proceed with human validation",
        strengths=("Enterprise negotiation", "Pipeline management"),
        interview_priorities=("Validate direct team size and reporting lines.",),
    )
    service = CandidateDecisionWorkspaceService(
        competency_service=_CompetencyService(),
        compensation_service=_CompensationService(),
        budget_service=_BudgetService(),
    )
    return service.build(report, session, context, brief), report


def test_candidate_decision_workspace_preserves_official_score_and_rank():
    view, _ = _workspace_view()
    assert view.official_match_score == 78.0
    assert view.official_rank == 1
    assert view.interview_status == "Completed"
    assert view.interview_recommendation == "Proceed with conditions"
    assert view.final_decision_recommendation == "Hire"
    assert view.compensation_fit == "Balanced negotiation"
    assert view.expected_salary == 95000.0
    assert view.availability_date == "2026-10-01"


def test_requirement_coverage_keeps_pre_and_post_interview_layers_separate():
    view, _ = _workspace_view()
    negotiation = next(item for item in view.requirements if item.requirement == "Enterprise negotiation")
    leadership = next(item for item in view.requirements if item.requirement == "Team leadership")
    assert negotiation.pre_interview_level == 3.0
    assert negotiation.post_interview_level == 4.2
    assert negotiation.current_status == "Demonstrated"
    assert leadership.pre_interview_level == 2.5
    assert leadership.post_interview_level is None
    assert leadership.current_status == "Validate"


def test_decision_journey_contains_three_independent_stages():
    view, _ = _workspace_view()
    assert [item.key for item in view.journey] == [
        "pre_interview",
        "interview",
        "final_decision",
    ]
    assert view.journey[0].evidence_note == "Official Talent Fit 78% · official rank #1."
    assert view.journey[1].status == "Completed"
    assert view.journey[2].status == "Recorded"


def test_candidate_pdf_uses_the_same_consolidated_decision_view():
    view, report = _workspace_view()
    export = RecruitmentPdfService().candidate(report, decision_view=view)
    assert export.data.startswith(b"%PDF")
    assert export.file_name == "talentcopilot_candidate_candidate-alex.pdf"
    for marker in (
        "decision_view: Any | None = None",
        "Decision journey",
        "Role requirement coverage",
        "Final human decision",
        "Official Talent Fit and rank are reproduced without recalculation",
    ):
        assert marker in PDF_SOURCE


def test_final_decision_records_owner_evidence_risks_timestamp_and_history(monkeypatch):
    context = RecruitmentWorkflowContext()
    monkeypatch.setattr(workflow_state, "get_workflow_context", lambda: context)
    monkeypatch.setattr(workflow_state, "save_workflow_context", lambda value: value)

    saved = workflow_state.save_final_decision(
        "candidate-alex",
        "Proceed with conditions",
        "Strong fit with one managed risk.",
        actor="Recruiter Lead",
        evidence=["Evidence A", "Evidence A", "Evidence B"],
        accepted_risks=["Risk A"],
    )

    assert saved.decision_recorded is True
    assert saved.final_decision_actor == "Recruiter Lead"
    assert saved.final_decision_timestamp
    assert saved.final_decision_evidence == ["Evidence A", "Evidence B"]
    assert saved.final_decision_accepted_risks == ["Risk A"]
    assert len(saved.decision_history) == 1
    assert saved.decision_history[0]["candidate_id"] == "candidate-alex"


def test_ui_exposes_consolidated_workspace_and_independent_decision_matrix():
    for marker in (
        "CandidateDecisionWorkspaceService",
        "Candidate decision workspace",
        "Decision journey",
        "Role requirement coverage",
        "Compensation and availability",
        "decision_view=decision_view",
    ):
        assert marker in CANDIDATE_UI

    for marker in (
        '"Talent Fit"',
        '"Evidence Confidence"',
        '"Critical Risk"',
        '"Interview Assessment"',
        '"Compensation Fit"',
        '"Availability"',
        '"Final Recommendation"',
    ):
        assert marker in COMPARISON_UI


def test_decision_board_requires_a_human_owner_and_audits_decision_changes():
    for marker in (
        "Decision owner",
        "Decisive evidence",
        "Risks accepted or conditionally managed",
        "actor=owner",
        "evidence=decisive_evidence",
        "accepted_risks=accepted_risks",
        "Decision audit history",
    ):
        assert marker in DECISION_UI


def test_release_is_presentation_and_traceability_only():
    assert "never recalculates official Talent Fit" in SERVICE_SOURCE
    assert "official_match_score" in SERVICE_SOURCE
    assert "official_rank" in SERVICE_SOURCE
    assert "real_ranking" not in CANDIDATE_UI
    assert "matching_output" not in CANDIDATE_UI
