from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass
class FitDimension:
    key: str
    label: str
    score: float
    weight: float
    matched: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MissionFitResult:
    overall_score: float
    confidence_score: int
    recommendation: str
    risk_level: str
    dimensions: List[FitDimension] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    rationale: str = ""
    engine_version: str = "mission-fit-v2.0"

    @property
    def breakdown(self) -> Dict[str, float]:
        return {dimension.key: round(dimension.score, 2) for dimension in self.dimensions}

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score, 2),
            "confidence_score": self.confidence_score,
            "recommendation": self.recommendation,
            "risk_level": self.risk_level,
            "dimensions": [dimension.to_dict() for dimension in self.dimensions],
            "strengths": list(self.strengths),
            "gaps": list(self.gaps),
            "evidence": list(self.evidence),
            "rationale": self.rationale,
            "engine_version": self.engine_version,
        }
