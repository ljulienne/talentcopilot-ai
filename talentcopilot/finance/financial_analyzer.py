from __future__ import annotations

from typing import Any, Dict


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def calculate_salary_gap(expected_salary: Any, budget_max: Any) -> float:
    return _safe_float(expected_salary) - _safe_float(budget_max)


def calculate_budget_fit_score(expected_salary: Any, budget_min: Any, budget_max: Any) -> int:
    expected = _safe_float(expected_salary)
    minimum = _safe_float(budget_min)
    maximum = _safe_float(budget_max)

    if expected <= 0 or maximum <= 0:
        return 0

    if minimum > 0 and minimum <= expected <= maximum:
        return 100

    if expected < minimum:
        return 90

    gap = expected - maximum
    gap_ratio = gap / maximum

    if gap_ratio <= 0.05:
        return 85

    if gap_ratio <= 0.10:
        return 70

    if gap_ratio <= 0.20:
        return 50

    return 25


def get_budget_verdict(expected_salary: Any, budget_min: Any, budget_max: Any) -> str:
    score = calculate_budget_fit_score(expected_salary, budget_min, budget_max)
    gap = calculate_salary_gap(expected_salary, budget_max)

    if score >= 90:
        return "Within budget"

    if score >= 80:
        return "Slightly above budget"

    if score >= 60:
        return "Negotiation required"

    if gap > 0:
        return "Above budget"

    return "Budget data incomplete"


def analyze_candidate_financial_fit(
    candidate_name: str,
    expected_salary: Any,
    budget_min: Any,
    budget_max: Any,
    currency: str = "EUR",
) -> Dict[str, Any]:
    salary_gap = calculate_salary_gap(expected_salary, budget_max)
    budget_fit_score = calculate_budget_fit_score(expected_salary, budget_min, budget_max)
    verdict = get_budget_verdict(expected_salary, budget_min, budget_max)

    return {
        "candidate_name": candidate_name,
        "expected_salary": _safe_float(expected_salary),
        "budget_min": _safe_float(budget_min),
        "budget_max": _safe_float(budget_max),
        "currency": currency,
        "salary_gap": salary_gap,
        "budget_fit_score": budget_fit_score,
        "verdict": verdict,
    }


def generate_financial_summary(analysis: Dict[str, Any]) -> str:
    name = analysis.get("candidate_name", "This candidate")
    currency = analysis.get("currency", "EUR")
    expected_salary = analysis.get("expected_salary", 0)
    budget_max = analysis.get("budget_max", 0)
    salary_gap = analysis.get("salary_gap", 0)
    verdict = analysis.get("verdict", "Budget data incomplete")

    if expected_salary <= 0 or budget_max <= 0:
        return f"{name} does not have enough salary or budget data for a reliable financial assessment."

    if salary_gap <= 0:
        return (
            f"{name} is within the recruitment budget. Expected salary is "
            f"{expected_salary:,.0f} {currency}, compared with a maximum budget of "
            f"{budget_max:,.0f} {currency}."
        )

    return (
        f"{name} is {salary_gap:,.0f} {currency} above the maximum budget. "
        f"Verdict: {verdict}."
    )
