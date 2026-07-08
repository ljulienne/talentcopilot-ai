from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_executive_summary_in_profile_metadata():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 8},
        "Leadership Role",
        RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=5),
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=90000),
    )

    assert "executive_summary" in profile.metadata
    assert "recruiter_summary" in profile.metadata
    assert profile.recommendation in profile.metadata["executive_summary"]


def test_executive_trace_step_exists():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 8},
        "Leadership Role",
        RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=5),
    )

    assert "GENERATE_EXECUTIVE_SUMMARY" in [step.action for step in profile.decision_trace.steps]
