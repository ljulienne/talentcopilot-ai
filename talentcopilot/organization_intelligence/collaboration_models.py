from __future__ import annotations

from dataclasses import dataclass, field

from talentcopilot.intelligence_core.models import OrganizationInsight


@dataclass(frozen=True)
class DepartmentCollaborationMetric:
    department: str
    employee_count: int
    internal_links: int
    external_links: int
    partner_departments: int
    collaboration_score: int
    risk_level: str


@dataclass(frozen=True)
class DepartmentPairMetric:
    department_a: str
    department_b: str
    inferred_links: int
    collaboration_score: int
    risk_level: str


@dataclass(frozen=True)
class CollaborationBroker:
    employee_id: str
    name: str
    department: str
    total_relationships: int
    cross_department_links: int
    departments_reached: int
    dependency_level: str


@dataclass(frozen=True)
class CollaborationDiagnostic:
    employee_count: int
    department_count: int
    overall_collaboration_score: int
    overall_health: str
    silo_count: int
    broker_count: int
    weak_pair_count: int
    departments: tuple[DepartmentCollaborationMetric, ...] = field(default_factory=tuple)
    department_pairs: tuple[DepartmentPairMetric, ...] = field(default_factory=tuple)
    brokers: tuple[CollaborationBroker, ...] = field(default_factory=tuple)
    insights: tuple[OrganizationInsight, ...] = field(default_factory=tuple)
    recommendations: tuple[str, ...] = field(default_factory=tuple)
