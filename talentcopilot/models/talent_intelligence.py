from dataclasses import dataclass, field
from typing import List


@dataclass
class TalentSignal:
    name: str
    coverage: int
    evidence_count: int


@dataclass
class TalentShortlistLine:
    candidate_name: str
    rank: int
    match_score: float
    top_skills: List[str] = field(default_factory=list)
    sourcing_note: str = ""


@dataclass
class TalentRecommendation:
    title: str
    detail: str
    priority: str = "Medium"


@dataclass
class TalentIntelligenceReport:
    role_title: str
    session_id: str
    search_readiness: int
    shortlist: List[TalentShortlistLine] = field(default_factory=list)
    skill_signals: List[TalentSignal] = field(default_factory=list)
    recommendations: List[TalentRecommendation] = field(default_factory=list)
