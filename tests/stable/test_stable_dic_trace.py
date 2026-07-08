from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService


def test_decision_trace_contains_evidence_steps():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"]},
        "Transformation Lead",
    )

    engines = [step.engine for step in profile.decision_trace.steps]
    actions = [step.action for step in profile.decision_trace.steps]

    assert "EvidenceGraphBuilder" in engines
    assert "CREATE_EVIDENCE_GRAPH" in actions
    assert "CALCULATE_EVIDENCE_COVERAGE" in actions
