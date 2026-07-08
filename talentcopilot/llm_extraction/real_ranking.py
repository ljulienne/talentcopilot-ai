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
    semantic_score: int = 0
    career_score: int = 0
    hybrid_score: int = 0


@dataclass
class LLMRealRankingOutput:
    role_title: str
    total_candidates: int
    ranked_candidates: List[LLMRankedCandidate] = field(default_factory=list)
    performance_report: LLMPerformanceReport = field(default_factory=LLMPerformanceReport)


class LLMRealRankingPipeline:
    RECOMMENDATION_WEIGHT = {
        "Strong Hire": 100,
        "Hire": 90,
        "Interview": 72,
        "Review Compensation Feasibility": 68,
        "More Evidence Required": 55,
        "Review": 45,
        "Reject": 0,
    }

    RISK_PENALTY = {
        "Low": 0,
        "Medium": 8,
        "High": 18,
        "Critical": 35,
    }

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
            candidate_result = self.engine.extract_candidate(candidate_text)

            matches.append(
                matching_pipeline.build_decision_output(
                    candidate_result=candidate_result,
                    role_result=role_result,
                    expected_salary=candidate.expected_salary,
                    candidate_language=detector.detect(candidate_text),
                    role_language=role_language,
                )
            )

        ranked = []
        for match in matches:
            profile = match.decision_output.profile
            hybrid = match.hybrid_report
            semantic_score = int(hybrid.semantic_score if hybrid else 0)
            career_score = int(hybrid.career_score if hybrid else 0)
            hybrid_score = int(hybrid.hybrid_score if hybrid else 0)

            ranked.append(
                LLMRankedCandidate(
                    rank=0,
                    candidate_name=profile.candidate_name,
                    recommendation=profile.recommendation or "No recommendation",
                    fit_score=int(profile.fit_score or 0),
                    confidence_score=int(profile.confidence_score or 0),
                    risk_level=profile.risk_level or "Unknown",
                    ranking_score=self._ranking_score(profile, hybrid_score),
                    matching_output=match,
                    semantic_score=semantic_score,
                    career_score=career_score,
                    hybrid_score=hybrid_score,
                )
            )

        ranked.sort(key=lambda item: item.ranking_score, reverse=True)
        for index, item in enumerate(ranked, start=1):
            item.rank = index

        return LLMRealRankingOutput(
            role_title=role_result.facts.title,
            total_candidates=len(data.candidates),
            ranked_candidates=ranked,
            performance_report=self.engine.report,
        )

    def _ranking_score(self, profile, hybrid_score: int = 0) -> int:
        rec_score = self.RECOMMENDATION_WEIGHT.get(profile.recommendation or "Review", 40)
        fit = int(profile.fit_score or 0)
        confidence = int(profile.confidence_score or 0)
        risk_penalty = self.RISK_PENALTY.get(profile.risk_level or "Medium", 10)

        decision_score = int(rec_score * 0.35 + fit * 0.35 + confidence * 0.15 - risk_penalty)
        if hybrid_score:
            score = int(decision_score * 0.65 + hybrid_score * 0.35)
        else:
            score = decision_score
        return max(0, min(100, score))
