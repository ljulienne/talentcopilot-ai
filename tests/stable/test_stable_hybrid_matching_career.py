from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.services.hybrid_intelligence_demo_service import HybridIntelligenceDemoService


def test_hybrid_matching_includes_career_report():
    report = HybridMatchingEngine().analyze(
        HybridMatchingInput(
            candidate_name="Vincent Blakoe",
            role_title="HRIS Lead",
            candidate_skills=["SIRH", "Workday", "OCTIME"],
            required_skills=["HRIS", "Time Management"],
            years_experience=13,
            titles=["HRIS Consultant", "HRIS Project Manager", "HRIS Lead"],
            achievements=["Improved adoption by 35%."],
            responsibilities=["Led HRIS transformation and stakeholder management."],
        )
    )

    assert report.semantic_score >= 70
    assert report.career_score >= 60
    assert report.hybrid_score >= 70
    assert report.career_report is not None


def test_hybrid_demo_score():
    demo = HybridIntelligenceDemoService().run_demo()

    assert demo.report.hybrid_score >= 70
    assert demo.report.career_report.seniority_level in {"Senior", "Senior+", "Executive"}
