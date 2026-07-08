from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_candidate_decision_profile_builds_with_confidence():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management"],
        "years_experience": 8,
    }
    role = RoleRequirements(
        role_title="Transformation Lead",
        required_skills=["Project Management"],
        minimum_years_experience=5,
    )

    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        candidate,
        "Transformation Lead",
        role,
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=120000),
    )

    assert profile.metadata["profile_version"] == "dic-v2.0-alpha-f"
    assert profile.fit_score is not None
    assert profile.risk_level is not None
    assert profile.confidence_score is not None
    assert "confidence_score" in profile.metadata
    assert "decision_quality" in profile.metadata


def test_candidate_decision_profile_build_many():
    role = RoleRequirements("Transformation Lead", required_skills=["HRIS"])
    profiles = CandidateDecisionProfileService().build_many(
        [
            {"name": "Alice Martin", "skills": ["HRIS"]},
            {"name": "David Smith", "skills": []},
        ],
        "Transformation Lead",
        role,
    )

    assert len(profiles) == 2
    assert profiles[0].profile_id != profiles[1].profile_id
