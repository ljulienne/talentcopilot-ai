import re

from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.ai_core.structured_outputs import StructuredOutputValidator
from talentcopilot.job_intelligence.models import JobAnalysis, RoleProfile


class RoleProfileExtractor:
    KNOWN_SKILLS = [
        "HRIS", "Workday", "SuccessFactors", "SAP", "Project Management",
        "Stakeholder Management", "Leadership", "Change Management",
        "Python", "API", "Payroll", "Reporting", "Power BI",
    ]

    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()
        self.validator = StructuredOutputValidator()

    def extract(self, analysis: JobAnalysis) -> RoleProfile:
        extraction_text = self._best_text(analysis)
        response = self.router.run(
            AIRequest(
                task="job_description_extraction",
                prompt_id="job.extract.v1",
                input_text=extraction_text,
            )
        )
        data = response.structured_data

        role_title = data.get("role_title") or self._infer_title(analysis.cleaned_text)
        required_skills = self._extract_skills(extraction_text)
        minimum_years = self._extract_years(extraction_text)
        target_salary, maximum_salary = self._extract_salary(extraction_text)

        envelope = self.validator.validate_required_fields(
            "RoleProfile",
            {"role_title": role_title},
            ["role_title"],
        )

        return RoleProfile(
            role_title=role_title,
            required_skills=required_skills,
            preferred_skills=list(dict.fromkeys(data.get("required_skills", []) or []))[:5],
            responsibilities=self._extract_bullets(analysis, "responsibilities"),
            languages=self._extract_languages(extraction_text),
            certifications=self._extract_certifications(extraction_text),
            minimum_years_experience=minimum_years,
            target_salary=target_salary,
            maximum_salary=maximum_salary,
            raw_excerpt=extraction_text[:800],
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

    def _best_text(self, analysis: JobAnalysis) -> str:
        if not analysis.sections:
            return analysis.cleaned_text[:4000]
        priority = ["overview", "requirements", "responsibilities", "preferred", "languages", "compensation"]
        selected = []
        for title in priority:
            selected.extend(section.content for section in analysis.sections if section.title == title)
        return "\n\n".join(selected)[:4000] if selected else analysis.cleaned_text[:4000]

    def _infer_title(self, text: str) -> str:
        for line in (text or "").splitlines():
            clean = line.strip()
            if clean and len(clean) < 80:
                return clean
        return "Unknown Role"

    def _extract_skills(self, text: str) -> list[str]:
        lower = text.lower()
        found = []
        for skill in self.KNOWN_SKILLS:
            if skill.lower() in lower:
                found.append(skill)
        return list(dict.fromkeys(found))

    def _extract_years(self, text: str) -> int:
        patterns = [
            r"(\d+)\+?\s+years",
            r"(\d+)\+?\s+ans",
            r"minimum\s+(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, (text or "").lower())
            if match:
                return int(match.group(1))
        return 0

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

    def _extract_languages(self, text: str) -> list[str]:
        lower = (text or "").lower()
        languages = []
        for language in ["English", "French", "Mandarin", "Chinese", "Spanish"]:
            if language.lower() in lower:
                languages.append(language)
        return languages

    def _extract_certifications(self, text: str) -> list[str]:
        lower = (text or "").lower()
        certs = []
        for cert in ["PMP", "PHRi", "SPHRi", "Prince2", "Scrum"]:
            if cert.lower() in lower:
                certs.append(cert)
        return certs
