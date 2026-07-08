from dataclasses import dataclass

from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.document_intelligence.document_loader import DocumentLoader
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
from talentcopilot.llm_extraction.adapters import CandidateExtractionAdapter, RoleExtractionAdapter
from talentcopilot.llm_extraction.engine import LLMExtractionEngine
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


class LLMRealMatchingPipeline:
    def run(self, data: LLMRealMatchingInput) -> LLMRealMatchingOutput:
        cleaner = TextCleaner()
        language_detector = LanguageDetector()

        candidate_text = cleaner.clean(data.candidate_text)
        job_text = cleaner.clean(data.job_text)

        candidate_language = language_detector.detect(candidate_text)
        role_language = language_detector.detect(job_text)

        engine = LLMExtractionEngine()
        candidate_result = engine.extract_candidate(candidate_text)
        role_result = engine.extract_role(job_text)

        candidate_dict = CandidateExtractionAdapter().to_candidate_dict(candidate_result)
        role_profile = RoleExtractionAdapter().to_role_profile(role_result, role_language)
        role = role_result.facts

        decision_input = DecisionCoreInput(
            candidate=candidate_dict,
            role_title=role.title,
            required_skills=role.required_skills,
            preferred_skills=role.preferred_skills,
            minimum_years_experience=role.minimum_experience,
            target_salary=role.salary_min,
            maximum_salary=role.salary_max,
            expected_salary=data.expected_salary if data.expected_salary is not None else role.salary_min,
        )

        decision_output = DecisionCoreOrchestrator().analyze_candidate(decision_input)

        return LLMRealMatchingOutput(
            candidate_extraction=candidate_result,
            role_extraction=role_result,
            decision_output=decision_output,
            candidate_language=candidate_language,
            role_language=role_language,
        )
