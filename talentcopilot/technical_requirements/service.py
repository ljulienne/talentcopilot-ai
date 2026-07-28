from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping

from talentcopilot.technical_requirements.models import (
    CandidateRequirementEvidence,
    TechnicalRequirement,
    TechnicalRequirementCatalog,
)


class TechnicalRequirementService:
    """One deterministic source of truth for role-specific requirements.

    The service preserves exact technologies and delivery expectations instead
    of collapsing them into generic labels. It is presentation/evaluation
    intelligence only and never changes the canonical fit score or rank.
    """

    VERSION = "7.6.0"
    MAX_RADAR_AXES = 9

    # Ordered by decision value for the role-aligned radar.
    _DEFINITIONS = (
        {
            "name": "SAP SuccessFactors & Core HR",
            "category": "Technology & HRIS",
            "family": "HRIS Platforms",
            "kind": "technical_platform",
            "importance": "Critical",
            "level": 5.0,
            "aliases": ("sap successfactors", "successfactors", "success factors"),
            "related": (
                "core hr", "hris", "sirh", "workday", "peoplesoft", "oracle hcm",
                "oracle hr", "sap hr", "talentsoft", "saba", "cornerstone", "tapplent",
                "premium rh", "seditweb", "sedit web", "employee central",
            ),
            "triggers": ("successfactors", "core hr"),
        },
        {
            "name": "Power BI & HR Reporting",
            "category": "Data & Analytics",
            "family": "Business Intelligence",
            "kind": "technical_tool",
            "importance": "Critical",
            "level": 4.0,
            "aliases": ("power bi", "powerbi", "microsoft power bi"),
            "related": (
                "tableau", "qlik", "qliksense", "business objects", "reporting",
                "dashboard", "dashboards", "people analytics", "hr analytics", "dax",
                "power query",
            ),
            "triggers": ("power bi",),
        },
        {
            "name": "AI Solutions for HR",
            "category": "Innovation & Data",
            "family": "Applied Artificial Intelligence",
            "kind": "technical_innovation",
            "importance": "High",
            "level": 3.0,
            "aliases": (
                "artificial intelligence", "ai solution", "ai solutions", "generative ai",
                "machine learning", "intelligence artificielle", "solution ia", "solutions ia",
            ),
            "related": (
                "data science", "python", "analytics", "automation", "predictive",
                "ibm data science", "natural language processing", "nlp",
            ),
            "triggers": ("artificial intelligence", " ai ", "intelligence artificielle", "solution ia"),
        },
        {
            "name": "HRIS Project Leadership",
            "category": "Leadership & Delivery",
            "family": "Programme Delivery",
            "kind": "delivery_capability",
            "importance": "Critical",
            "level": 5.0,
            "aliases": (
                "hris project management", "hris project manager", "project management",
                "program management", "programme management", "project leadership",
            ),
            "related": ("implementation", "deployment", "migration", "project manager", "programme"),
            "triggers": ("hris project", "complex hris projects", "project management"),
        },
        {
            "name": "Interfaces & Technical Delivery",
            "category": "Technology & HRIS",
            "family": "Integration & Testing",
            "kind": "technical_delivery",
            "importance": "High",
            "level": 4.0,
            "aliases": (
                "interfaces with third-party systems", "third party interfaces", "system interfaces",
                "api integration", "interfaces", "integration", "acceptance testing", "uat", "sit",
                "functional testing", "technical testing",
            ),
            "related": ("api", "web service", "data flow", "integration", "testing", "migration"),
            "triggers": ("interface", "acceptance testing", "technical acceptance", "third-party systems"),
        },
        {
            "name": "Data Quality & Core HR Reliability",
            "category": "Data & Analytics",
            "family": "Data Governance",
            "kind": "data_governance",
            "importance": "High",
            "level": 4.0,
            "aliases": (
                "data cleaning", "data reliability", "data quality", "data accuracy",
                "data integrity", "core hr data", "data governance",
            ),
            "related": ("rgpd", "gdpr", "sql", "reporting", "validation", "payroll data"),
            "triggers": ("data cleaning", "data reliability", "data quality", "core hr data"),
        },
        {
            "name": "Change Management & Adoption",
            "category": "Transformation",
            "family": "Change & Adoption",
            "kind": "functional_capability",
            "importance": "High",
            "level": 4.0,
            "aliases": (
                "change management", "user adoption", "communication and training plans",
                "training plans", "post-deployment support", "upskilling", "conduite du changement",
            ),
            "related": ("training", "communication", "support", "transformation", "adoption"),
            "triggers": ("change management", "adopting new tools", "communication and training"),
        },
        {
            "name": "Vendor & Stakeholder Management",
            "category": "Leadership & Delivery",
            "family": "Stakeholder Governance",
            "kind": "delivery_capability",
            "importance": "High",
            "level": 4.0,
            "aliases": (
                "solution providers", "external providers management", "vendor management",
                "integrators", "steering committees", "project committees", "stakeholder management",
            ),
            "related": ("vendor", "provider", "supplier", "integrator", "stakeholder", "committee", "liaising"),
            "triggers": ("solution providers", "providers management", "integrators", "steering committees"),
        },
        {
            "name": "Team Leadership & International Delivery",
            "category": "Leadership & Delivery",
            "family": "People & International Leadership",
            "kind": "leadership_capability",
            "importance": "High",
            "level": 4.0,
            "aliases": (
                "management experience", "supporting collaborators", "team leadership", "team management",
                "international environment", "international projects", "large group", "multi-country",
            ),
            "related": ("managed", "led a team", "team member", "global", "international", "countries", "regions"),
            "triggers": ("internal collaborator", "management", "international environment", "large group"),
        },
    )

    _ELIGIBILITY_PATTERNS = (
        ("Minimum experience", ("minimum of 10 years", "10 years of", "minimum 10 years")),
        ("Higher education", ("higher education degree", "bac+5", "master")),
        ("French and English", ("fluent french and english", "french and english", "français et anglais")),
    )

    def catalog(self, job: Mapping | None) -> TechnicalRequirementCatalog:
        job = dict(job or {})
        text = str(job.get("raw_text") or job.get("description") or "")
        role_title = str(job.get("title") or "Recruitment")

        embedded = job.get("technical_requirements") or []
        if embedded:
            parsed = tuple(self._from_mapping(item) for item in embedded if isinstance(item, Mapping))
            parsed = tuple(item for item in parsed if item is not None)
            if parsed:
                return TechnicalRequirementCatalog(
                    role_title=role_title,
                    requirements=parsed[: self.MAX_RADAR_AXES],
                    eligibility_checks=self._eligibility(text),
                )

        requirements = self.extract(text, fallback=job.get("required_skills") or [])
        return TechnicalRequirementCatalog(
            role_title=role_title,
            requirements=tuple(requirements[: self.MAX_RADAR_AXES]),
            eligibility_checks=self._eligibility(text),
        )

    def extract(self, text: str, *, fallback=()) -> list[TechnicalRequirement]:
        plain = self._plain(text)
        padded = f" {plain} "
        found: list[TechnicalRequirement] = []
        for definition in self._DEFINITIONS:
            matched = next(
                (
                    trigger
                    for trigger in definition["triggers"]
                    if self._plain(trigger).strip() and self._plain(trigger) in padded
                ),
                None,
            )
            if matched is None:
                continue
            source = self._source_excerpt(text, matched)
            found.append(self._build(definition, source))

        if not found:
            for raw in fallback or ():
                name = str(raw.get("name") if isinstance(raw, Mapping) else raw or "").strip()
                if not name:
                    continue
                found.append(
                    TechnicalRequirement(
                        requirement_id=self._slug(name),
                        name=name,
                        category=self._fallback_category(name),
                        family="Role requirement",
                        requirement_kind="general_capability",
                        importance="Critical",
                        required_level=4.0,
                        source_excerpt="Extracted from the role requirements.",
                        aliases=(name,),
                        related_terms=(),
                        interview_priority="Validate",
                    )
                )
        return found[: self.MAX_RADAR_AXES]

    def evaluate_candidate(
        self,
        requirement: TechnicalRequirement | Mapping,
        candidate: Mapping | None,
    ) -> CandidateRequirementEvidence:
        req = requirement if isinstance(requirement, TechnicalRequirement) else self._from_mapping(requirement)
        if req is None:
            raise ValueError("A valid technical requirement is required.")
        candidate = dict(candidate or {})
        text_parts = [
            str(candidate.get("raw_text") or ""),
            " ".join(str(item) for item in candidate.get("skills", []) or []),
            " ".join(str(item) for item in candidate.get("achievements", []) or []),
        ]
        raw = "\n".join(text_parts)
        plain = f" {self._plain(raw)} "

        direct_hits = self._hits(plain, req.aliases)
        related_hits = self._hits(plain, req.related_terms)
        action_depth = self._action_depth(raw, direct_hits)

        if direct_hits:
            status = "Direct evidence"
            level = self._direct_level(req, raw, direct_hits, action_depth)
            confidence = "High" if action_depth >= 2 or len(direct_hits) >= 2 else "Moderate"
            priority = "Confirm depth" if level >= req.required_level * 0.7 else "Validate depth"
            evidence = self._candidate_excerpt(raw, direct_hits[0]) or f"Direct mention identified: {direct_hits[0]}."
            related = tuple(dict.fromkeys(related_hits))
        elif related_hits:
            status = "Related evidence"
            level = min(max(1.0, req.required_level * 0.45), 2.5)
            confidence = "Limited"
            priority = "Mandatory probe" if req.importance == "Critical" else "Validate transferability"
            evidence = (
                f"No direct evidence of {req.name} was identified. Related experience was found: "
                + ", ".join(list(dict.fromkeys(related_hits))[:4])
                + "."
            )
            related = tuple(dict.fromkeys(related_hits))
        else:
            status = "No direct evidence"
            level = 0.5 if req.importance != "Critical" else 0.0
            confidence = "Low"
            priority = "Mandatory probe" if req.importance in {"Critical", "High"} else "Validate"
            evidence = f"No direct or transferable evidence of {req.name} was identified in the current CV."
            related = ()

        return CandidateRequirementEvidence(
            requirement_id=req.requirement_id,
            requirement_name=req.name,
            evidence_status=status,
            estimated_level=round(min(5.0, max(0.0, level)), 1),
            confidence=confidence,
            evidence=evidence,
            related_evidence=related,
            interview_priority=priority,
        )

    def _direct_level(self, req, raw: str, hits: list[str], action_depth: int) -> float:
        level = 2.6
        level += min(0.8, 0.25 * len(hits))
        level += min(1.1, 0.35 * action_depth)
        if re.search(r"\b\d+(?:[.,]\d+)?\s*(?:%|users?|countries?|sites?|projects?|teams?)\b", raw, re.I):
            level += 0.3
        if req.requirement_kind == "technical_tool" and action_depth == 0:
            level = min(level, 3.0)
        return min(5.0, level)

    def _action_depth(self, raw: str, hits: list[str]) -> int:
        if not hits:
            return 0
        count = 0
        lower = raw.casefold()
        for marker in (
            "implemented", "launched", "designed", "built", "configured", "developed",
            "led", "managed", "created", "deployed", "validated", "tested", "piloted",
            "mis en place", "déployé", "conçu", "piloté", "lancé",
        ):
            if marker in lower:
                count += 1
        return min(4, count)

    def _hits(self, plain_text: str, terms) -> list[str]:
        hits = []
        for term in terms or ():
            normalized = self._plain(term)
            if normalized and f" {normalized} " in plain_text:
                hits.append(str(term))
            elif normalized and len(normalized) > 4 and normalized in plain_text:
                hits.append(str(term))
        return hits

    def _source_excerpt(self, text: str, trigger: str) -> str:
        return self._candidate_excerpt(text, trigger) or f"Requirement detected from: {trigger}."

    def _candidate_excerpt(self, text: str, term: str) -> str:
        lines = [" ".join(line.split()) for line in str(text or "").splitlines() if line.strip()]
        needle = self._plain(term)
        for line in lines:
            if needle and needle in self._plain(line):
                return line[:300]
        clean = " ".join(str(text or "").split())
        normalized = self._plain(clean)
        index = normalized.find(needle)
        if index < 0:
            return ""
        # Normalized indices are approximate; return a compact readable segment.
        return clean[max(0, index - 80): index + len(term) + 180].strip()[:300]

    def _build(self, definition: Mapping, source: str) -> TechnicalRequirement:
        return TechnicalRequirement(
            requirement_id=self._slug(definition["name"]),
            name=definition["name"],
            category=definition["category"],
            family=definition["family"],
            requirement_kind=definition["kind"],
            importance=definition["importance"],
            required_level=float(definition["level"]),
            source_excerpt=source,
            aliases=tuple(definition["aliases"]),
            related_terms=tuple(definition["related"]),
            interview_priority="Mandatory probe" if definition["importance"] == "Critical" else "Validate",
        )

    def _from_mapping(self, item: Mapping) -> TechnicalRequirement | None:
        name = str(item.get("name") or item.get("competency") or "").strip()
        if not name:
            return None
        return TechnicalRequirement(
            requirement_id=str(item.get("requirement_id") or self._slug(name)),
            name=name,
            category=str(item.get("category") or self._fallback_category(name)),
            family=str(item.get("family") or "Role requirement"),
            requirement_kind=str(item.get("requirement_kind") or "general_capability"),
            importance=str(item.get("importance") or "High"),
            required_level=float(item.get("required_level") or 4.0),
            source_excerpt=str(item.get("source_excerpt") or ""),
            aliases=tuple(item.get("aliases") or (name,)),
            related_terms=tuple(item.get("related_terms") or ()),
            interview_priority=str(item.get("interview_priority") or "Validate"),
        )

    def _eligibility(self, text: str) -> tuple[str, ...]:
        plain = self._plain(text)
        return tuple(
            label
            for label, patterns in self._ELIGIBILITY_PATTERNS
            if any(self._plain(pattern) in plain for pattern in patterns)
        )

    @staticmethod
    def _plain(value: object) -> str:
        text = unicodedata.normalize("NFKD", str(value or ""))
        text = "".join(char for char in text if not unicodedata.combining(char))
        text = text.casefold().replace("&", " and ")
        text = re.sub(r"[^a-z0-9+#]+", " ", text)
        return " ".join(text.split())

    @staticmethod
    def _slug(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "-", str(value or "item").casefold()).strip("-") or "item"

    @staticmethod
    def _fallback_category(name: str) -> str:
        value = name.casefold()
        if any(token in value for token in ("data", "report", "power bi", "analytics")):
            return "Data & Analytics"
        if any(token in value for token in ("hris", "sap", "system", "interface", "technical")):
            return "Technology & HRIS"
        if any(token in value for token in ("lead", "manage", "stakeholder", "project")):
            return "Leadership & Delivery"
        return "Role capability"
