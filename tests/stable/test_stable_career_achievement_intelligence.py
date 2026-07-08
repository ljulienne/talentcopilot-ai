from talentcopilot.career_intelligence.achievement_engine import AchievementIntelligenceEngine
from talentcopilot.career_intelligence.career_engine import CareerIntelligenceEngine


def test_achievement_engine_detects_impact_leadership_transformation():
    signals = AchievementIntelligenceEngine().analyze(
        achievements=[
            "Led HRIS transformation across 5 countries.",
            "Improved adoption by 35%.",
            "Reduced payroll errors by 40%.",
        ],
        responsibilities=["Managed stakeholders and change management activities."],
    )

    categories = {signal.category for signal in signals}
    assert "Impact" in categories
    assert "Leadership" in categories
    assert "Transformation" in categories


def test_career_engine_seniority_and_score():
    report = CareerIntelligenceEngine().analyze(
        candidate_name="Loretta Danielson",
        years_experience=18,
        titles=["HR Manager", "HR Director"],
        achievements=["Reduced HR costs by $5M.", "Managed 45 HR professionals."],
    )

    assert report.seniority_level == "Executive"
    assert report.career_score >= 70
    assert report.impact_score >= 60
