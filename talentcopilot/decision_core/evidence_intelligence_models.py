from dataclasses import dataclass, field
from typing import List


@dataclass
class EvidenceGap:
    area: str
    severity: str
    detail: str


@dataclass
class EvidenceStrength:
    area: str
    detail: str
    confidence: int


@dataclass
class EvidenceIntelligenceReport:
    candidate_name: str
    evidence_quality_score: int
    evidence_coverage_score: int
    evidence_reliability_score: int
    evidence_density_score: int
    evidence_readiness_score: int
    status: str
    strengths: List[EvidenceStrength] = field(default_factory=list)
    gaps: List[EvidenceGap] = field(default_factory=list)
    summary: str = ""
