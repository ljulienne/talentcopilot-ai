from talentcopilot.llm_extraction.engine import LLMExtractionEngine
from talentcopilot.llm_extraction.provider import MockLLMProvider


def test_llm_extraction_engine_candidate_mock():
    engine = LLMExtractionEngine(provider=MockLLMProvider())
    result = engine.extract_candidate("LORETTA DANIELSON, MBA, SPHR, SHRM-SCP")

    assert result.facts.candidate_name == "Loretta Danielson"
    assert result.extraction_status == "OK"


def test_llm_extraction_engine_role_mock():
    engine = LLMExtractionEngine(provider=MockLLMProvider())
    result = engine.extract_role("HRIS Director. Required skills: HRIS, Project Management.")

    assert result.facts.title
    assert "HRIS" in result.facts.required_skills


def test_llm_extraction_ui_imports():
    module = __import__("talentcopilot.ui.llm_extraction", fromlist=["render_llm_extraction"])
    assert hasattr(module, "render_llm_extraction")
