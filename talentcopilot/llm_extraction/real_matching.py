from dataclasses import dataclass
from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
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

class LLMRealMatchingPipeline:
    def __init__(self, engine: CachedLLMExtractionEngine | None = None):
        self.engine = engine or CachedLLMExtractionEngine()

    def run(self, data: LLMRealMatchingInput) -> LLMRealMatchingOutput:
        cleaner = TextCleaner()
        detector = LanguageDetector()
        candidate_text = cleaner.clean(data.candidate_text)
        job_text = cleaner.clean(data.job_text)
        return self.build_decision_output(
            self.engine.extract_candidate(candidate_text),
            self.engine.extract_role(job_text),
            data.expected_salary,
            detector.detect(candidate_text),
            detector.detect(job_text),
        )

    def build_decision_output(self, candidate_result, role_result, expected_salary=None, candidate_language="unknown", role_language="unknown"):
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
        return LLMRealMatchingOutput(candidate_result, role_result, DecisionCoreOrchestrator().analyze_candidate(decision_input), candidate_language, role_language)
