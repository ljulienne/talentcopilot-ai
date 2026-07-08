from talentcopilot.document_intelligence.document_loader import DocumentLoader
from talentcopilot.document_intelligence.language_detector import LanguageDetector
from talentcopilot.document_intelligence.text_cleaner import TextCleaner
from talentcopilot.job_intelligence.job_section_segmenter import JobSectionSegmenter
from talentcopilot.job_intelligence.models import JobAnalysis
from talentcopilot.job_intelligence.role_extractor import RoleProfileExtractor


class JobIntelligencePipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = TextCleaner()
        self.language_detector = LanguageDetector()
        self.segmenter = JobSectionSegmenter()
        self.extractor = RoleProfileExtractor()

    def analyze_text(self, filename: str, text: str) -> JobAnalysis:
        loaded = self.loader.load_text(filename, text)
        cleaned = self.cleaner.clean(loaded.text)
        language = self.language_detector.detect(cleaned)
        sections = self.segmenter.segment(cleaned)
        analysis = JobAnalysis(
            filename=loaded.filename,
            language=language,
            cleaned_text=cleaned,
            sections=sections,
        )
        analysis.role_profile = self.extractor.extract(analysis)
        return analysis

    def analyze_path(self, path: str) -> JobAnalysis:
        loaded = self.loader.load_path(path)
        return self.analyze_text(loaded.filename, loaded.text)
