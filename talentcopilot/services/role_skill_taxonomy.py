"""Deterministic recruitment skill taxonomy.

The module converts verbose job requirements and heterogeneous CV skill
labels into a compact set of comparable recruitment capabilities.

It deliberately uses no LLM, cache, model download or environment-specific
dependency.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


# Stable capabilities used by the official recruitment fit score.
OFFICIAL_ROLE_CAPABILITIES: tuple[str, ...] = (
    "HRIS",
    "Project Management",
    "Change Management",
    "Reporting",
    "SAP SuccessFactors",
    "International Experience",
    "French",
    "English",
)


def _plain(value: object) -> str:
    text = unicodedata.normalize(
        "NFKD",
        str(value or ""),
    )
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    text = text.casefold()
    text = re.sub(r"[^a-z0-9+#]+", " ", text)
    return " ".join(text.split())


_PATTERNS: dict[str, tuple[str, ...]] = {
    "HRIS": (
        "hris",
        "human resources information system",
        "human resource information system",
        "core hr",
        "hr system",
        "hr systems",
        "hr technology",
        "people system",
        "peoplesoft",
        "workday hris",
        "talentsoft",
        "sap hr",
        "payroll system",
        "time and attendance",
    ),
    "Project Management": (
        "project management",
        "project manager",
        "program management",
        "programme management",
        "project planning",
        "project monitoring",
        "implementation",
        "deployment",
        "migration",
        "requirements",
        "acceptance testing",
        "vendor management",
        "solution provider",
        "risk management",
        "corrective action",
        "steering committee",
        "project committee",
    ),
    "Change Management": (
        "change management",
        "change adoption",
        "communication and training",
        "communications and training",
        "training and communication",
        "user adoption",
        "transformation",
    ),
    "Reporting": (
        "reporting",
        "power bi",
        "business intelligence",
        "analytics",
        "data analysis",
        "dashboard",
        "dashboards",
        "data reliability",
        "data cleaning",
        "business objects",
    ),
    "SAP SuccessFactors": (
        "sap successfactors",
        "successfactors",
        "success factors",
    ),
    "International Experience": (
        "international experience",
        "international environment",
        "international deployment",
        "international project",
        "global project",
        "global environment",
        "multinational",
        "multi country",
        "multi-country",
        "large group",
    ),
    "French": (
        "french",
        "francais",
        "francophone",
    ),
    "English": (
        "english",
        "anglais",
        "anglophone",
    ),
}


def capability_set(value: object) -> set[str]:
    """Return official capabilities evidenced by one label or phrase."""

    normalized = _plain(value)

    if not normalized:
        return set()

    capabilities: set[str] = set()

    for capability, patterns in _PATTERNS.items():
        for pattern in patterns:
            normalized_pattern = _plain(pattern)

            if normalized_pattern in normalized:
                capabilities.add(capability)
                break

    return capabilities


def capability_set_many(values: Iterable[object]) -> set[str]:
    capabilities: set[str] = set()

    for value in values or ():
        capabilities.update(capability_set(value))

    return capabilities


def ordered_capabilities(values: Iterable[object]) -> list[str]:
    """Return unique capabilities in the official stable order."""

    detected = capability_set_many(values)

    return [
        capability
        for capability in OFFICIAL_ROLE_CAPABILITIES
        if capability in detected
    ]


def candidate_role_matches(
    candidate_skills: Iterable[object],
    role_skills: Iterable[object],
) -> tuple[list[str], list[str]]:
    """Return matched and missing official role capabilities."""

    candidate = capability_set_many(candidate_skills)
    role = set(ordered_capabilities(role_skills))

    matched = [
        capability
        for capability in OFFICIAL_ROLE_CAPABILITIES
        if capability in role and capability in candidate
    ]

    missing = [
        capability
        for capability in OFFICIAL_ROLE_CAPABILITIES
        if capability in role and capability not in candidate
    ]

    return matched, missing
