from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.ai_core.structured_outputs import StructuredOutputValidator
from talentcopilot.document_intelligence.models import DocumentAnalysis, ExtractedCandidateProfile


class CandidateDocumentExtractor:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()
        self.validator = StructuredOutputValidator()

    def extract(self, analysis: DocumentAnalysis) -> ExtractedCandidateProfile:
        extraction_text = self._best_text(analysis)
        response = self.router.run(
            AIRequest(
                task="candidate_document_extraction",
                prompt_id="candidate.extract.v1",
                input_text=extraction_text,
            )
        )
        data = response.structured_data
        envelope = self.validator.validate_required_fields(
            "CandidateProfile",
            data,
            ["candidate_name"],
        )

        return ExtractedCandidateProfile(
            candidate_name=data.get("candidate_name") or "Unknown Candidate",
            skills=list(dict.fromkeys(data.get("skills", []) or [])),
            raw_excerpt=data.get("raw_excerpt", extraction_text[:500]),
            language=analysis.language,
            extraction_status=envelope.validation_status,
        )

    def _best_text(self, analysis: DocumentAnalysis) -> str:
        if not analysis.sections:
            return analysis.cleaned_text
        priority = ["profile", "experience", "skills", "education"]
        selected = []
        for title in priority:
            selected.extend(section.content for section in analysis.sections if section.title == title)
        return "\n\n".join(selected)[:4000] if selected else analysis.cleaned_text[:4000]
