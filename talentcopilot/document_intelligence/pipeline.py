from talentcopilot.document_intelligence.candidate_extractor import CandidateDocumentExtractor
from talentcopilot.document_intelligence.document_loader import DocumentLoader
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.models import DocumentAnalysis, ExtractedCandidateProfile
from talentcopilot.document_intelligence.section_segmenter import CVSectionSegmenter
from talentcopilot.document_intelligence.text_cleaner import TextCleaner


class DocumentIntelligencePipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = TextCleaner()
        self.language_detector = LanguageDetector()
        self.segmenter = CVSectionSegmenter()
        self.extractor = CandidateDocumentExtractor()

    def analyze_text(self, filename: str, text: str) -> tuple[DocumentAnalysis, ExtractedCandidateProfile]:
        loaded = self.loader.load_text(filename, text)
        cleaned = self.cleaner.clean(loaded.text)
        language = self.language_detector.detect(cleaned)
        sections = self.segmenter.segment(cleaned)
        analysis = DocumentAnalysis(
            filename=loaded.filename,
            language=language,
            cleaned_text=cleaned,
            sections=sections,
        )
        candidate = self.extractor.extract(analysis)
        return analysis, candidate

    def analyze_path(self, path: str) -> tuple[DocumentAnalysis, ExtractedCandidateProfile]:
        loaded = self.loader.load_path(path)
        return self.analyze_text(loaded.filename, loaded.text)
