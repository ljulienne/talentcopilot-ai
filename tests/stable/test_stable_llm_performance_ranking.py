from talentcopilot.llm_extraction.cache import LLMExtractionCache
from talentcopilot.llm_extraction.cached_engine import CachedLLMExtractionEngine
from talentcopilot.llm_extraction.engine import LLMExtractionEngine
from talentcopilot.llm_extraction.provider import MockLLMProvider
from talentcopilot.llm_extraction.real_ranking import LLMCandidateTextInput, LLMRealRankingInput, LLMRealRankingPipeline
from talentcopilot.ui.enterprise_navigation import get_page_by_label

def test_llm_real_ranking_extracts_role_once_with_shared_engine(tmp_path, monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")
    engine = CachedLLMExtractionEngine(engine=LLMExtractionEngine(provider=MockLLMProvider()), cache=LLMExtractionCache(tmp_path))
    output = LLMRealRankingPipeline(engine=engine).run(
        LLMRealRankingInput(
            job_filename="job.txt",
            job_text="HRIS Director. Required skills: HRIS Project Management.",
            candidates=[
                LLMCandidateTextInput("loretta.txt", "LORETTA DANIELSON, MBA, SPHR"),
                LLMCandidateTextInput("vincent.txt", "Vincent BLAKOE 13 years experience HRIS"),
                LLMCandidateTextInput("loretta_copy.txt", "LORETTA DANIELSON, MBA, SPHR"),
            ],
        )
    )
    assert output.total_candidates == 3
    assert output.performance_report.calls == 4
    assert output.performance_report.cache_hits >= 1
    assert output.performance_report.cache_misses <= 3

def test_llm_monitor_navigation():
    page = get_page_by_label("LLM Monitor")
    assert page is not None
    assert page.module == "talentcopilot.ui.llm_monitor"

def test_llm_monitor_ui_imports():
    module = __import__("talentcopilot.ui.llm_monitor", fromlist=["render_llm_monitor"])
    assert hasattr(module, "render_llm_monitor")
