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


@dataclass(frozen=True)
class CareerDimension:
    key: str
    label: str
    score: float
    evidence_ids: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


@dataclass
class CareerFitReport:
    candidate_name: str
    score: float
    confidence: int
    functional_alignment: float
    recent_role_alignment: float
    domain_persistence: float
    career_drift: float
    seniority_alignment: float
    transferability: float
    dimensions: List[CareerDimension] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    summary: str = ""
    interview_focus: List[str] = field(default_factory=list)
    engine_version: str = "career-fit-intelligence-v1.0"

    def to_dict(self) -> dict:
        return {
            "candidate_name": self.candidate_name,
            "score": round(self.score, 2),
            "confidence": self.confidence,
            "functional_alignment": round(self.functional_alignment, 2),
            "recent_role_alignment": round(self.recent_role_alignment, 2),
            "domain_persistence": round(self.domain_persistence, 2),
            "career_drift": round(self.career_drift, 2),
            "seniority_alignment": round(self.seniority_alignment, 2),
            "transferability": round(self.transferability, 2),
            "dimensions": [item.to_dict() for item in self.dimensions],
            "strengths": list(self.strengths),
            "concerns": list(self.concerns),
            "summary": self.summary,
            "interview_focus": list(self.interview_focus),
            "engine_version": self.engine_version,
        }
