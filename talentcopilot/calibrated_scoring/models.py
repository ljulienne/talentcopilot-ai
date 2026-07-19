from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CalibratedScoreResult:
    score: float
    confidence: int
    band: str
    raw_mission_fit: float
    comparative_scope: float
    coverage_factor: float
    evidence_factor: float
    critical_cap: float
    limiting_factors: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "score": self.score,
            "confidence": self.confidence,
            "band": self.band,
            "raw_mission_fit": self.raw_mission_fit,
            "comparative_scope": self.comparative_scope,
            "coverage_factor": self.coverage_factor,
            "evidence_factor": self.evidence_factor,
            "critical_cap": self.critical_cap,
            "limiting_factors": list(self.limiting_factors),
            "strengths": list(self.strengths),
        }
