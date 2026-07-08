from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.interview_engine import HybridInterviewFocusEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput

def test_hybrid_interview_focus_questions_created():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Candidate",
            role_title="HRIS Manager",
            candidate_skills=["Graphic Design"],
            required_skills=["HRIS", "Payroll"],
            years_experience=2,
        )
    )
    assert report.recruiter_report.structured_interview_questions
    assert report.recruiter_report.structured_interview_questions[0].question

def test_interview_focus_engine_direct():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Vincent Blakoe",
            role_title="HRIS Lead",
            candidate_skills=["SIRH", "OCTIME"],
            required_skills=["HRIS", "Payroll", "Reporting"],
            years_experience=13,
            achievements=["Improved adoption by 35%."],
        )
    )
    plan = HybridInterviewFocusEngine().build(report)
    assert plan.total_questions >= 1
    assert any(q.focus_area for q in plan.questions)

def test_structured_questions_have_evaluation_criteria():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Loretta Danielson",
            role_title="HR Director",
            candidate_skills=["HRIS", "Leadership"],
            required_skills=["HRIS", "Payroll"],
            years_experience=18,
        )
    )
    questions = report.recruiter_report.structured_interview_questions
    assert questions
    assert all(q.evaluation_criterion for q in questions)
    assert all(q.strong_signal for q in questions)
    assert all(q.red_flag for q in questions)
