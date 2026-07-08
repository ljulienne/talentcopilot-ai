import os

from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_document_pipeline_with_llm_mock_mode(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")
    analysis, candidate = DocumentIntelligencePipeline().analyze_text(
        "cv.txt",
        "LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director",
    )

    assert candidate.candidate_name == "Loretta Danielson"


def test_job_pipeline_still_extracts_role():
    analysis = JobIntelligencePipeline().analyze_text(
        "job.txt",
        "HRIS Director\nRequirements\nMinimum 8 years experience. HRIS Project Management",
    )

    assert analysis.role_profile.role_title
    assert analysis.role_profile.required_skills


def test_llm_extraction_navigation():
    page = get_page_by_label("LLM Extraction")
    assert page is not None
    assert page.module == "talentcopilot.ui.llm_extraction"
