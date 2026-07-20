from talentcopilot.models.hiring_budget import HiringBudgetInput
from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
    SessionStatus,
)
from talentcopilot.services.hiring_budget_service import HiringBudgetService


def _session():
    analyses = [
        CandidateAnalysisState("Louis Julienne", "louis", CandidateAnalysisStatus.ANALYZED, 84, rank=1),
        CandidateAnalysisState("Vincent Blakoe", "vincent", CandidateAnalysisStatus.ANALYZED, 80, rank=2),
        CandidateAnalysisState("Zelma O'Reilly", "zelma", CandidateAnalysisStatus.ANALYZED, 66, rank=3),
        CandidateAnalysisState("Loretta Danielson", "loretta", CandidateAnalysisStatus.ANALYZED, 56, rank=4),
    ]
    return RecruitmentSession(
        session_id="budget-consistency",
        job={"title": "HRIS Manager"},
        candidates=[
            {"candidate_id": "louis", "name": "Louis Julienne"},
            {"candidate_id": "vincent", "name": "Vincent Blakoe"},
            {"candidate_id": "zelma", "name": "Zelma O'Reilly"},
            {"candidate_id": "loretta", "name": "Loretta Danielson"},
        ],
        status=SessionStatus.COMPLETED,
        analyses=analyses,
    )


def test_missing_salary_never_creates_fictional_budget_fit():
    report = HiringBudgetService().build(
        _session(), HiringBudgetInput(85000, 100000)
    )
    assert len(report.assessments) == 4
    assert all(item.expected_salary is None for item in report.assessments)
    assert all(item.budget_fit is None for item in report.assessments)
    assert all(item.budget_recommendation == "Pending compensation data" for item in report.assessments)


def test_talent_recommendations_are_not_overwritten_by_budget_fallback():
    report = HiringBudgetService().build(
        _session(), HiringBudgetInput(85000, 100000)
    )
    recommendations = [item.talent_recommendation for item in report.assessments]
    assert len(set(recommendations)) > 1
    assert recommendations[0] != "Review"


def test_real_salary_data_enables_budget_assessment():
    session = _session()
    session.candidates[0]["expected_salary"] = 98000
    report = HiringBudgetService().build(
        session, HiringBudgetInput(85000, 100000)
    )
    louis = report.assessments[0]
    assert louis.expected_salary == 98000
    assert louis.budget_fit is not None
    assert louis.compensation_data_status == "Available"
