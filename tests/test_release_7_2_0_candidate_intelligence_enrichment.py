from types import SimpleNamespace

from talentcopilot.models.recruitment_session import CandidateAnalysisState, CandidateAnalysisStatus, RecruitmentSession, SessionStatus
from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService


def _session():
    analysis = CandidateAnalysisState(
        candidate_name="Louis Julienne",
        candidate_id="louis",
        status=CandidateAnalysisStatus.ANALYZED,
        match_score=78.0,
        rank=1,
        score_breakdown={"mission_fit_rank": 1, "confidence": 82},
        decision_report=SimpleNamespace(
            recommendation="Proceed with validation",
            executive_summary="Strong HRIS transformation profile with targeted validation required.",
            concerns=[],
            interview_focus=[],
        ),
    )
    return RecruitmentSession(
        session_id="release-7-2-0",
        job={
            "title": "HRIS Manager",
            "required_skills": ["Project Management", "SAP SuccessFactors", "Budget Management"],
        },
        candidates=[{
            "candidate_id": "louis",
            "name": "Louis Julienne",
            "title": "HRIS Manager",
            "skills": ["Project Management", "Budget Management", "HRIS"],
            "achievements": [
                "Led an HRIS transformation across 6 countries and managed a regional project budget.",
                "Improved user adoption by 35% through governance and change management.",
            ],
        }],
        status=SessionStatus.COMPLETED,
        analyses=[analysis],
    )


def test_candidate_intelligence_has_distinct_skill_assessments():
    report = CandidateWorkspaceService().build_all(_session())[0]
    levels = {skill.name: skill.level for skill in report.skills}
    assert levels["Project Management"] != levels["SAP SuccessFactors"]
    assert levels["Budget Management"] != levels["SAP SuccessFactors"]
    assert all(skill.status for skill in report.skills)
    assert all(skill.confidence for skill in report.skills)


def test_candidate_intelligence_has_rich_evidence_and_candidate_specific_risks():
    report = CandidateWorkspaceService().build_all(_session())[0]
    assert report.evidence
    assert all(item.source and item.confidence and item.evidence_type for item in report.evidence)
    assert report.risks
    sap_risk = next(risk for risk in report.risks if "SAP SuccessFactors" in risk.title)
    assert sap_risk.classification in {"Validation point", "Probable risk"}
    assert sap_risk.related_requirement == "SAP SuccessFactors"
    assert "personally" in sap_risk.interview_question.lower()
    assert "No major risk detected" not in sap_risk.detail


def test_overview_and_interview_focus_are_enriched_without_changing_official_result():
    report = CandidateWorkspaceService().build_all(_session())[0]
    assert report.match_score == 78.0
    assert report.rank == 1
    assert report.recommendation_label in {"Proceed", "Proceed with validation"}
    assert report.recommendation_rationale
    assert report.next_action
    assert len(report.interview_focus) >= 4
    assert any(item.startswith("Positive signals") for item in report.interview_focus)
    assert any(item.startswith("Warning signals") for item in report.interview_focus)
