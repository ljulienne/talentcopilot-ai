from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput


def test_orchestrated_decision_trace_has_required_steps():
    output = DecisionCoreOrchestrator().analyze_candidate(
        DecisionCoreInput(
            candidate={"name": "Alice Martin", "skills": ["Leadership"]},
            role_title="Transformation Lead",
            required_skills=["Leadership"],
        )
    )

    actions = [step.action for step in output.profile.decision_trace.steps]

    assert "CREATE_EVIDENCE_GRAPH" in actions
    assert "EVALUATE_EVIDENCE_QUALITY" in actions
    assert "EVALUATE_CANDIDATE_FIT" in actions
    assert "EVALUATE_HIRING_RISK" in actions
    assert "EVALUATE_ANALYSIS_CONFIDENCE" in actions
    assert "GENERATE_FINAL_RECOMMENDATION" in actions
    assert "GENERATE_EXECUTIVE_SUMMARY" in actions
