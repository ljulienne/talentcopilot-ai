from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_candidate_decision_profile_builds_after_orchestrator_patch():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Project Management"], "years_experience": 8},
        "Transformation Lead",
        RoleRequirements("Transformation Lead", required_skills=["Project Management"], minimum_years_experience=5),
    )

    assert profile.metadata["profile_version"] == "dic-v2.0-alpha-i"
    assert profile.recommendation is not None
    assert "executive_summary" in profile.metadata


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
