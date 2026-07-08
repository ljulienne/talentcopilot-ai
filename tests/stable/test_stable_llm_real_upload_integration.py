from talentcopilot.services.llm_real_upload_service import LLMRealUploadService
from talentcopilot.services.upload_text_reader_service import UploadedTextDocument
from talentcopilot.ui.enterprise_navigation import get_page_by_label

def test_llm_real_upload_service_demo(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")
    report = LLMRealUploadService().run_demo()
    assert report.status == "Ready"
    assert report.ranking_output is not None
    assert report.ranking_output.ranked_candidates
    assert report.ranking_output.performance_report.calls >= 1

def test_llm_real_upload_service_with_documents(monkeypatch):
    monkeypatch.setenv("TALENTCOPILOT_USE_LLM_EXTRACTION", "mock")
    report = LLMRealUploadService().run(
        UploadedTextDocument("job.txt", "txt", "HRIS Director. Required skills: HRIS."),
        [UploadedTextDocument("cv.txt", "txt", "LORETTA DANIELSON, MBA, SPHR")],
    )
    assert report.status == "Ready"
    assert report.ranking_output.ranked_candidates[0].candidate_name == "Loretta Danielson"

def test_llm_real_upload_ui_imports():
    module = __import__("talentcopilot.ui.llm_real_upload", fromlist=["render_llm_real_upload"])
    assert hasattr(module, "render_llm_real_upload")

def test_llm_real_upload_navigation():
    page = get_page_by_label("LLM Real Upload")
    assert page is not None
    assert page.module == "talentcopilot.ui.llm_real_upload"
