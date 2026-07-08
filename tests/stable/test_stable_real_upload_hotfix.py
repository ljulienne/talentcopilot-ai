from talentcopilot.services.upload_text_reader_service import UploadedTextDocument, UploadTextReaderService


def test_uploaded_text_document_status_model():
    doc = UploadedTextDocument("cv.pdf", "pdf", "", "Missing dependency: pypdf")
    assert doc.status.startswith("Missing dependency")


def test_upload_text_reader_direct_still_works():
    doc = UploadTextReaderService().read_text_direct("cv.txt", "Alice HRIS")
    assert doc.filename == "cv.txt"
    assert doc.file_type == "txt"
    assert doc.text == "Alice HRIS"
    assert doc.status == "OK"
