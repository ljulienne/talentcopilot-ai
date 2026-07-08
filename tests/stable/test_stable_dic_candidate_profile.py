from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_candidate_decision_profile_builds():
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
    )

    assert profile.candidate_name == "Alice Martin"
    assert profile.role_title == "Transformation Lead"
    assert profile.evidence_graph.nodes
    assert profile.decision_trace.steps
    assert profile.is_ready_for_decision_core()
    assert profile.metadata["profile_version"] == "dic-v2.0-alpha-d"
    assert profile.fit_score is not None
    assert profile.risk_level is not None
    assert "risk_score" in profile.metadata


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
