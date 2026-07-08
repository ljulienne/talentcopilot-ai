from dataclasses import dataclass
from talentcopilot.career_intelligence.models import CareerIntelligenceReport
from talentcopilot.semantic_intelligence.models import SemanticSkillReport


@dataclass
class HybridMatchingInput:
    candidate_name: str
    role_title: str
    candidate_skills: list[str]
    required_skills: list[str]
    years_experience: int = 0
    titles: list[str] | None = None
    achievements: list[str] | None = None
    responsibilities: list[str] | None = None


@dataclass
class HybridMatchingReport:
    candidate_name: str
    role_title: str
    semantic_skill_report: SemanticSkillReport
    career_report: CareerIntelligenceReport | None = None
    explanation_report: object | None = None
    recruiter_report: object | None = None

    @property
    def semantic_score(self) -> int:
        return self.semantic_skill_report.average_score

    @property
    def career_score(self) -> int:
        return self.career_report.career_score if self.career_report else 0

    @property
    def hybrid_score(self) -> int:
        if self.explanation_report:
            return self.explanation_report.breakdown.final_score
        if self.career_report:
            return int(self.semantic_score * 0.7 + self.career_score * 0.3)
        return self.semantic_score

    @property
    def summary(self) -> str:
        if self.recruiter_report and self.recruiter_report.executive_summary:
            return self.recruiter_report.executive_summary
        if self.explanation_report and self.explanation_report.recruiter_summary:
            return self.explanation_report.recruiter_summary
        base = (
            f"{self.candidate_name} covers "
            f"{self.semantic_skill_report.covered_skills}/{len(self.semantic_skill_report.required_skills)} "
            f"required skills semantically."
        )
        if self.career_report:
            base += f" Career level: {self.career_report.seniority_level}."
        return base
