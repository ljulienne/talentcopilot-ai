from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class ComparativeProfile:
    candidate_name: str
    role_level: float
    geographic_scope: float
    leadership_scope: float
    commercial_scope: float
    industry_depth: float
    career_progression: float
    score: float
    differentiators: List[str] = field(default_factory=list)
    validation_points: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
