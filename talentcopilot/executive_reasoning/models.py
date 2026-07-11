from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ExecutivePriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass(frozen=True)
class RegisteredEvidence:
    evidence_id: str
    source_engine: str
    label: str
    detail: str
    confidence: float
    severity: str
    related_people: tuple[str, ...] = field(default_factory=tuple)
    related_skills: tuple[str, ...] = field(default_factory=tuple)
    related_departments: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id is required.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Evidence confidence must be between 0 and 1.")


@dataclass(frozen=True)
class DecisionTraceStep:
    order: int
    source_engine: str
    contribution: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    included: bool = True


@dataclass(frozen=True)
class ExecutiveAnswer:
    summary: str
    priority: ExecutivePriority
    confidence: float
    evidence: tuple[RegisteredEvidence, ...]
    recommendations: tuple[str, ...]
    actions: tuple[str, ...]
    risks: tuple[str, ...]
    sources: tuple[str, ...]
    missing_data: tuple[str, ...]
    assumptions: tuple[str, ...]
    decision_trace: tuple[DecisionTraceStep, ...]
    engine_coverage: float
    evidence_quality: str
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Answer confidence must be between 0 and 1.")
        if not 0.0 <= self.engine_coverage <= 1.0:
            raise ValueError("Engine coverage must be between 0 and 1.")

    @property
    def confidence_percent(self) -> int:
        return round(self.confidence * 100)

    @property
    def coverage_percent(self) -> int:
        return round(self.engine_coverage * 100)
