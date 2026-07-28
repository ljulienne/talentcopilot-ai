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

    VERSION = "7.7.1"
    MAX_RADAR_AXES = 10

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
            if parsed and embedded_version == self.VERSION:
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
        raw_text = str(candidate.get("raw_text") or "")
        skills_text = "\n".join(str(item) for item in candidate.get("skills", []) or [])
        achievements_text = "\n".join(str(item) for item in candidate.get("achievements", []) or [])
        searchable_raw = "\n".join((raw_text, skills_text, achievements_text))
        # Transferability must be grounded in a professional statement or a
        # relevant credential. A bare skill label is not enough.
        grounding_raw = "\n".join((raw_text, achievements_text))
        plain = f" {self._plain(searchable_raw)} "

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

        related_excerpts = self._grounded_related_evidence(req, grounding_raw)
        action_depth = self._action_depth(grounding_raw, direct_hits)

        if direct_hits:
            evidence = self._candidate_excerpt(grounding_raw, direct_hits[0])
            if not evidence:
                evidence = f"Mentioned in the candidate profile: {direct_hits[0]}."
            grounded_action = action_depth > 0 or self._has_action_signal(evidence)
            if not grounded_action and not self._has_metric(evidence):
                status = "Ambiguous evidence"
                level = min(3.0, max(1.8, req.required_level * 0.55))
                confidence = "Limited"
                priority = "Validate depth"
            else:
                status = "Direct evidence"
                effective_depth = max(action_depth, 1 if grounded_action else 0)
                level = self._direct_level(req, grounding_raw, direct_hits, effective_depth)
                confidence = "High" if effective_depth >= 2 or self._has_metric(evidence) else "Moderate"
                priority = "Confirm depth" if level >= req.required_level * 0.7 else "Validate depth"
            related = () if status == "Direct evidence" else tuple(related_excerpts[:2])
        elif related_excerpts:
            status = "Related evidence"
            level = min(max(1.0, req.required_level * 0.45), 2.5)
            confidence = "Moderate" if len(related_excerpts) >= 2 else "Limited"
            priority = "Mandatory probe" if req.importance == "Critical" else "Validate transferability"
            evidence = (
                f"No direct evidence of {req.name} was identified. "
                f"Grounded related evidence: {related_excerpts[0]}"
            )
            related = tuple(related_excerpts)
        else:
            status = "No direct evidence"
            level = 0.5 if req.importance != "Critical" else 0.0
            confidence = "Low"
            priority = "Mandatory probe" if req.importance in {"Critical", "High"} else "Validate"
            evidence = (
                f"No direct or sufficiently grounded related evidence of {req.name} "
                "was identified in the current CV."
            )
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

    def _grounded_related_evidence(
        self,
        requirement: TechnicalRequirement,
        raw: str,
    ) -> list[str]:
        """Return complete, grounded CV excerpts for transferable evidence.

        Related evidence is accepted only when it is attached to a substantive
        professional action, measurable outcome or relevant credential. Names,
        contact details, locations, headings and isolated job titles are rejected.
        """
        if not str(raw or "").strip():
            return []

        direct_terms = {
            self._plain(value)
            for value in requirement.aliases + requirement.components + (requirement.name,)
            if self._plain(value)
        }
        adjacent = set(self.extractor.adjacent_families(requirement.family))
        candidates: list[tuple[int, str]] = []

        for entity, family, excerpt in self.extractor.extract_candidate_entities(raw):
            entity_plain = self._plain(entity)
            if not entity_plain or entity_plain in direct_terms:
                continue
            relation_score = self._family_relation_score(requirement.family, family, adjacent)
            if relation_score <= 0:
                continue
            clean_excerpt = self._clean_evidence_excerpt(excerpt)
            if not self._is_grounded_professional_excerpt(clean_excerpt, anchor=entity):
                continue
            score = (
                relation_score
                + self._grounding_score(clean_excerpt)
                + self._transfer_fit_score(requirement, clean_excerpt)
            )
            candidates.append((score, clean_excerpt))

        # Some valid transferable evidence is a functional phrase rather than
        # a named product (for example Salary Review for an ICR requirement).
        relation_terms = tuple(dict.fromkeys(
            tuple(self._family_markers(requirement.family))
        ))
        for line in self.extractor._lines(raw):
            clean_line = self._clean_evidence_excerpt(line)
            if not self._is_grounded_professional_excerpt(clean_line):
                continue
            line_plain = self._plain(clean_line)
            if any(term and term in line_plain for term in direct_terms):
                continue
            matched = [term for term in relation_terms if self._contains_term(line_plain, term)]
            if not matched:
                continue
            # Generic family labels alone are not enough; require at least one
            # concrete term or a strong action/credential signal.
            concrete = [term for term in matched if self._is_concrete_related_term(term)]
            if not concrete and self._grounding_score(clean_line) < 3:
                continue
            candidates.append((
                2
                + self._grounding_score(clean_line)
                + min(2, len(concrete))
                + self._transfer_fit_score(requirement, clean_line),
                clean_line,
            ))

        # Recover evidence split across PDF lines by taking a bounded source
        # window around a concrete family marker, then requiring a grounding
        # signal inside that window.
        for term in relation_terms:
            if not self._is_concrete_related_term(term):
                continue
            window = self._source_window(raw, term)
            if not window or not self._is_grounded_professional_excerpt(window):
                continue
            candidates.append((
                3 + self._grounding_score(window) + self._transfer_fit_score(requirement, window),
                window,
            ))

        # Highest-quality grounded excerpts first, preserving only distinct
        # sentences. The UI and interview engine receive the source sentence,
        # never a detached entity label.
        ordered: list[str] = []
        seen: set[str] = set()
        for _score, excerpt in sorted(candidates, key=lambda item: (-item[0], len(item[1]))):
            key = self._plain(excerpt)
            if not key or key in seen:
                continue
            # Avoid near-duplicates where one excerpt fully contains another.
            if any(key in existing or existing in key for existing in seen):
                continue
            seen.add(key)
            ordered.append(excerpt)
            if len(ordered) >= 4:
                break
        return ordered

    @staticmethod
    def _family_relation_score(required_family: str, candidate_family: str, adjacent: set[str]) -> int:
        if candidate_family == required_family:
            return 4
        if candidate_family in adjacent:
            return 2
        return 0

    def _source_window(self, raw: str, term: object) -> str:
        clean = " ".join(str(raw or "").split())
        needle = " ".join(str(term or "").split())
        if not needle:
            return ""
        match = re.search(re.escape(needle), clean, re.I)
        if not match:
            for line in self.extractor._lines(raw):
                if self._contains_term(self._plain(line), needle):
                    return self._clean_evidence_excerpt(line)
            return ""

        # Prefer one complete bullet or sentence. This preserves the source
        # statement while preventing the evidence card from swallowing the
        # next experience or a second-column heading from a PDF.
        previous_bullet = clean.rfind("•", 0, match.start())
        previous_sentence = max(clean.rfind(". ", 0, match.start()), clean.rfind("; ", 0, match.start()))
        start = max(previous_bullet, previous_sentence + 1, 0)
        next_bullet = clean.find("•", match.end())
        next_sentence = clean.find(". ", match.end())
        end_candidates = [value for value in (next_bullet, next_sentence + 1 if next_sentence >= 0 else -1) if value >= 0]
        end = min(end_candidates) if end_candidates else min(len(clean), match.end() + 240)
        window = clean[start:end].strip(" •,;:-")

        if not self._has_action_signal(window) and not self._is_credential_excerpt(window):
            # Expand to the preceding bullet when the term is on a wrapped PDF
            # line whose action verb appears immediately before it.
            earlier_bullet = clean.rfind("•", 0, max(0, start - 1))
            if earlier_bullet >= 0:
                window = clean[earlier_bullet:end].strip(" •,;:-")

        # On multi-column CVs, training titles may be concatenated with job
        # headings. Isolate the smallest credential phrase containing the term.
        precise_credential = re.search(
            rf"(?:[A-Z][A-Za-z0-9&+./'-]*\s+)?{re.escape(needle)}(?:\s+[A-Z][A-Za-z0-9&+./'-]*){{0,4}}\s+(?:Certificate|Certification|Course|Programme|Program|Degree)",
            window,
            re.I,
        )
        if precise_credential:
            return self._clean_evidence_excerpt(precise_credential.group(0))
        credential_matches = list(re.finditer(
            r"(?:[A-Z][A-Za-z0-9&+./'-]*\s+){0,7}[A-Z][A-Za-z0-9&+./'-]*(?:\s+[A-Z][A-Za-z0-9&+./'-]*){0,7}\s+(?:Certificate|Certification|Course|Programme|Program|Degree)",
            window,
        ))
        for credential in credential_matches:
            candidate = credential.group(0).strip()
            if self._contains_term(self._plain(candidate), needle):
                return self._clean_evidence_excerpt(candidate)
        return self._clean_evidence_excerpt(window)

    def _family_markers(self, family: str) -> tuple[str, ...]:
        for candidate_family, _category, markers in self.extractor._FAMILY_RULES:
            if candidate_family == family:
                return tuple(markers)
        for _name, _category, candidate_family, _kind, patterns in self.extractor._CAPABILITY_RULES:
            if candidate_family == family:
                return tuple(patterns)
        return ()

    def _transfer_fit_score(self, requirement: TechnicalRequirement, excerpt: str) -> int:
        plain = self._plain(excerpt)
        score = 0
        if requirement.requirement_kind == "technical_platform":
            if re.search(r"\b(?:implement|implemented|deploy|deployed|configure|configured|migrate|migrated|upgrade|upgraded|integrate|integrated|administer|administered)\b", plain):
                score += 4
            if re.search(r"\b(?:platform|system|software|module|modules|hris|erp|crm)\b", plain):
                score += 2
            if re.search(r"\b(?:report|dashboard|analytics)\b", plain) and not re.search(r"\b(?:implement|deploy|configure|migrate|upgrade|integrate)\b", plain):
                score -= 2
        elif requirement.requirement_kind == "technical_innovation":
            if re.search(r"\b(?:data science|machine learning|predictive|python|nlp|automation)\b", plain):
                score += 5
            elif re.search(r"\b(?:analytics|dashboard|business intelligence)\b", plain):
                score += 1
            if self._is_credential_excerpt(excerpt):
                score += 2
        elif requirement.requirement_kind == "technical_tool":
            if re.search(r"\b(?:built|created|designed|configured|implemented|launched|administered|developed)\b", plain):
                score += 3
        elif requirement.requirement_kind in {"functional_capability", "general_capability"}:
            if any(self._contains_term(plain, marker) for marker in self._family_markers(requirement.family)):
                score += 3
        return score

    def _is_grounded_professional_excerpt(self, excerpt: str, *, anchor: str = "") -> bool:
        if not excerpt or self._is_contact_or_identity_line(excerpt):
            return False
        words = self._plain(excerpt).split()
        if len(words) < 4:
            return False
        if anchor and not self._contains_term(self._plain(excerpt), anchor):
            return False
        return self._has_action_signal(excerpt) or self._is_credential_excerpt(excerpt) or self._has_metric(excerpt)

    def _grounding_score(self, excerpt: str) -> int:
        score = 0
        if self._has_action_signal(excerpt):
            score += 3
        if self._is_credential_excerpt(excerpt):
            score += 2
        if self._has_metric(excerpt):
            score += 2
        if len(self._plain(excerpt).split()) >= 8:
            score += 1
        return score

    def _has_action_signal(self, value: str) -> bool:
        plain = self._plain(value)
        for marker in self.extractor._ACTION_MARKERS:
            normalized = self._plain(marker)
            if normalized and re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?:ed|ing|s)?(?![a-z0-9])", plain):
                return True
        # Additional CV verbs that are not requirement-extraction cues.
        return bool(re.search(
            r"\b(?:responsible|oversaw|supervised|administered|configured|integrated|migrated|analysed|analyzed|supported|coordinated|facilitated|contributed|participated|certified|trained)\b",
            plain,
        ))

    def _is_credential_excerpt(self, value: str) -> bool:
        plain = self._plain(value)
        return bool(re.search(
            r"\b(?:certification|certificate|certified|course|training|degree|diploma|programme|program)\b",
            plain,
        ))

    def _is_contact_or_identity_line(self, value: str) -> bool:
        clean = " ".join(str(value or "").split())
        plain = self._plain(clean)
        if not clean:
            return True
        if re.search(r"(?:https?://|www\.|linkedin\.|@|gmail\.|outlook\.|yahoo\.)", clean, re.I):
            return True
        if re.search(r"(?:\+?\d[\d .()/-]{6,}\d)", clean):
            return True
        if re.search(r"\b(?:street|road|avenue|boulevard|lane|rue|postal|postcode|zip code)\b", plain):
            return True
        if len(plain.split()) <= 5 and not self._has_action_signal(clean) and not self._is_credential_excerpt(clean):
            # Isolated names, locations, employers, headings and job titles are
            # context, not evidence of competence.
            if clean.isupper() or clean.istitle() or re.search(
                r"\b(?:manager|director|consultant|specialist|officer|lead|engineer|analyst|professional|location|summary|experience|skills|strengths)\b",
                plain,
            ):
                return True
        return False

    def _clean_evidence_excerpt(self, value: str) -> str:
        clean = " ".join(str(value or "").strip(" \t•*-–—").split())
        # PDF extraction sometimes prefixes a location or heading to the first
        # bullet. Keep the professional statement starting at the first action.
        action_pattern = re.compile(
            r"\b(?:implemented|launched|created|built|designed|developed|configured|deployed|migrated|integrated|managed|led|delivered|supervised|administered|supported|coordinated|facilitated|contributed|participated|processed|provided|enhanced|hired|acted)\b",
            re.I,
        )
        match = action_pattern.search(clean)
        if match and len(clean[: match.start()].split()) <= 7:
            clean = clean[match.start():]
        return clean[:420]

    def _is_concrete_related_term(self, value: str) -> bool:
        plain = self._plain(value)
        if not plain or len(plain) < 3:
            return False
        generic = {
            "hris platforms", "business intelligence", "data and databases",
            "project and delivery methods", "software engineering", "cloud and devops",
            "finance systems", "marketing technology", "technical tools and platforms",
        }
        if plain in generic:
            return False
        return len(plain.split()) <= 5

    def _contains_term(self, plain_text: str, term: object) -> bool:
        needle = self._plain(term)
        if not needle:
            return False
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", plain_text))

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
        needle = self._plain(term)
        candidates: list[tuple[int, str]] = []
        for line in self.extractor._lines(text):
            if needle and needle in self._plain(line):
                clean = self._clean_evidence_excerpt(line)
                if self._is_contact_or_identity_line(clean):
                    continue
                candidates.append((self._grounding_score(clean), clean))
        if candidates:
            return sorted(candidates, key=lambda item: (-item[0], -len(item[1])))[0][1][:420]
        clean = " ".join(str(text or "").split())
        normalized = self._plain(clean)
        index = normalized.find(needle)
        if index < 0:
            return ""
        excerpt = clean[max(0, index - 80): index + len(term) + 180].strip()
        excerpt = self._clean_evidence_excerpt(excerpt)
        return "" if self._is_contact_or_identity_line(excerpt) else excerpt[:420]

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
