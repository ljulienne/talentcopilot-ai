from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_decision_trace_contains_executive_step():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"]},
        "Transformation Lead",
        RoleRequirements("Transformation Lead", required_skills=["Leadership"]),
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=120000),
    )

    actions = [step.action for step in profile.decision_trace.steps]

    assert "GENERATE_FINAL_RECOMMENDATION" in actions
    assert "GENERATE_EXECUTIVE_SUMMARY" in actions
