from talentcopilot.decision_core.budget_intelligence_models import BudgetContext, CandidateCompensation
from talentcopilot.decision_core.candidate_decision_profile_service import CandidateDecisionProfileService
from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements


def test_zero_fit_candidate_is_rejected():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "David Smith", "skills": ["Graphic Design"], "years_experience": 1},
        "Transformation Lead",
        RoleRequirements(
            "Transformation Lead",
            required_skills=["Project Management", "Stakeholder Management"],
            minimum_years_experience=6,
        ),
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=50000),
    )

    assert profile.fit_score < 30
    assert profile.recommendation == "Reject"


def test_strong_fit_over_budget_gets_compensation_review():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {
            "name": "Alice Martin",
            "skills": ["Project Management", "Stakeholder Management", "HRIS"],
            "years_experience": 10,
            "achievements": ["Improved adoption by 35%"],
        },
        "Transformation Lead",
        RoleRequirements(
            "Transformation Lead",
            required_skills=["Project Management", "Stakeholder Management"],
            preferred_skills=["HRIS"],
            minimum_years_experience=6,
        ),
        BudgetContext(target_salary=85000, maximum_salary=100000),
        CandidateCompensation(expected_salary=125000),
    )

    assert profile.fit_score >= 80
    assert profile.recommendation == "Review Compensation Feasibility"


def test_recommendation_trace_step_exists():
    profile = CandidateDecisionProfileService().build_from_candidate_dict(
        {"name": "Alice Martin", "skills": ["Leadership"], "years_experience": 8},
        "Leadership Role",
        RoleRequirements("Leadership Role", required_skills=["Leadership"], minimum_years_experience=5),
    )

    assert "GENERATE_FINAL_RECOMMENDATION" in [step.action for step in profile.decision_trace.steps]
