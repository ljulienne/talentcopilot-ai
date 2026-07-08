from talentcopilot.llm_extraction.cache import LLMExtractionCache
from talentcopilot.llm_extraction.models import CandidateExtractionResult, CandidateFacts

def test_llm_extraction_cache_roundtrip(tmp_path):
    cache = LLMExtractionCache(tmp_path)
    result = CandidateExtractionResult(facts=CandidateFacts(candidate_name="Loretta Danielson"), extraction_confidence=0.9)
    cache.set("candidate", "sample text", result, "mock")
    loaded = cache.get("candidate", "sample text", CandidateExtractionResult, "mock")
    assert loaded is not None
    assert loaded.facts.candidate_name == "Loretta Danielson"

def test_llm_extraction_cache_stats_and_clear(tmp_path):
    cache = LLMExtractionCache(tmp_path)
    result = CandidateExtractionResult(facts=CandidateFacts(candidate_name="Vincent Blakoe"))
    cache.set("candidate", "vincent", result, "mock")
    assert cache.stats()["entries"] == 1
    assert cache.clear() == 1
    assert cache.stats()["entries"] == 0
