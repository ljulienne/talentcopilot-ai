from dataclasses import dataclass, field
from typing import List


@dataclass
class CareerSignal:
    category: str
    label: str
    score: int
    evidence: List[str] = field(default_factory=list)


@dataclass
class CareerIntelligenceReport:
    candidate_name: str
    years_experience: int
    seniority_level: str
    career_score: int
    signals: List[CareerSignal] = field(default_factory=list)

    @property
    def leadership_score(self) -> int:
        values = [s.score for s in self.signals if s.category == "Leadership"]
        return max(values) if values else 0

    @property
    def transformation_score(self) -> int:
        values = [s.score for s in self.signals if s.category == "Transformation"]
        return max(values) if values else 0

    @property
    def impact_score(self) -> int:
        values = [s.score for s in self.signals if s.category == "Impact"]
        return max(values) if values else 0
