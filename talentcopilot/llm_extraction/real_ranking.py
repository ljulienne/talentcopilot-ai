from dataclasses import dataclass, field
from typing import List
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
from talentcopilot.llm_extraction.cached_engine import CachedLLMExtractionEngine
from talentcopilot.llm_extraction.performance import LLMPerformanceReport
from talentcopilot.llm_extraction.real_matching import LLMRealMatchingOutput, LLMRealMatchingPipeline

@dataclass
class LLMCandidateTextInput:
    filename: str
    text: str
    expected_salary: float | None = None

@dataclass
class LLMRealRankingInput:
    job_filename: str
    job_text: str
    candidates: List[LLMCandidateTextInput] = field(default_factory=list)

@dataclass
class LLMRankedCandidate:
    rank: int
    candidate_name: str
    recommendation: str
    fit_score: int
    confidence_score: int
    risk_level: str
    ranking_score: int
    matching_output: LLMRealMatchingOutput

@dataclass
class LLMRealRankingOutput:
    role_title: str
    total_candidates: int
    ranked_candidates: List[LLMRankedCandidate] = field(default_factory=list)
    performance_report: LLMPerformanceReport = field(default_factory=LLMPerformanceReport)

class LLMRealRankingPipeline:
    RECOMMENDATION_WEIGHT = {"Strong Hire": 100, "Hire": 90, "Interview": 72, "Review Compensation Feasibility": 68, "More Evidence Required": 55, "Review": 45, "Reject": 0}
    RISK_PENALTY = {"Low": 0, "Medium": 8, "High": 18, "Critical": 35}

    def __init__(self, engine: CachedLLMExtractionEngine | None = None):
        self.engine = engine or CachedLLMExtractionEngine()

    def run(self, data: LLMRealRankingInput) -> LLMRealRankingOutput:
        cleaner = TextCleaner()
        detector = LanguageDetector()
        job_text = cleaner.clean(data.job_text)
        role_language = detector.detect(job_text)
        role_result = self.engine.extract_role(job_text)
        matching_pipeline = LLMRealMatchingPipeline(engine=self.engine)
        matches = []
        for candidate in data.candidates:
            candidate_text = cleaner.clean(candidate.text)
            matches.append(matching_pipeline.build_decision_output(
                self.engine.extract_candidate(candidate_text),
                role_result,
                candidate.expected_salary,
                detector.detect(candidate_text),
                role_language,
            ))
        ranked = []
        for match in matches:
            profile = match.decision_output.profile
            ranked.append(LLMRankedCandidate(
                0, profile.candidate_name, profile.recommendation or "No recommendation",
                int(profile.fit_score or 0), int(profile.confidence_score or 0),
                profile.risk_level or "Unknown", self._ranking_score(profile), match
            ))
        ranked.sort(key=lambda item: item.ranking_score, reverse=True)
        for i, item in enumerate(ranked, 1):
            item.rank = i
        return LLMRealRankingOutput(role_result.facts.title, len(data.candidates), ranked, self.engine.report)

    def _ranking_score(self, profile) -> int:
        rec = self.RECOMMENDATION_WEIGHT.get(profile.recommendation or "Review", 40)
        risk = self.RISK_PENALTY.get(profile.risk_level or "Medium", 10)
        return max(0, min(100, int(rec * 0.4 + int(profile.fit_score or 0) * 0.4 + int(profile.confidence_score or 0) * 0.2 - risk)))
