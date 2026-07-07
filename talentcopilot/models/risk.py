from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskItem:
    competency: str
    risk_level: str
    reason: str
    mitigation: str = ""


@dataclass
class CandidateRiskSummary:
    overall_risk_level: str
    risks: List[RiskItem] = field(default_factory=list)
    explanation: str = ""

    @property
    def risk_count(self) -> int:
        return len(self.risks)
