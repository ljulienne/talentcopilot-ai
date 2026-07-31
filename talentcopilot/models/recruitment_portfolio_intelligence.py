"""Cross-project recruitment portfolio intelligence models.

The models in this module describe operational signals derived only from
persisted project metadata and workflow state. They never recalculate or
reinterpret official candidate scores or ranks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class PortfolioAlert:
    project_id: str
    project_title: str
    severity: str
    category: str
    summary: str
    recommended_action: str
    lifecycle: str
    owner: str
    priority: str
    activity_age_days: int | None


@dataclass(frozen=True)
class PortfolioLifecycleMetric:
    lifecycle: str
    label: str
    project_count: int
    candidate_count: int


@dataclass(frozen=True)
class PortfolioOwnerLoad:
    owner: str
    project_count: int
    critical_or_high_count: int
    decision_ready_count: int
    attention_count: int


@dataclass(frozen=True)
class PortfolioFreshnessMetric:
    band: str
    label: str
    project_count: int


@dataclass(frozen=True)
class RecruitmentPortfolioIntelligenceReport:
    generated_at: str
    active_project_count: int
    candidate_count: int
    decision_ready_count: int
    decided_count: int
    attention_project_count: int
    stale_project_count: int
    unassigned_project_count: int
    critical_project_count: int
    lifecycle_metrics: Tuple[PortfolioLifecycleMetric, ...] = field(default_factory=tuple)
    owner_load: Tuple[PortfolioOwnerLoad, ...] = field(default_factory=tuple)
    freshness_metrics: Tuple[PortfolioFreshnessMetric, ...] = field(default_factory=tuple)
    alerts: Tuple[PortfolioAlert, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    limitation: str = (
        "Portfolio signals use saved workflow state and last-activity timestamps. "
        "They do not estimate time-to-hire or change candidate scores, ranks or evidence."
    )
