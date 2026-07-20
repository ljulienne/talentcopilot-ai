from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ScoreEvidence:
    label: str
    detail: str
    impact: float = 0.0
    kind: str = "evidence"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreDimension:
    key: str
    label: str
    score: float
    weight: float
    contribution: float
    status: str
    evidence: List[ScoreEvidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        return payload


@dataclass(frozen=True)
class CandidateScoreBreakdown:
    candidate_id: str
    candidate_name: str
    mission_fit: float
    confidence: float
    dimensions: List[ScoreDimension] = field(default_factory=list)
    positive_contributions: List[ScoreEvidence] = field(default_factory=list)
    penalties: List[ScoreEvidence] = field(default_factory=list)
    rationale: str = ""
    engine_version: str = "explainable-scoring-v1.0"

    @property
    def reconstructed_score(self) -> float:
        return round(sum(item.contribution for item in self.dimensions), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "mission_fit": self.mission_fit,
            "confidence": self.confidence,
            "dimensions": [item.to_dict() for item in self.dimensions],
            "positive_contributions": [item.to_dict() for item in self.positive_contributions],
            "penalties": [item.to_dict() for item in self.penalties],
            "rationale": self.rationale,
            "engine_version": self.engine_version,
        }
