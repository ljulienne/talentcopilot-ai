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
