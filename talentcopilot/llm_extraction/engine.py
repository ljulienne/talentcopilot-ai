from talentcopilot.llm_extraction.models import CandidateExtractionResult, RoleExtractionResult
from talentcopilot.llm_extraction.prompts import CANDIDATE_EXTRACTION_PROMPT, ROLE_EXTRACTION_PROMPT
from talentcopilot.llm_extraction.provider import SafeExtractionProvider


class LLMExtractionEngine:
    def __init__(self, provider=None):
        self.provider = provider or SafeExtractionProvider()

    def extract_candidate(self, text: str) -> CandidateExtractionResult:
        prompt = CANDIDATE_EXTRACTION_PROMPT.format(text=(text or "")[:20000])
        return self.provider.extract(prompt, CandidateExtractionResult)

    def extract_role(self, text: str) -> RoleExtractionResult:
        prompt = ROLE_EXTRACTION_PROMPT.format(text=(text or "")[:20000])
        return self.provider.extract(prompt, RoleExtractionResult)
