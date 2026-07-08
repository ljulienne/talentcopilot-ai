from talentcopilot.document_intelligence.candidate_extractor import CandidateDocumentExtractor
from talentcopilot.document_intelligence.models import DocumentAnalysis, DocumentSection
from talentcopilot.document_intelligence.section_segmenter import CVSectionSegmenter


def test_section_segmenter_detects_sections():
    sections = CVSectionSegmenter().segment(
        "Alice Martin\nExperience\nLed HRIS projects\nSkills\nHRIS Leadership"
    )

    titles = [section.title for section in sections]
    assert "experience" in titles
    assert "skills" in titles


def test_candidate_extractor_returns_profile():
    analysis = DocumentAnalysis(
        filename="cv.txt",
        language="en",
        cleaned_text="Alice Martin has HRIS Leadership and Project Management experience.",
        sections=[
            DocumentSection("profile", "Alice Martin has HRIS Leadership and Project Management experience.")
        ],
    )

    candidate = CandidateDocumentExtractor().extract(analysis)

    assert candidate.candidate_name
    assert candidate.extraction_status == "Valid"
    assert isinstance(candidate.skills, list)


def test_document_intelligence_ui_imports():
    module = __import__("talentcopilot.ui.document_intelligence", fromlist=["render_document_intelligence"])
    assert hasattr(module, "render_document_intelligence")
