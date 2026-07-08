from talentcopilot.services.real_upload_ranking_service import RealUploadRankingService
from talentcopilot.services.upload_text_reader_service import UploadTextReaderService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_upload_text_reader_direct():
    doc = UploadTextReaderService().read_text_direct("cv.txt", "Alice HRIS")

    assert doc.filename == "cv.txt"
    assert doc.file_type == "txt"
    assert doc.text == "Alice HRIS"


def test_real_upload_ranking_demo():
    report = RealUploadRankingService().run_demo()

    assert report.status == "Ready"
    assert report.ranking_output is not None
    assert report.ranking_output.ranked_candidates


def test_real_upload_ui_imports():
    module = __import__("talentcopilot.ui.real_upload_workspace", fromlist=["render_real_upload_workspace"])
    assert hasattr(module, "render_real_upload_workspace")


def test_real_upload_navigation():
    page = get_page_by_label("Real Upload")
    assert page is not None
    assert page.module == "talentcopilot.ui.real_upload_workspace"
