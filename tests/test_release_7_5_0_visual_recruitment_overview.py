from pathlib import Path

from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService
from talentcopilot.services.recruitment_overview_service import RecruitmentOverviewService
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService
from talentcopilot.ui.enterprise_navigation import get_page_by_label
from talentcopilot.ui.recruitment_workflow_shell import aggregate_workflow_steps


ROOT = Path(__file__).resolve().parents[1]
OVERVIEW_SOURCE = (ROOT / "talentcopilot/ui/recruitment_overview.py").read_text(encoding="utf-8")
SHELL_SOURCE = (ROOT / "talentcopilot/ui/recruitment_workflow_shell.py").read_text(encoding="utf-8")


def _session() -> RecruitmentSession:
    return RecruitmentSession(
        session_id="overview-75",
        job={
            "job_id": "job-75",
            "title": "HRIS Transformation Lead",
            "required_skills": ["HRIS", "Change Management", "Stakeholder Management"],
            "required_levels": {
                "HRIS": 4,
                "Change Management": 4,
                "Stakeholder Management": 3,
            },
        },
        candidates=[
            {
                "candidate_id": "c1",
                "name": "Maria Garcia",
                "skills": ["HRIS", "Change Management", "Stakeholder Management"],
                "achievements": ["Led an HRIS rollout across 8 countries with 91% adoption."],
            },
            {
                "candidate_id": "c2",
                "name": "David Smith",
                "skills": ["HRIS", "Stakeholder Management"],
                "achievements": ["Managed HR systems stakeholders across three business units."],
            },
            {
                "candidate_id": "c3",
                "name": "Anna Wilson",
                "skills": ["Project Management"],
                "achievements": [],
            },
        ],
        analyses=[
            CandidateAnalysisState(
                candidate_id="c1",
                candidate_name="Maria Garcia",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=82,
                rank=1,
                score_breakdown={"confidence": 88},
            ),
            CandidateAnalysisState(
                candidate_id="c2",
                candidate_name="David Smith",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=61,
                rank=2,
                score_breakdown={"confidence": 70},
            ),
            CandidateAnalysisState(
                candidate_id="c3",
                candidate_name="Anna Wilson",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=22,
                rank=3,
                score_breakdown={"confidence": 42},
            ),
        ],
        status=SessionStatus.COMPLETED,
    )


def test_visual_overview_is_a_primary_importable_page():
    page = get_page_by_label("Recruitment Overview")
    assert page is not None
    assert page.module == "talentcopilot.ui.recruitment_overview"
    module = __import__(page.module, fromlist=[page.function])
    assert hasattr(module, page.function)


def test_overview_uses_official_scores_without_recalculating_them(tmp_path):
    session = _session()
    original = [(item.match_score, item.rank) for item in session.analyses]
    competency_service = CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    view = RecruitmentOverviewService(competency_service=competency_service).build(
        session,
        RecruitmentWorkflowContext(),
    )

    assert [item.official_match_score for item in view.candidates] == [82.0, 61.0, 22.0]
    assert [item.official_rank for item in view.candidates] == [1, 2, 3]
    assert view.strong_fit_count == 1
    assert view.potential_fit_count == 1
    assert view.low_fit_count == 1
    assert [(item.match_score, item.rank) for item in session.analyses] == original


def test_post_interview_alignment_is_separate_and_versioned(tmp_path):
    session = _session()
    competency_service = CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    candidate_service = RecruitmentOverviewService(competency_service=competency_service).candidate_service
    report = candidate_service.build_all(session)[0]
    matrix = competency_service.build(report, session)
    updates = {
        item.competency_id: {
            "interviewer_level": item.required_level,
            "validation_status": "Confirmed",
            "interview_evidence": "Situation, responsibility, actions and measurable result were documented.",
        }
        for item in matrix.active_competencies()
        if item.is_job_requirement
    }
    competency_service.update(matrix, updates, evaluator="Recruiter", status="interview_in_progress")
    competency_service.finalize(matrix, evaluator="Recruiter")

    context = RecruitmentWorkflowContext(
        interview_assessed_candidate_ids=["c1"],
        interview_evaluations={"c1": {"evidence_coverage": 100}},
    )
    view = RecruitmentOverviewService(competency_service=competency_service).build(session, context)
    maria = view.candidates[0]

    assert maria.official_match_score == 82.0
    assert maria.post_interview_alignment == 100.0
    assert maria.interview_status == "Completed"
    assert maria.interview_progress == 100
    assert maria.evidence_coverage == 100
    assert view.has_post_interview_data is True


def test_competency_coverage_and_next_action_are_decision_oriented(tmp_path):
    view = RecruitmentOverviewService(
        competency_service=CompetencyMatrixService(storage_dir=tmp_path / "matrices")
    ).build(_session(), RecruitmentWorkflowContext())

    assert view.competency_coverage
    assert {item.competency for item in view.competency_coverage} >= {
        "HRIS",
        "Change Management",
        "Stakeholder Management",
    }
    assert view.next_action_page == "Candidate Intelligence"
    assert view.next_action_button == "Review candidates"


def test_workflow_shell_collapses_technical_steps_into_four_user_stages():
    session = _session()
    states = RecruitmentWorkflowService().resolve_steps(
        session,
        RecruitmentWorkflowContext(),
        current_page="Recruitment Overview",
    )
    groups = aggregate_workflow_steps(states, current_page="Recruitment Overview")

    assert [item.label for item in groups] == [
        "Analyze",
        "Review candidates",
        "Interview",
        "Compare & decide",
    ]
    assert groups[0].current is True
    assert len(groups) == 4


def test_dashboard_contract_is_visual_progressive_and_presentation_only():
    for contract in (
        "st.plotly_chart",
        "Talent-pool distribution",
        "Competency coverage",
        "Interview assessment progress",
        "Recommended next action",
        "How to read these indicators",
        "Official role fit",
        "Post-interview competencies",
    ):
        assert contract in OVERVIEW_SOURCE

    assert "match_score =" not in OVERVIEW_SOURCE
    assert "official_rank =" not in OVERVIEW_SOURCE
    assert "grid-template-columns:repeat(4" in SHELL_SOURCE
    assert '"Recruitment Overview": "Recruitment Workspace"' in SHELL_SOURCE
