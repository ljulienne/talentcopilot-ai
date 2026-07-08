import os
from talentcopilot.llm_extraction.cache import LLMExtractionCache
from talentcopilot.llm_extraction.engine import LLMExtractionEngine
from talentcopilot.llm_extraction.models import CandidateExtractionResult, RoleExtractionResult
from talentcopilot.llm_extraction.performance import LLMExtractionMetric, LLMPerformanceReport, Timer

class CachedLLMExtractionEngine:
    def __init__(self, engine: LLMExtractionEngine | None = None, cache: LLMExtractionCache | None = None):
        self.engine = engine or LLMExtractionEngine()
        self.cache = cache or LLMExtractionCache()
        self.report = LLMPerformanceReport()
        self.model = os.environ.get("TALENTCOPILOT_LLM_MODEL", "default")

    def extract_candidate(self, text: str) -> CandidateExtractionResult:
        return self._extract("candidate", text, CandidateExtractionResult, self.engine.extract_candidate)

    def extract_role(self, text: str) -> RoleExtractionResult:
        return self._extract("role", text, RoleExtractionResult, self.engine.extract_role)

    def _extract(self, extraction_type: str, text: str, schema, extractor):
        cached = self.cache.get(extraction_type, text, schema, self.model)
        if cached is not None:
            self.report.metrics.append(LLMExtractionMetric(extraction_type, True, 0, "CACHE_HIT"))
            return cached
        with Timer() as timer:
            result = extractor(text)
        self.cache.set(extraction_type, text, result, self.model)
        self.report.metrics.append(LLMExtractionMetric(extraction_type, False, timer.duration_ms, getattr(result, "extraction_status", "OK")))
        return result
