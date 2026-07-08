from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_decision_trace_contains_evidence_fit_and_risk_steps():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"]},
        "Transformation Lead",
        RoleRequirements("Transformation Lead", required_skills=["Leadership"]),
    )

    engines = [step.engine for step in profile.decision_trace.steps]
    actions = [step.action for step in profile.decision_trace.steps]

    assert "EvidenceGraphBuilder" in engines
    assert "EvidenceIntelligenceEngine" in engines
    assert "FitIntelligenceEngine" in engines
    assert "RiskIntelligenceEngine" in engines
    assert "CREATE_EVIDENCE_GRAPH" in actions
    assert "EVALUATE_EVIDENCE_QUALITY" in actions
    assert "EVALUATE_CANDIDATE_FIT" in actions
    assert "EVALUATE_HIRING_RISK" in actions
