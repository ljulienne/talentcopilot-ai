from talentcopilot.models.hiring_budget import CandidateCostInput, HiringBudgetInput
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_low_fit_candidate_rejected_even_if_affordable():
    service = HiringBudgetService()
    assessment = service.assess_candidate(
        CandidateCostInput("David Smith", expected_salary=50000),
        HiringBudgetInput(target_salary=85000, maximum_salary=100000),
        fit_score=0,
    )

    assert assessment.recommendation == "Reject"
    assert assessment.fit_score == 0


def test_strong_candidate_over_budget_gets_compensation_review():
    service = HiringBudgetService()
    assessment = service.assess_candidate(
        CandidateCostInput("Alice Martin", expected_salary=120000),
        HiringBudgetInput(target_salary=85000, maximum_salary=100000),
        fit_score=92,
    )

    assert assessment.recommendation == "Review Compensation Feasibility"
    assert assessment.budget_fit < 60


def test_hiring_budget_imports():
    module = __import__("talentcopilot.ui.hiring_budget", fromlist=["render_hiring_budget"])
    assert hasattr(module, "render_hiring_budget")


def test_hiring_budget_navigation():
    page = get_page_by_label("Hiring Budget")
    assert page is not None
    assert page.module == "talentcopilot.ui.hiring_budget"
    assert page.function == "render_hiring_budget"
