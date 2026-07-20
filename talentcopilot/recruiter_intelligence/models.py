from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class EvidenceClaim:
    key: str
    label: str
    score: float
    evidence: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateDNA:
    archetypes: Dict[str, float] = field(default_factory=dict)
    primary_archetype: str = "Generalist"
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RecruiterIntelligenceAssessment:
    candidate_name: str
    strategic_fit_score: float
    confidence_score: int
    job_persona: List[str] = field(default_factory=list)
    candidate_dna: CandidateDNA = field(default_factory=CandidateDNA)
    dimensions: List[EvidenceClaim] = field(default_factory=list)
    decisive_strengths: List[str] = field(default_factory=list)
    material_gaps: List[str] = field(default_factory=list)
    recruiter_summary: str = ""
    interview_focus: List[str] = field(default_factory=list)
    engine_version: str = "recruiter-intelligence-v1.0"

    def to_dict(self) -> dict:
        return {
            "candidate_name": self.candidate_name,
            "strategic_fit_score": round(self.strategic_fit_score, 2),
            "confidence_score": self.confidence_score,
            "job_persona": list(self.job_persona),
            "candidate_dna": self.candidate_dna.to_dict(),
            "dimensions": [item.to_dict() for item in self.dimensions],
            "decisive_strengths": list(self.decisive_strengths),
            "material_gaps": list(self.material_gaps),
            "recruiter_summary": self.recruiter_summary,
            "interview_focus": list(self.interview_focus),
            "engine_version": self.engine_version,
        }
