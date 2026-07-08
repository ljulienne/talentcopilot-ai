from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.hybrid_matching.explainability_engine import HybridExplainabilityEngine


def test_explainable_hybrid_matching_generates_breakdown():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Loretta Danielson",
            role_title="HR Director",
            candidate_skills=["HRIS", "Leadership", "Change Management"],
            required_skills=["HRIS", "Leadership", "Payroll"],
            years_experience=18,
            titles=["HR Manager", "HR Director"],
            achievements=["Reduced HR costs by $5M.", "Managed 45 HR professionals."],
            responsibilities=["Led HR transformation and managed teams."],
        )
    )

    assert report.explanation_report is not None
    assert report.explanation_report.breakdown.final_score >= 50
    assert report.explanation_report.positive_contributions
    assert report.explanation_report.recruiter_summary


def test_explainability_penalizes_missing_skills():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Candidate",
            role_title="HRIS Manager",
            candidate_skills=["Graphic Design"],
            required_skills=["HRIS", "Payroll"],
            years_experience=2,
        )
    )

    assert report.explanation_report.penalties
    assert report.hybrid_score < 60


def test_explainability_engine_direct():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Vincent Blakoe",
            role_title="HRIS Lead",
            candidate_skills=["SIRH", "OCTIME", "Business Objects"],
            required_skills=["HRIS", "Time Management", "Reporting"],
            years_experience=13,
            achievements=["Improved adoption by 35%."],
        )
    )

    explanation = HybridExplainabilityEngine().explain(report)
    assert explanation.breakdown.final_score >= 60
    assert explanation.positive_contributions
