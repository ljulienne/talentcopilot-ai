from dataclasses import dataclass, field
from typing import List


@dataclass
class UncertaintyItem:
    competency: str
    uncertainty_score: float
    reason: str
    missing_information: List[str] = field(default_factory=list)
    recommendation: str = ""

    @property
    def uncertainty_level(self) -> str:
        if self.uncertainty_score >= 70:
            return "High"
        if self.uncertainty_score >= 40:
            return "Medium"
        return "Low"


@dataclass
class CandidateUncertaintySummary:
    overall_uncertainty: float
    uncertainties: List[UncertaintyItem] = field(default_factory=list)
    explanation: str = ""

    @property
    def uncertainty_level(self) -> str:
        if self.overall_uncertainty >= 70:
            return "High"
        if self.overall_uncertainty >= 40:
            return "Medium"
        return "Low"
