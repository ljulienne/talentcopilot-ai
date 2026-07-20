from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class MissionCriterion:
    key: str
    label: str
    category: str
    weight: float
    mandatory: bool = False
    aliases: List[str] = field(default_factory=list)
    transferable_aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class CriterionAssessment:
    criterion: MissionCriterion
    evidence_level: str
    evidence_score: float
    contribution: float
    evidence: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "criterion": self.criterion.to_dict(),
            "evidence_level": self.evidence_level,
            "evidence_score": self.evidence_score,
            "contribution": self.contribution,
            "evidence": list(self.evidence),
            "gaps": list(self.gaps),
        }


@dataclass
class RecruitmentReasoningResult:
    score: float
    confidence: int
    recommendation: str
    risk_level: str
    criteria: List[MissionCriterion] = field(default_factory=list)
    assessments: List[CriterionAssessment] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    rationale: str = ""
    version: str = "recruitment-reasoning-v1.1.0-consultant-grade"

    def to_dict(self) -> Dict[str, object]:
        return {
            "score": self.score,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "risk_level": self.risk_level,
            "criteria": [item.to_dict() for item in self.criteria],
            "assessments": [item.to_dict() for item in self.assessments],
            "strengths": list(self.strengths),
            "gaps": list(self.gaps),
            "rationale": self.rationale,
            "version": self.version,
        }
