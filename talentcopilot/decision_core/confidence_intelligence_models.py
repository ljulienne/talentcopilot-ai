from dataclasses import dataclass, field
from typing import List


@dataclass
class ConfidenceDriver:
    area: str
    detail: str
    impact: int


@dataclass
class ConfidenceGap:
    area: str
    severity: str
    detail: str
    action: str


@dataclass
class ConfidenceIntelligenceReport:
    candidate_name: str
    confidence_score: int
    confidence_level: str
    decision_quality: str
    drivers: List[ConfidenceDriver] = field(default_factory=list)
    gaps: List[ConfidenceGap] = field(default_factory=list)
    summary: str = ""
