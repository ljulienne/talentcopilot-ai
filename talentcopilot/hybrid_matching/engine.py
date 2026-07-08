from talentcopilot.hybrid_matching.models import HybridMatchingInput, HybridMatchingReport
from talentcopilot.semantic_intelligence.skill_matcher import SemanticSkillMatcher


class HybridMatchingEngine:
    def __init__(self, skill_matcher: SemanticSkillMatcher | None = None):
        self.skill_matcher = skill_matcher or SemanticSkillMatcher()

    def analyze(self, data: HybridMatchingInput) -> HybridMatchingReport:
        semantic_report = self.skill_matcher.compare(data.required_skills, data.candidate_skills)
        return HybridMatchingReport(
            candidate_name=data.candidate_name,
            role_title=data.role_title,
            semantic_skill_report=semantic_report,
        )
