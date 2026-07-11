from __future__ import annotations

import re
import unicodedata


DEFAULT_ALIASES: dict[str, tuple[str, ...]] = {
    "HRIS": ("hris", "sirh", "human resources information system", "human resource information system"),
    "Project Management": ("project management", "gestion de projet", "project lead", "project leadership", "pm"),
    "Payroll": ("payroll", "paie", "payroll management"),
    "Workforce Management": ("workforce management", "gta", "time and attendance", "gestion des temps"),
    "Change Management": ("change management", "conduite du changement", "change enablement"),
    "Stakeholder Management": ("stakeholder management", "gestion des parties prenantes", "stakeholder engagement"),
    "Data Analytics": ("data analytics", "analytics", "analyse de donnees", "data analysis"),
    "Artificial Intelligence": ("artificial intelligence", "ai", "ia", "generative ai", "genai"),
    "Python": ("python",),
    "SQL": ("sql",),
    "SAP Payroll": ("sap payroll", "sap hcm payroll", "sap paie"),
    "Workday": ("workday", "workday hcm"),
    "Business Objects": ("business objects", "sap businessobjects", "bo reporting"),
    "Leadership": ("leadership", "team leadership", "people leadership", "management d equipe"),
}

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("AI & Data", ("python", "sql", "data", "analytics", "artificial intelligence", "ai", "machine learning", "business objects")),
    ("HR Technology", ("hris", "workday", "sap", "payroll", "workforce management", "gta")),
    ("Delivery", ("project management", "program management", "change management", "agile", "scrum")),
    ("Leadership", ("leadership", "stakeholder", "coaching", "management")),
)


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


class SkillsTaxonomy:
    def __init__(self, aliases: dict[str, tuple[str, ...]] | None = None):
        self.aliases = aliases or DEFAULT_ALIASES
        self._lookup: dict[str, str] = {}
        for canonical, values in self.aliases.items():
            self._lookup[normalize_text(canonical)] = canonical
            for alias in values:
                self._lookup[normalize_text(alias)] = canonical

    def canonicalize(self, skill: str) -> str:
        normalized = normalize_text(skill)
        if not normalized:
            return ""
        return self._lookup.get(normalized, self._title(skill))

    def category_for(self, canonical_skill: str) -> str:
        normalized = normalize_text(canonical_skill)
        for category, markers in CATEGORY_RULES:
            if any(normalize_text(marker) in normalized for marker in markers):
                return category
        return "Business & Functional"

    @staticmethod
    def _title(value: str) -> str:
        words = re.split(r"\s+", value.strip())
        return " ".join(word.upper() if word.casefold() in {"hris", "sql", "ai", "sap"} else word.capitalize() for word in words)
