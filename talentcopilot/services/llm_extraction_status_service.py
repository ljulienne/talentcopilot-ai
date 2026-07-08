import os
from dataclasses import dataclass

from talentcopilot.llm_extraction.engine import LLMExtractionEngine


@dataclass
class LLMExtractionStatus:
    openai_key_configured: bool
    mode: str
    sample_candidate_name: str
    sample_confidence: float
    sample_status: str


class LLMExtractionStatusService:
    def build(self) -> LLMExtractionStatus:
        text = "LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director\nHRIS, Change Management, Talent Acquisition"
        result = LLMExtractionEngine().extract_candidate(text)
        return LLMExtractionStatus(
            openai_key_configured=bool(os.environ.get("OPENAI_API_KEY")),
            mode=os.environ.get("TALENTCOPILOT_USE_LLM_EXTRACTION", "auto"),
            sample_candidate_name=result.facts.candidate_name,
            sample_confidence=result.extraction_confidence,
            sample_status=result.extraction_status,
        )
