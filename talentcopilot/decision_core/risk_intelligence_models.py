from dataclasses import dataclass, field
from typing import List


@dataclass
class RiskFactor:
    area: str
    severity: str
    detail: str
    mitigation: str
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class RiskIntelligenceReport:
    candidate_name: str
    role_title: str
    risk_score: int
    risk_level: str
    risk_factors: List[RiskFactor] = field(default_factory=list)
    mitigation_actions: List[str] = field(default_factory=list)
    summary: str = ""
