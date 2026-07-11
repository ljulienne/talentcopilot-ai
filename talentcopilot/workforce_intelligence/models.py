from __future__ import annotations

from dataclasses import dataclass, field

from talentcopilot.intelligence_core.models import OrganizationInsight


@dataclass(frozen=True)
class SuccessorCandidate:
    employee_id: str
    name: str
    department: str
    role: str
    readiness_score: int
    matched_skills: tuple[str, ...] = field(default_factory=tuple)
    missing_skills: tuple[str, ...] = field(default_factory=tuple)
    rationale: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DepartureImpact:
    employee_id: str
    employee_name: str
    department: str
    role: str
    lost_skills: tuple[str, ...]
    critical_lost_skills: tuple[str, ...]
    unique_skills_lost: tuple[str, ...]
    affected_departments: tuple[str, ...]
    successor_candidates: tuple[SuccessorCandidate, ...]
    risk_score: int
    risk_level: str
    executive_summary: str
    recommendations: tuple[str, ...] = field(default_factory=tuple)
    insights: tuple[OrganizationInsight, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class WorkforceScenarioReport:
    employee_count: int
    scenario_type: str
    subject_employee_id: str
    subject_employee_name: str
    impact: DepartureImpact
