from dataclasses import dataclass
from talentcopilot.semantic_intelligence.models import SemanticSkillReport


@dataclass
class HybridMatchingInput:
    candidate_name: str
    role_title: str
    candidate_skills: list[str]
    required_skills: list[str]


@dataclass
class HybridMatchingReport:
    candidate_name: str
    role_title: str
    semantic_skill_report: SemanticSkillReport

    @property
    def semantic_score(self) -> int:
        return self.semantic_skill_report.average_score

    @property
    def summary(self) -> str:
        return (
            f"{self.candidate_name} covers "
            f"{self.semantic_skill_report.covered_skills}/{len(self.semantic_skill_report.required_skills)} "
            f"required skills semantically."
        )
