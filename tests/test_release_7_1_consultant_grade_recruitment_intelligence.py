from types import SimpleNamespace

from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.recruitment.mission.state import build_recruitment_mission_state
from talentcopilot.recruitment_reasoning.engine import RecruitmentReasoningEngine


def test_mid_range_candidate_is_not_high_risk_by_score_alone():
    engine = RecruitmentReasoningEngine()
    job = """
    HRIS Manager. Minimum 10 years of experience. Human Resources required.
    HRIS and SAP are desirable. People leadership required.
    """
    cv = """
    Loretta Danielson. Human Resources leader with 10 years of experience.
    Supervised a team and led operational HR improvement initiatives.
    """
    result = engine.evaluate(job, cv, "Loretta Danielson")
    assert 40 <= result.score < 70
    assert result.risk_level == "Medium"
    assert "evidence uncertainty, not a confirmed capability gap" in result.rationale
    assert "Recommendation:" in result.rationale
    assert "\n\n" in result.rationale


def test_consultant_narrative_distinguishes_evidence_from_capability_gap():
    result = RecruitmentReasoningEngine().evaluate(
        "HRIS Manager requiring SAP, Power BI and change management.",
        "Candidate led HR operations and supervised a team.",
        "Candidate One",
    )
    assert "No evidence found for" not in result.rationale
    assert "does not provide sufficient evidence" in result.rationale
    assert "not a confirmed capability gap" in result.rationale


def _analysis(name, score=47, rank=1):
    return SimpleNamespace(
        candidate_id=name.lower().replace(" ", "-"),
        candidate_name=name,
        match_score=score,
        rank=rank,
        decision_score=score,
        score_breakdown={"mission_fit_rank": rank, "decision_rank": rank},
        official_rank=rank,
        official_match_score=score,
        official_decision_score=score,
        official_confidence_score=72,
        notes=[
            f"{name} presents a plausible but incomplete match.\n\n"
            "The available CV does not provide sufficient evidence to confirm the role-critical requirement for HRIS / HR systems function. "
            "This is an evidence uncertainty, not a confirmed capability gap.\n\n"
            "Recommendation: Review. Hiring risk is Medium."
        ],
        errors=[],
    )


def test_validation_focus_is_specific_and_decision_oriented():
    analysis = _analysis("Loretta Danielson")
    session = SimpleNamespace(
        session_id="s71",
        role_title="HRIS Manager",
        status="analyzed",
        candidate_count=1,
        analyzed_count=1,
        ranked_analyses=[analysis],
        candidates=[{"candidate_id": analysis.candidate_id, "name": analysis.candidate_name, "achievements": []}],
    )
    state = build_recruitment_mission_state(session)
    focus = state.candidates[0].validation_focus[0]
    assert "HRIS / HR systems function" in focus
    assert "genuine capability gap or simply under-documented" in focus
    assert "measurable outcome" in focus


def test_interview_risk_calibration_does_not_mark_every_sub_60_profile_high():
    analysis = _analysis("Loretta Danielson", score=47)
    session = SimpleNamespace(
        session_id="s71",
        role_title="HRIS Manager",
        ranked_analyses=[analysis],
        analyses=[analysis],
        candidates=[{
            "candidate_id": analysis.candidate_id,
            "name": analysis.candidate_name,
            "skills": ["Human Resources", "People Leadership"],
            "achievements": ["Supervised a team and improved an HR process"],
        }],
        job={"title": "HRIS Manager", "required_skills": ["HRIS", "SAP", "Power BI", "People Leadership"]},
    )
    report = InterviewWorkspaceService().build_all(session)[0]
    assert report.risk_level == "Medium"
    assert report.questions
    assert "Resolve the decision uncertainty" in report.questions[0].objective
