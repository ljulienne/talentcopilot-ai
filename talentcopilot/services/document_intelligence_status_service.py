from dataclasses import dataclass

from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline


@dataclass
class DocumentIntelligenceStatus:
    language: str
    section_count: int
    candidate_name: str
    skills_count: int
    extraction_status: str


class DocumentIntelligenceStatusService:
    def build_sample(self) -> DocumentIntelligenceStatus:
        sample = '''
Alice Martin
Experience
Led HRIS transformation and Project Management initiatives.
Skills
HRIS, Leadership, Project Management, Workday
Education
Master Human Resources
'''
        analysis, candidate = DocumentIntelligencePipeline().analyze_text("sample_cv.txt", sample)
        return DocumentIntelligenceStatus(
            language=analysis.language,
            section_count=len(analysis.sections),
            candidate_name=candidate.candidate_name,
            skills_count=len(candidate.skills),
            extraction_status=candidate.extraction_status,
        )
