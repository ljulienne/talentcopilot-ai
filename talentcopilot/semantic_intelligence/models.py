from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class SkillConcept:
    canonical: str
    aliases: List[str]
    family: str
    parent: str | None = None
    related: List[str] = field(default_factory=list)


@dataclass
class SkillMatch:
    required_skill: str
    candidate_skill: str | None
    score: int
    match_type: str
    explanation: str


@dataclass
class SemanticSkillReport:
    required_skills: List[str]
    candidate_skills: List[str]
    matches: List[SkillMatch] = field(default_factory=list)

    @property
    def average_score(self) -> int:
        if not self.matches:
            return 0
        return int(sum(match.score for match in self.matches) / len(self.matches))

    @property
    def covered_skills(self) -> int:
        return sum(1 for match in self.matches if match.score >= 70)

    @property
    def missing_skills(self) -> List[str]:
        return [match.required_skill for match in self.matches if match.score < 50]
