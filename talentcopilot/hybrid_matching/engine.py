from talentcopilot.career_intelligence.career_engine import CareerIntelligenceEngine
from talentcopilot.hybrid_matching.explainability_engine import HybridExplainabilityEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput, HybridMatchingReport
from talentcopilot.hybrid_matching.report_engine import HybridRecruiterReportEngine
from talentcopilot.semantic_intelligence.skill_matcher import SemanticSkillMatcher


class HybridMatchingEngine:
    def __init__(
        self,
        skill_matcher: SemanticSkillMatcher | None = None,
        career_engine: CareerIntelligenceEngine | None = None,
        explainability_engine: HybridExplainabilityEngine | None = None,
        report_engine: HybridRecruiterReportEngine | None = None,
    ):
        self.skill_matcher = skill_matcher or SemanticSkillMatcher()
        self.career_engine = career_engine or CareerIntelligenceEngine()
        self.explainability_engine = explainability_engine or HybridExplainabilityEngine()
        self.report_engine = report_engine or HybridRecruiterReportEngine()

    def analyze(self, data: HybridMatchingInput) -> HybridMatchingReport:
        semantic_report = self.skill_matcher.compare(data.required_skills, data.candidate_skills)
        career_report = self.career_engine.analyze(
            candidate_name=data.candidate_name,
            years_experience=data.years_experience,
            titles=data.titles or [],
            achievements=data.achievements or [],
            responsibilities=data.responsibilities or [],
        )
        report = HybridMatchingReport(
            candidate_name=data.candidate_name,
            role_title=data.role_title,
            semantic_skill_report=semantic_report,
            career_report=career_report,
        )
        report.explanation_report = self.explainability_engine.explain(report)
        report.recruiter_report = self.report_engine.build(report)
        return report
