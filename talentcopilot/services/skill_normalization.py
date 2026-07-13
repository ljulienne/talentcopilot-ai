"""Canonical bilingual HRIS skill normalisation."""

from __future__ import annotations

import re
import unicodedata


ALIASES = {
    "hris": {
        "hris", "sirh", "human resources information systems",
        "human resource information systems", "hr systems", "people systems",
    },
    "project management": {
        "project management", "gestion de projet", "gestion de projets",
        "program management", "programme management", "delivery management",
    },
    "change management": {
        "change management", "conduite du changement",
        "organizational change", "organisation transformation",
        "hr transformation", "user adoption",
    },
    "core hr": {
        "core hr", "employee data", "personnel administration",
        "employee central", "hr master data", "hr data management",
    },
    "successfactors": {
        "successfactors", "sap successfactors", "employee central",
    },
    "power bi": {
        "power bi", "microsoft power bi", "business intelligence",
        "hr analytics", "people analytics",
    },
    "reporting": {
        "reporting", "analytics", "business objects", "qliksense",
        "tableau", "dashboards", "data visualization",
    },
    "interfaces": {
        "interfaces", "system interface", "system interfaces",
        "system integration", "system integrations", "integrations",
        "third-party system", "third-party systems",
        "third-party integration", "third-party integrations",
        "api integration", "api integrations", "payroll interface",
        "payroll interfaces",
    },
    "data quality": {
        "data quality", "data cleaning", "data reliability",
        "data accuracy", "data integrity",
    },
    "stakeholder management": {
        "stakeholder management", "business partnering",
        "steering committee", "project committee",
        "cross-functional", "vendor management",
    },
    "vendor management": {
        "vendor management", "provider management", "integrator management",
        "solution providers", "vendors",
    },
    "international": {
        "international", "multi-country", "global", "emea",
        "asia pacific", "multi country",
    },
    "testing": {
        "testing", "uat", "sit", "acceptance testing",
        "functional testing", "technical acceptance",
    },
    "management": {
        "management", "team management", "people management",
        "coaching", "supporting collaborators", "line management",
    },
}


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9+#]+", " ", text)
    return " ".join(text.split())


def canonical_skill(value: str) -> str:
    normalized = normalize_text(value)
    for canonical, aliases in ALIASES.items():
        normalized_aliases = {normalize_text(alias) for alias in aliases}
        if normalized in normalized_aliases:
            return canonical
    return normalized


def canonical_skill_set(values) -> set[str]:
    return {
        canonical_skill(value)
        for value in (values or [])
        if str(value or "").strip()
    }
