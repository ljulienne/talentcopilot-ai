from dataclasses import dataclass, field
from typing import List

from talentcopilot.real_matching.models import RealMatchingOutput


@dataclass
class CandidateTextInput:
    filename: str
    text: str
    expected_salary: float | None = None


@dataclass
class RealRankingInput:
    job_filename: str
    job_text: str
    candidates: List[CandidateTextInput] = field(default_factory=list)


@dataclass
class RankedCandidate:
    rank: int
    candidate_name: str
    recommendation: str
    fit_score: int
    confidence_score: int
    risk_level: str
    ranking_score: int
    rationale: str
    matching_output: RealMatchingOutput


@dataclass
class RealRankingOutput:
    role_title: str
    total_candidates: int
    ranked_candidates: List[RankedCandidate] = field(default_factory=list)
