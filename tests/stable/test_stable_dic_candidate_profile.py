from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService


def test_candidate_decision_profile_builds():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management"],
        "years_experience": 8,
    }

    profile = CandidateDecisionProfileService().build_from_candidate_dict(candidate, "Transformation Lead")

    assert profile.candidate_name == "Alice Martin"
    assert profile.role_title == "Transformation Lead"
    assert profile.evidence_graph.nodes
    assert profile.decision_trace.steps
    assert profile.is_ready_for_decision_core()
    assert profile.metadata["profile_version"] == "dic-v2.0-alpha-b"
    assert "evidence_readiness_score" in profile.metadata


def test_candidate_decision_profile_build_many():
    profiles = CandidateDecisionProfileService().build_many(
        [
            {"name": "Alice Martin", "skills": ["HRIS"]},
            {"name": "David Smith", "skills": []},
        ],
        "Transformation Lead",
    )

    assert len(profiles) == 2
    assert profiles[0].profile_id != profiles[1].profile_id
