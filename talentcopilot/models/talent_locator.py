from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TalentLocatorFit(str, Enum):
    EXCELLENT = "Excellent Fit"
    STRONG = "Strong Fit"
    MODERATE = "Moderate Fit"
    WEAK = "Weak Fit"


@dataclass
class TalentLocatorReason:
    title: str
    explanation: str
    weight: float = 1.0


@dataclass
class TalentLocatorCandidate:
    candidate_name: str
    role_title: str
    locator_score: float
    fit: TalentLocatorFit
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    reasons: List[TalentLocatorReason] = field(default_factory=list)
    evidence_hints: List[str] = field(default_factory=list)

    @property
    def is_recommended(self) -> bool:
        return self.fit in {TalentLocatorFit.EXCELLENT, TalentLocatorFit.STRONG}


@dataclass
class TalentLocatorReport:
    role_title: str
    total_candidates: int
    results: List[TalentLocatorCandidate] = field(default_factory=list)
    summary: str = ""

    @property
    def recommended_count(self) -> int:
        return len([candidate for candidate in self.results if candidate.is_recommended])
