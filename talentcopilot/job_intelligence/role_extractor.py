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

    DETERMINISTIC_MODE = "deterministic"
    ENRICHED_MODE = "enriched"
    AUTO_MODE = "auto"

    VALID_MODES = {
        DETERMINISTIC_MODE,
        ENRICHED_MODE,
        AUTO_MODE,
    }

    def __init__(self, router: LLMRouter | None=None, *, extraction_mode: str=AUTO_MODE):
        normalized_mode = str(extraction_mode or self.AUTO_MODE).strip().lower()
        if normalized_mode not in self.VALID_MODES:
            raise ValueError(f'Unsupported extraction mode: {extraction_mode!r}')
        self.extraction_mode = normalized_mode
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
        location = self.extract_location(analysis.cleaned_text, data.get("location"))
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
            location=location,
            remote_policy=str(data.get("remote_policy") or ""),
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
        """Return whether optional LLM enrichment is enabled."""

        if self.extraction_mode == self.DETERMINISTIC_MODE:
            return False

        if self.extraction_mode == self.ENRICHED_MODE:
            return True

        flag = os.environ.get(
            "TALENTCOPILOT_USE_LLM_EXTRACTION",
            "auto",
        ).strip().lower()

        if flag in {"true", "1", "yes"}:
            return True

        if flag in {"false", "0", "no", "mock"}:
            return False

        return bool(
            os.environ.get("OPENAI_API_KEY")
        )

    def _best_text(self, analysis: JobAnalysis) -> str:
        if not analysis.sections:
            return analysis.cleaned_text[:6000]
        priority = ["overview", "requirements", "responsibilities", "preferred", "languages", "compensation"]
        selected = []
        for title in priority:
            selected.extend(section.content for section in analysis.sections if section.title == title)
        return "\n\n".join(selected)[:6000] if selected else analysis.cleaned_text[:6000]

    _STRUCTURAL_LABELS = {
        "location", "localisation", "lieu", "job description", "description du poste",
        "position", "poste", "about", "company", "department", "employment type",
        "job type", "responsibilities", "responsabilités", "missions", "requirements",
        "profile", "profil", "skills", "competencies", "compétences", "salary",
        "remote", "remote policy", "reporting to", "date", "additional information",
    }

    def _infer_title(self, text: str, fallback: str | None = None) -> str:
        line_candidate = self._title_from_lines(text)
        fallback_candidate = self.clean_role_title(fallback or "", text)

        # A standalone heading at the beginning of the document is more reliable
        # than a mock/LLM response that may have absorbed the following field
        # label (for example: "HRIS Manager Location").
        if line_candidate:
            return line_candidate
        if fallback_candidate and fallback_candidate != "Unknown Role":
            return fallback_candidate
        return "Unknown Role"

    @classmethod
    def clean_role_title(cls, value: str | None, text: str = "") -> str:
        clean = " ".join(str(value or "").replace("\n", " ").split()).strip(" -•*|:;")
        clean = re.sub(r"^(?:job\s+title|position|poste|role|intitulé(?:\s+du\s+poste)?)\s*[:\-]\s*", "", clean, flags=re.I)
        if not clean:
            return ""

        # Remove one or more structural field labels accidentally appended to
        # the role title by deterministic or LLM extraction.
        words = clean.split()
        while words:
            removed = False
            for width in (3, 2, 1):
                if len(words) < width:
                    continue
                suffix = " ".join(words[-width:]).casefold().strip(" :")
                if suffix in cls._STRUCTURAL_LABELS:
                    words = words[:-width]
                    removed = True
                    break
            if not removed:
                break
        clean = " ".join(words).strip(" -•*|:;")
        if clean.isupper():
            acronyms = {"HR", "HRIS", "IT", "AI", "BI", "ERP", "CRM", "CEO", "CFO", "CTO", "COO", "APAC", "EMEA", "UX", "UI", "QA"}
            clean = " ".join(word if word in acronyms else word.title() for word in clean.split())
        return clean[:120]

    @classmethod
    def extract_location(cls, text: str, fallback: str | None = None) -> str:
        fallback_clean = " ".join(str(fallback or "").split()).strip(" -•*|:;")
        if fallback_clean and fallback_clean.casefold() not in cls._STRUCTURAL_LABELS:
            return fallback_clean[:160]

        lines = [" ".join(line.split()).strip() for line in str(text or "").splitlines()]
        for index, line in enumerate(lines):
            match = re.match(
                r"^(?:location|localisation|lieu|work\s+location|based\s+in)\s*[:\-]?\s*(.*)$",
                line,
                flags=re.I,
            )
            if not match:
                continue
            inline = match.group(1).strip(" -•*|:;")
            if inline and inline.casefold() not in cls._STRUCTURAL_LABELS:
                return inline[:160]
            for following in lines[index + 1:index + 4]:
                candidate = following.strip(" -•*|:;")
                if not candidate:
                    continue
                if candidate.casefold() in cls._STRUCTURAL_LABELS:
                    break
                return candidate[:160]
        return ""

    @classmethod
    def _title_from_lines(cls, text: str) -> str:
        lines = [" ".join(line.split()).strip(" -•*|:;") for line in str(text or "").splitlines()]
        for line in lines[:18]:
            if not line or len(line) > 120:
                continue
            lower = line.casefold()
            if lower in cls._STRUCTURAL_LABELS:
                continue
            if any(lower.startswith(label + ":") for label in cls._STRUCTURAL_LABELS):
                continue
            if re.search(r"[.!?]$", line) and len(line.split()) > 7:
                continue
            candidate = cls.clean_role_title(line)
            if candidate and candidate.casefold() not in cls._STRUCTURAL_LABELS:
                return candidate
        return ""

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
