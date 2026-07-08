from dataclasses import dataclass, field
from typing import List


@dataclass
class FitDriver:
    area: str
    detail: str
    impact: int
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class FitGap:
    area: str
    severity: str
    detail: str


@dataclass
class RoleRequirements:
    role_title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    minimum_years_experience: int = 0


@dataclass
class FitIntelligenceReport:
    candidate_name: str
    role_title: str
    fit_score: int
    skill_match_score: int
    experience_match_score: int
    achievement_signal_score: int
    status: str
    drivers: List[FitDriver] = field(default_factory=list)
    gaps: List[FitGap] = field(default_factory=list)
    summary: str = ""
