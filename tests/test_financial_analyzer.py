from talentcopilot.finance.financial_analyzer import (
    analyze_candidate_financial_fit,
    calculate_budget_fit_score,
    calculate_salary_gap,
    generate_financial_summary,
    get_budget_verdict,
)


def test_calculate_salary_gap():
    assert calculate_salary_gap(85000, 80000) == 5000
    assert calculate_salary_gap(75000, 80000) == -5000


def test_budget_fit_within_budget():
    assert calculate_budget_fit_score(75000, 70000, 85000) == 100
    assert get_budget_verdict(75000, 70000, 85000) == "Within budget"


def test_budget_fit_slightly_above_budget():
    assert calculate_budget_fit_score(87000, 70000, 85000) == 85
    assert get_budget_verdict(87000, 70000, 85000) == "Slightly above budget"


def test_budget_fit_above_budget():
    assert calculate_budget_fit_score(105000, 70000, 85000) == 25
    assert get_budget_verdict(105000, 70000, 85000) == "Above budget"


def test_analyze_candidate_financial_fit():
    analysis = analyze_candidate_financial_fit(
        candidate_name="Emma Martin",
        expected_salary=82000,
        budget_min=70000,
        budget_max=85000,
        currency="EUR",
    )

    assert analysis["candidate_name"] == "Emma Martin"
    assert analysis["budget_fit_score"] == 100
    assert analysis["salary_gap"] == -3000
    assert analysis["verdict"] == "Within budget"


def test_generate_financial_summary():
    analysis = analyze_candidate_financial_fit(
        candidate_name="John Smith",
        expected_salary=95000,
        budget_min=70000,
        budget_max=85000,
        currency="EUR",
    )

    summary = generate_financial_summary(analysis)

    assert "John Smith" in summary
    assert "above the maximum budget" in summary
