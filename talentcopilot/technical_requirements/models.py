from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class TechnicalRequirement:
    requirement_id: str
    name: str
    category: str
    family: str
    requirement_kind: str
    importance: str
    required_level: float
    source_excerpt: str = ""
    aliases: tuple[str, ...] = field(default_factory=tuple)
    related_terms: tuple[str, ...] = field(default_factory=tuple)
    components: tuple[str, ...] = field(default_factory=tuple)
    context_terms: tuple[str, ...] = field(default_factory=tuple)
    interview_priority: str = "Validate"
    extraction_method: str = "deterministic"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class CandidateRequirementEvidence:
    requirement_id: str
    requirement_name: str
    evidence_status: str
    estimated_level: float
    confidence: str
    evidence: str
    related_evidence: tuple[str, ...] = field(default_factory=tuple)
    matched_components: tuple[str, ...] = field(default_factory=tuple)
    missing_components: tuple[str, ...] = field(default_factory=tuple)
    interview_priority: str = "Validate"


@dataclass(frozen=True)
class TechnicalRequirementCatalog:
    role_title: str
    requirements: tuple[TechnicalRequirement, ...]
    eligibility_checks: tuple[str, ...] = field(default_factory=tuple)
    extraction_method: str = "deterministic"

    def to_dicts(self) -> list[dict]:
        return [item.to_dict() for item in self.requirements]
