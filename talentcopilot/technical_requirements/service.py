from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping

from talentcopilot.technical_requirements.extractor import DomainAgnosticRequirementExtractor
from talentcopilot.technical_requirements.models import (
    CandidateRequirementEvidence,
    TechnicalRequirement,
    TechnicalRequirementCatalog,
)


class TechnicalRequirementService:
    """Unified, domain-agnostic role requirement intelligence.

    Exact technologies and role capabilities are extracted from the offer at
    runtime. An optional grounded LLM pass can enrich the deterministic output,
    while the deterministic engine remains the safe offline fallback. This
    service is evaluation/presentation intelligence only and never changes the
    canonical fit score or rank.
    """

    VERSION = "7.7.0"
    MAX_RADAR_AXES = 9

    def __init__(self, extractor: DomainAgnosticRequirementExtractor | None = None):
        self.extractor = extractor or DomainAgnosticRequirementExtractor()

    def catalog(self, job: Mapping | None) -> TechnicalRequirementCatalog:
        job = dict(job or {})
        text = str(job.get("raw_text") or job.get("description") or "")
        role_title = str(job.get("title") or "Recruitment")

        embedded = job.get("technical_requirements") or []
        embedded_version = str(job.get("technical_requirement_engine_version") or "")
        if embedded:
            parsed = tuple(self._from_mapping(item) for item in embedded if isinstance(item, Mapping))
            parsed = tuple(item for item in parsed if item is not None)
            # A 7.7+ embedded catalogue is authoritative. Older specialised
            # catalogues are regenerated from raw text to avoid carrying their
            # domain assumptions into a new session.
            if parsed and embedded_version.startswith("7.7"):
                return TechnicalRequirementCatalog(
                    role_title=role_title,
                    requirements=parsed[: self.MAX_RADAR_AXES],
                    eligibility_checks=self.extractor.eligibility(text),
                    extraction_method=str(job.get("technical_requirement_extraction_method") or "embedded"),
                )

        requirements, method = self.extract_with_method(
            text,
            role_title=role_title,
            fallback=job.get("required_skills") or [],
        )
        return TechnicalRequirementCatalog(
            role_title=role_title,
            requirements=tuple(requirements[: self.MAX_RADAR_AXES]),
            eligibility_checks=self.extractor.eligibility(text),
            extraction_method=method,
        )

    def extract(self, text: str, *, fallback=(), role_title: str = "Recruitment") -> list[TechnicalRequirement]:
        requirements, _ = self.extract_with_method(text, fallback=fallback, role_title=role_title)
        return requirements

    def extract_with_method(
        self,
        text: str,
        *,
        fallback=(),
        role_title: str = "Recruitment",
    ) -> tuple[list[TechnicalRequirement], str]:
        return self.extractor.extract(
            text,
            role_title=role_title,
            fallback=fallback,
            limit=self.MAX_RADAR_AXES,
        )

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
            "\n".join(str(item) for item in candidate.get("skills", []) or []),
            "\n".join(str(item) for item in candidate.get("achievements", []) or []),
        ]
        raw = "\n".join(text_parts)
        plain = f" {self._plain(raw)} "

        aliases = tuple(dict.fromkeys(tuple(req.aliases) + tuple(req.components) + (req.name,)))
        direct_hits = self._hits(plain, aliases)
        matched_components = tuple(
            component for component in (req.components or aliases)
            if self._hits(plain, (component,))
        )
        missing_components = tuple(
            component for component in (req.components or ())
            if component not in matched_components
        )

        candidate_entities = self.extractor.extract_candidate_entities(raw)
        related_entities = self._related_entities(req, candidate_entities)
        related_term_hits = self._hits(plain, req.related_terms)
        related_hits = list(dict.fromkeys(related_entities + related_term_hits))
        action_depth = self._action_depth(raw, direct_hits)

        if direct_hits:
            evidence = self._candidate_excerpt(raw, direct_hits[0]) or f"Direct mention identified: {direct_hits[0]}."
            if action_depth == 0 and not self._has_metric(evidence):
                status = "Ambiguous evidence"
                level = min(3.0, max(1.8, req.required_level * 0.55))
                confidence = "Limited"
                priority = "Validate depth"
            else:
                status = "Direct evidence"
                level = self._direct_level(req, raw, direct_hits, action_depth)
                confidence = "High" if action_depth >= 2 or self._has_metric(evidence) else "Moderate"
                priority = "Confirm depth" if level >= req.required_level * 0.7 else "Validate depth"
            related = tuple(related_hits)
        elif related_hits:
            status = "Related evidence"
            level = min(max(1.0, req.required_level * 0.45), 2.5)
            confidence = "Limited"
            priority = "Mandatory probe" if req.importance == "Critical" else "Validate transferability"
            evidence = (
                f"No direct evidence of {req.name} was identified. Related or transferable experience was found: "
                + ", ".join(related_hits[:5])
                + "."
            )
            related = tuple(related_hits)
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
            matched_components=matched_components,
            missing_components=missing_components,
            interview_priority=priority,
        )

    def _related_entities(
        self,
        requirement: TechnicalRequirement,
        candidate_entities: list[tuple[str, str, str]],
    ) -> list[str]:
        related: list[str] = []
        adjacent = set(self.extractor.adjacent_families(requirement.family))
        for entity, family, _excerpt in candidate_entities:
            if self._plain(entity) in {self._plain(value) for value in requirement.aliases + requirement.components}:
                continue
            if family == requirement.family or family in adjacent:
                related.append(entity)
        return list(dict.fromkeys(related))[:8]

    def _direct_level(self, req, raw: str, hits: list[str], action_depth: int) -> float:
        level = 2.5
        level += min(0.8, 0.25 * len(hits))
        level += min(1.2, 0.35 * action_depth)
        if self._has_metric(raw):
            level += 0.3
        if req.requirement_kind in {"technical_tool", "technical_platform"} and action_depth == 0:
            level = min(level, 3.0)
        return min(5.0, level)

    def _action_depth(self, raw: str, hits: list[str]) -> int:
        if not hits:
            return 0
        lines = [" ".join(line.split()) for line in str(raw or "").splitlines() if line.strip()]
        relevant = [
            line.casefold() for line in lines
            if any(self._plain(hit) in self._plain(line) for hit in hits)
        ]
        if not relevant:
            relevant = [str(raw or "").casefold()]
        count = 0
        for marker in self.extractor._ACTION_MARKERS:
            if any(marker in line for line in relevant):
                count += 1
        return min(4, count)

    @staticmethod
    def _has_metric(value: str) -> bool:
        return bool(re.search(r"\b\d+(?:[.,]\d+)?\s*(?:%|users?|countries?|sites?|projects?|teams?|m|k|million|hours?|days?)\b", value, re.I))

    def _hits(self, plain_text: str, terms) -> list[str]:
        hits: list[str] = []
        for term in terms or ():
            normalized = self._plain(term)
            if not normalized:
                continue
            if f" {normalized} " in plain_text:
                hits.append(str(term))
            elif len(normalized) > 4 and re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", plain_text):
                hits.append(str(term))
        return list(dict.fromkeys(hits))

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
        return clean[max(0, index - 80): index + len(term) + 180].strip()[:300]

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
            components=tuple(item.get("components") or (name,)),
            context_terms=tuple(item.get("context_terms") or ()),
            interview_priority=str(item.get("interview_priority") or "Validate"),
            extraction_method=str(item.get("extraction_method") or "embedded"),
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
        if any(token in value for token in ("data", "report", "analytics", "database")):
            return "Data & Analytics"
        if any(token in value for token in ("system", "software", "platform", "technical", "cloud", "api")):
            return "Technology & Tools"
        if any(token in value for token in ("lead", "manage", "stakeholder", "project")):
            return "Leadership & Delivery"
        return "Role Capability"
