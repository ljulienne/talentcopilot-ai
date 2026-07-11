from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class DecisionReadiness(str, Enum):
    READY = "Ready"
    REVIEW = "Review"
    NOT_READY = "Not ready"


class DecisionPriority(str, Enum):
    DO_NOW = "Do now"
    PLAN = "Plan"
    MONITOR = "Monitor"


class DecisionStatus(str, Enum):
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    IN_PROGRESS = "In progress"
    COMPLETED = "Completed"
    DISMISSED = "Dismissed"


class DecisionEffort(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass(frozen=True)
class Evidence:
    label: str
    detail: str
    source: str = "organization_data"
    strength: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("Evidence strength must be between 0 and 1.")


@dataclass(frozen=True)
class Recommendation:
    action: str
    priority: str
    timeframe: str
    business_value: str


@dataclass(frozen=True)
class OrganizationInsight:
    insight_id: str
    title: str
    category: str
    severity: Severity
    confidence: float
    current_situation: str
    business_impact: str
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    recommendations: tuple[Recommendation, ...] = field(default_factory=tuple)
    decision_readiness: DecisionReadiness = DecisionReadiness.REVIEW

    def __post_init__(self) -> None:
        if not self.insight_id.strip():
            raise ValueError("insight_id is required.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Insight confidence must be between 0 and 1.")

    @property
    def confidence_percent(self) -> int:
        return round(self.confidence * 100)

    @property
    def evidence_quality(self) -> str:
        if not self.evidence:
            return "Insufficient"
        weighted = sum(item.strength for item in self.evidence) / len(self.evidence)
        if len(self.evidence) >= 3 and weighted >= 0.8:
            return "Excellent"
        if len(self.evidence) >= 2 and weighted >= 0.65:
            return "Good"
        return "Limited"


@dataclass(frozen=True)
class AIDecision:
    decision_id: str
    title: str
    priority: DecisionPriority
    status: DecisionStatus
    business_impact: str
    effort: DecisionEffort
    horizon: str
    confidence: float
    source_insight_id: str
    source_insight_title: str
    rationale: str
    evidence: tuple[str, ...] = field(default_factory=tuple)
    business_value: str = ""

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id is required.")
        if not self.title.strip():
            raise ValueError("Decision title is required.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Decision confidence must be between 0 and 1.")

    @property
    def confidence_percent(self) -> int:
        return round(self.confidence * 100)


@dataclass(frozen=True)
class DecisionQueue:
    decisions: tuple[AIDecision, ...] = field(default_factory=tuple)

    @property
    def do_now_count(self) -> int:
        return sum(item.priority == DecisionPriority.DO_NOW for item in self.decisions)

    @property
    def plan_count(self) -> int:
        return sum(item.priority == DecisionPriority.PLAN for item in self.decisions)

    @property
    def monitor_count(self) -> int:
        return sum(item.priority == DecisionPriority.MONITOR for item in self.decisions)


@dataclass(frozen=True)
class ExecutiveBrief:
    headline: str
    overall_severity: Severity
    narrative: str
    priority_insights: tuple[OrganizationInsight, ...]
    recommended_decisions: tuple[str, ...]
    evidence_quality: str
    confidence: float
    decision_readiness: DecisionReadiness

    @property
    def confidence_percent(self) -> int:
        return round(self.confidence * 100)


def as_tuple(items: Iterable) -> tuple:
    return tuple(items)

@dataclass(frozen=True)
class DecisionEvent:
    event_id: str
    decision_id: str
    status: DecisionStatus
    occurred_at: str
    note: str = ""
    actor: str = "TalentCopilot user"


@dataclass(frozen=True)
class DecisionProgress:
    decision: AIDecision
    events: tuple[DecisionEvent, ...] = field(default_factory=tuple)

    @property
    def current_status(self) -> DecisionStatus:
        return self.events[-1].status if self.events else self.decision.status

    @property
    def last_updated(self) -> str:
        return self.events[-1].occurred_at if self.events else ""


@dataclass(frozen=True)
class DecisionTimeline:
    items: tuple[DecisionProgress, ...] = field(default_factory=tuple)

    @property
    def completed_count(self) -> int:
        return sum(item.current_status == DecisionStatus.COMPLETED for item in self.items)

    @property
    def active_count(self) -> int:
        return sum(
            item.current_status in {DecisionStatus.ACCEPTED, DecisionStatus.IN_PROGRESS}
            for item in self.items
        )

    @property
    def proposed_count(self) -> int:
        return sum(item.current_status == DecisionStatus.PROPOSED for item in self.items)

    @property
    def completion_rate(self) -> int:
        return round((self.completed_count / len(self.items)) * 100) if self.items else 0
