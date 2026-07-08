from dataclasses import dataclass, field
from typing import List


@dataclass
class CandidateSkill:
    name: str
    level: int
    evidence: str = ""


@dataclass
class CandidateEvidence:
    title: str
    detail: str
    strength: str = "Medium"


@dataclass
class CandidateRisk:
    title: str
    detail: str
    severity: str = "Medium"


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
