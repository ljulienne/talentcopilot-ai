from dataclasses import dataclass

from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
from talentcopilot.hybrid_matching.llm_adapter import LLMHybridMatchingAdapter
from talentcopilot.llm_extraction.adapters import CandidateExtractionAdapter
from talentcopilot.llm_extraction.cached_engine import CachedLLMExtractionEngine
from talentcopilot.llm_extraction.models import CandidateExtractionResult, RoleExtractionResult


@dataclass
class LLMRealMatchingInput:
    candidate_filename: str
    candidate_text: str
    job_filename: str
    job_text: str
    expected_salary: float | None = None


@dataclass
class LLMRealMatchingOutput:
    candidate_extraction: CandidateExtractionResult
    role_extraction: RoleExtractionResult
    decision_output: object
    candidate_language: str = "unknown"
    role_language: str = "unknown"
    hybrid_report: object | None = None


class LLMRealMatchingPipeline:
    def __init__(self, engine: CachedLLMExtractionEngine | None = None):
        self.engine = engine or CachedLLMExtractionEngine()

    def run(self, data: LLMRealMatchingInput) -> LLMRealMatchingOutput:
        cleaner = TextCleaner()
        detector = LanguageDetector()

        candidate_text = cleaner.clean(data.candidate_text)
        job_text = cleaner.clean(data.job_text)

        candidate_result = self.engine.extract_candidate(candidate_text)
        role_result = self.engine.extract_role(job_text)

        return self.build_decision_output(
            candidate_result=candidate_result,
            role_result=role_result,
            expected_salary=data.expected_salary,
            candidate_language=detector.detect(candidate_text),
            role_language=detector.detect(job_text),
        )

    def build_decision_output(
        self,
        candidate_result: CandidateExtractionResult,
        role_result: RoleExtractionResult,
        expected_salary: float | None = None,
        candidate_language: str = "unknown",
        role_language: str = "unknown",
    ) -> LLMRealMatchingOutput:
        candidate_dict = CandidateExtractionAdapter().to_candidate_dict(candidate_result)
        role = role_result.facts

        decision_input = DecisionCoreInput(
            candidate=candidate_dict,
            role_title=role.title,
            required_skills=role.required_skills,
            preferred_skills=role.preferred_skills,
            minimum_years_experience=role.minimum_experience,
            target_salary=role.salary_min,
            maximum_salary=role.salary_max,
            expected_salary=expected_salary if expected_salary is not None else role.salary_min,
        )

        decision_output = DecisionCoreOrchestrator().analyze_candidate(decision_input)
        hybrid_report = LLMHybridMatchingAdapter().build_report(candidate_result, role_result)

        return LLMRealMatchingOutput(
            candidate_extraction=candidate_result,
            role_extraction=role_result,
            decision_output=decision_output,
            candidate_language=candidate_language,
            role_language=role_language,
            hybrid_report=hybrid_report,
        )
