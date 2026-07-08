import os
import re

from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.ai_core.structured_outputs import StructuredOutputValidator
from talentcopilot.extraction.skills_ontology import SkillsOntology
from talentcopilot.extraction.text_signals import TextSignalExtractor
from talentcopilot.job_intelligence.models import JobAnalysis, RoleProfile
from talentcopilot.llm_extraction.adapters import RoleExtractionAdapter
from talentcopilot.llm_extraction.engine import LLMExtractionEngine


class RoleProfileExtractor:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()
        self.validator = StructuredOutputValidator()
        self.ontology = SkillsOntology()
        self.signals = TextSignalExtractor()

    def extract(self, analysis: JobAnalysis) -> RoleProfile:
        if self._should_use_llm():
            try:
                result = LLMExtractionEngine().extract_role(analysis.cleaned_text)
                return RoleExtractionAdapter().to_role_profile(result, analysis.language)
            except Exception:
                pass

        extraction_text = self._best_text(analysis)
        response = self.router.run(
            AIRequest(
                task="job_description_extraction",
                prompt_id="job.extract.v1",
                input_text=extraction_text,
            )
        )
        data = response.structured_data

        role_title = self._infer_title(analysis.cleaned_text, data.get("role_title"))
        required_skills = self._extract_required_skills(extraction_text)
        preferred_skills = self._extract_preferred_skills(extraction_text, required_skills)
        minimum_years = self.signals.extract_years_experience(extraction_text)
        target_salary, maximum_salary = self._extract_salary(extraction_text)

        envelope = self.validator.validate_required_fields(
            "RoleProfile",
            {"role_title": role_title},
            ["role_title"],
        )

        return RoleProfile(
            role_title=role_title,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=self._extract_bullets(analysis, "responsibilities") or self.signals.extract_responsibilities(extraction_text),
            languages=self.signals.extract_languages(extraction_text),
            certifications=self.signals.extract_certifications(extraction_text),
            minimum_years_experience=minimum_years,
            target_salary=target_salary,
            maximum_salary=maximum_salary,
            raw_excerpt=extraction_text[:1200],
            language=analysis.language,
            extraction_status=envelope.validation_status,
        )

    def to_role_requirements(self, profile: RoleProfile):
        from talentcopilot.decision_core.fit_intelligence_models import RoleRequirements

        return RoleRequirements(
            role_title=profile.role_title,
            required_skills=profile.required_skills,
            preferred_skills=profile.preferred_skills,
            minimum_years_experience=profile.minimum_years_experience,
        )

    def _should_use_llm(self) -> bool:
        flag = os.environ.get("TALENTCOPILOT_USE_LLM_EXTRACTION", "auto").lower()
        if flag in {"true", "1", "yes"}:
            return True
        if flag in {"false", "0", "no", "mock"}:
            return False
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _best_text(self, analysis: JobAnalysis) -> str:
        if not analysis.sections:
            return analysis.cleaned_text[:6000]
        priority = ["overview", "requirements", "responsibilities", "preferred", "languages", "compensation"]
        selected = []
        for title in priority:
            selected.extend(section.content for section in analysis.sections if section.title == title)
        return "\n\n".join(selected)[:6000] if selected else analysis.cleaned_text[:6000]

    def _infer_title(self, text: str, fallback: str | None = None) -> str:
        if fallback and fallback != "Unknown Role":
            return fallback
        for line in (text or "").splitlines():
            clean = line.strip(" -•*")
            lower = clean.lower()
            if clean and len(clean) < 90 and not any(marker in lower for marker in ["requirements", "responsibilities", "missions", "skills", "compétences"]):
                return clean
        return fallback or "Unknown Role"

    def _extract_required_skills(self, text: str) -> list[str]:
        return self.ontology.extract_skills(text)

    def _extract_preferred_skills(self, text: str, required: list[str]) -> list[str]:
        lower = (text or "").lower()
        preferred_zone = ""
        for marker in ["preferred", "nice to have", "souhaité", "atouts"]:
            if marker in lower:
                preferred_zone = lower.split(marker, 1)[1]
                break
        preferred = self.ontology.extract_skills(preferred_zone) if preferred_zone else []
        return [skill for skill in preferred if skill not in required][:8]

    def _extract_salary(self, text: str):
        raw_numbers = re.findall(r"\d+", text or "")
        numbers = []
        for raw in raw_numbers:
            try:
                value = int(raw)
            except ValueError:
                continue
            if 20000 <= value <= 300000:
                numbers.append(value)
        if len(numbers) >= 2:
            return min(numbers), max(numbers)
        if len(numbers) == 1:
            return None, numbers[0]
        return None, None

    def _extract_bullets(self, analysis: JobAnalysis, title: str) -> list[str]:
        items = []
        for section in analysis.sections:
            if section.title == title:
                for line in section.content.splitlines():
                    clean = line.strip("-•* ").strip()
                    if clean:
                        items.append(clean)
        return items[:10]
