from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DecisionRankingAssessment:
    """Evidence-grounded interview-priority score, separate from Mission Fit."""

    score: float
    base_score: float
    alignment_adjustment: float
    components: Dict[str, float] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)
    rationale: str = ""
    version: str = "decision-ranking-policy-v1.1"

    def to_dict(self) -> dict:
        return asdict(self)
