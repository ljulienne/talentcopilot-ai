from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.confidence_intelligence_engine import ConfidenceIntelligenceEngine
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_confidence_profile_has_confidence_score():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 8},
        "Leadership Role",
        RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=5),
    )

    assert profile.confidence_score is not None
    assert "confidence_level" in profile.metadata
    assert "decision_quality" in profile.metadata


def test_confidence_trace_completeness():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 8},
        "Leadership Role",
        RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=5),
    )

    assert "EVALUATE_ANALYSIS_CONFIDENCE" in [step.action for step in profile.decision_trace.steps]


def test_confidence_engine_level_boundaries():
    engine = ConfidenceIntelligenceEngine()
    assert engine._level(90) == "High"
    assert engine._level(70) == "Medium"
    assert engine._level(50) == "Low"
    assert engine._level(20) == "Very Low"
