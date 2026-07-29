from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HiringBudgetInput:
    target_salary: float
    maximum_salary: float
    minimum_salary: float = 0.0
    currency: str = "EUR"
    target_bonus_percent: float = 0.0
    benefits_budget: float = 0.0
    relocation_budget: float = 0.0
    agency_fee: float = 0.0
    signing_bonus: float = 0.0
    onboarding_cost: float = 0.0
    first_year_cost_limit: float = 0.0
    notes: str = ""


@dataclass
class CandidateCostInput:
    candidate_name: str
    expected_salary: float
    relocation_required: bool = False
    notice_period_weeks: int = 0
    visa_sponsorship_required: bool = False
    variable_compensation: float = 0.0
    benefits_value: float = 0.0
    signing_bonus_requested: float = 0.0
    relocation_support_requested: float = 0.0
    benefits_requested: str = ""
    availability_date: str = ""
    flexibility: str = "Unknown"
    notes: str = ""
    currency: str = "EUR"


@dataclass
class CandidateBudgetAssessment:
    candidate_name: str
    fit_score: float
    expected_salary: Optional[float]
    salary_gap: Optional[float]
    budget_fit: Optional[int]
    cost_impact: str
    feasibility: str
    recommendation: str
    rationale: str
    next_actions: List[str] = field(default_factory=list)
    talent_recommendation: str = "Review"
    compensation_data_status: str = "Available"
    budget_recommendation: str = "Review"
    requested_package: Optional[float] = None
    total_first_year_cost: Optional[float] = None
    package_gap: Optional[float] = None
    benefits_requested: str = ""
    availability_date: str = ""
    flexibility: str = "Unknown"
    currency: str = "EUR"


@dataclass
class HiringBudgetReport:
    role_title: str
    target_salary: float
    maximum_salary: float
    assessments: List[CandidateBudgetAssessment] = field(default_factory=list)
    minimum_salary: float = 0.0
    currency: str = "EUR"
    first_year_cost_limit: float = 0.0
