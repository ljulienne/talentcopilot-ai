from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ConfidenceFactor:
    name: str
    score: float
    explanation: str


@dataclass
class ConfidenceAssessment:
    competency: str
    confidence_score: float
    evidence_count: int = 0
    evidence_quality_score: float = 0.0
    factors: List[ConfidenceFactor] = field(default_factory=list)
    explanation: str = ""

    @property
    def confidence_level(self) -> str:
        if self.confidence_score >= 85:
            return "High"
        if self.confidence_score >= 60:
            return "Medium"
        return "Low"


@dataclass
class CandidateConfidenceSummary:
    overall_confidence: float
    assessments: List[ConfidenceAssessment] = field(default_factory=list)
    explanation: str = ""

    @property
    def confidence_level(self) -> str:
        if self.overall_confidence >= 85:
            return "High"
        if self.overall_confidence >= 60:
            return "Medium"
        return "Low"
