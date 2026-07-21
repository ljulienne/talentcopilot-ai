from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CandidateSkill:
    name: str
    level: int
    evidence: str = ""
    status: str = "Moderate evidence"
    confidence: str = "Moderate"
    requirement_type: str = "Candidate capability"


@dataclass
class CandidateEvidence:
    title: str
    detail: str
    strength: str = "Medium"
    requirement: str = ""
    source: str = "Candidate CV"
    ownership: str = "Not established"
    outcome: str = "Not quantified"
    confidence: str = "Moderate"
    evidence_type: str = "Indirect evidence"


@dataclass
class CandidateRisk:
    title: str
    detail: str
    severity: str = "Medium"
    classification: str = "Validation point"
    related_requirement: str = ""
    interview_question: str = ""
    evidence_basis: str = ""


@dataclass
class CandidateWorkspaceReport:
    candidate_name: str
    rank: int
    match_score: float
    recommendation: str
    executive_summary: str
    skills: List[CandidateSkill] = field(default_factory=list)
    evidence: List[CandidateEvidence] = field(default_factory=list)
    risks: List[CandidateRisk] = field(default_factory=list)
    interview_focus: List[str] = field(default_factory=list)
    candidate_id: str = ""
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    recommendation_label: str = ""
    recommendation_rationale: str = ""
    next_action: str = ""

    @property
    def official_match_score(self) -> float:
        return self.match_score

    @property
    def official_rank(self) -> int:
        return self.rank
