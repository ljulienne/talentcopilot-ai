from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_text_cleaner():
    cleaned = TextCleaner().clean("Alice\r\n\n\n  HRIS   Manager")
    assert "\r" not in cleaned
    assert "  " not in cleaned


def test_language_detector():
    assert LanguageDetector().detect("Expérience Formation Compétences") == "fr"
    assert LanguageDetector().detect("Experience Education Skills") == "en"
    assert LanguageDetector().detect("你好 项目 管理") == "zh"


def test_document_pipeline_analyze_text():
    analysis, candidate = DocumentIntelligencePipeline().analyze_text(
        "cv.txt",
        "Alice Martin\nExperience\nLed HRIS and Project Management work.\nSkills\nHRIS Leadership",
    )

    assert analysis.cleaned_text
    assert analysis.sections
    assert candidate.candidate_name
    assert candidate.extraction_status == "Valid"


def test_document_intelligence_navigation():
    page = get_page_by_label("Document Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.document_intelligence"
