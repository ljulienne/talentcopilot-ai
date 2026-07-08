from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.ai_core.structured_outputs import StructuredOutputValidator
from talentcopilot.document_intelligence.models import DocumentAnalysis, ExtractedCandidateProfile
from talentcopilot.extraction.skills_ontology import SkillsOntology
from talentcopilot.extraction.text_signals import TextSignalExtractor


class CandidateDocumentExtractor:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()
        self.validator = StructuredOutputValidator()
        self.ontology = SkillsOntology()
        self.signals = TextSignalExtractor()

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

        ontology_skills = self.ontology.extract_skills(analysis.cleaned_text)
        llm_skills = data.get("skills", []) or []
        skills = list(dict.fromkeys([*ontology_skills, *llm_skills]))

        candidate_name = self._infer_candidate_name(analysis.cleaned_text, data.get("candidate_name"))

        envelope = self.validator.validate_required_fields(
            "CandidateProfile",
            {"candidate_name": candidate_name},
            ["candidate_name"],
        )

        return ExtractedCandidateProfile(
            candidate_name=candidate_name,
            skills=skills,
            raw_excerpt=analysis.cleaned_text[:2000],
            language=analysis.language,
            extraction_status=envelope.validation_status,
        )

    def to_candidate_dict(self, candidate: ExtractedCandidateProfile) -> dict:
        text = candidate.raw_excerpt or ""
        return {
            "name": candidate.candidate_name,
            "skills": candidate.skills,
            "years_experience": self.signals.extract_years_experience(text),
            "achievements": self.signals.extract_achievements(text),
            "languages": self.signals.extract_languages(text),
            "certifications": self.signals.extract_certifications(text),
            "responsibilities": self.signals.extract_responsibilities(text),
        }

    def _best_text(self, analysis: DocumentAnalysis) -> str:
        if not analysis.sections:
            return analysis.cleaned_text[:6000]
        priority = ["profile", "experience", "skills", "certifications", "languages", "education"]
        selected = []
        for title in priority:
            selected.extend(section.content for section in analysis.sections if section.title == title)
        return "\n\n".join(selected)[:6000] if selected else analysis.cleaned_text[:6000]

    def _infer_candidate_name(self, text: str, fallback: str | None = None) -> str:
        if fallback and fallback != "Unknown Candidate":
            return fallback
        for line in (text or "").splitlines():
            clean = line.strip()
            if 3 <= len(clean) <= 60 and not any(marker in clean.lower() for marker in ["experience", "skills", "compétences", "formation", "education"]):
                parts = clean.split()
                if 1 <= len(parts) <= 5:
                    return clean
        return fallback or "Unknown Candidate"
