"""Deterministic, consultant-grade recruitment narratives.

This module is deliberately presentation-only: it never recalculates official
scores, ranks, risks or recommendations.  Release 7.1.6 adds narrative compression and semantic variation so related
facts are merged before composition and each narrative block serves a distinct
decision purpose without recalculating business outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence


_PROFESSIONAL_TERMS = {
    "sap": "SAP",
    "sap successfactors": "SAP SuccessFactors",
    "power bi": "Power BI",
    "hris": "HRIS",
    "api": "API",
    "uat": "UAT",
    "core hr": "Core HR",
}

_METADATA_MARKERS = (
    "not a decisive criterion",
    "official mission fit",
    "official match",
    "evidence confidence",
    "recommendation:",
    "minimum experience threshold",
    "required level of seniority",
    "years evidenced",
    "years of experience",
)

_UNCERTAINTY_MARKERS = (
    "no evidence found",
    "limited evidence",
    "insufficient evidence",
    "insufficiently evidenced",
    "under-documented",
    "uncertain",
    "unclear",
    "unverified",
    "does not provide sufficient evidence",
    "principal decision uncertainty",
    "main decision uncertainty",
)

_NEGATIVE_MARKERS = (
    "confirmed gap",
    "below requirement",
    "does not meet",
    "contradictory evidence",
    "material weakness",
)

_POSITIVE_MARKERS = (
    "led ", "delivered ", "implemented ", "deployed ", "designed ",
    "managed ", "owned ", "transformation", "migration", "integration",
    "governance", "programme", "program", "project", "stakeholder",
    "leadership", "international", "multi-country", "measurable",
    "improved", "reduced", "increased", "adoption", "system",
    "process redesign", "data", "analytics", "vendor", "budget",
    "resource", "hris", "sap", "successfactors", "implementation",
    "deployment",
)

_ELIGIBILITY_MARKERS = (
    "years of experience", "years evidenced", "minimum ",
    "required level of seniority", "education requirement", "language requirement",
)

_LEADING_CONNECTORS = (
    "the most compelling evidence comes from",
    "the most compelling evidence is",
    "the case is supported by",
    "the profile is most persuasive where it demonstrates",
)


@dataclass(frozen=True)
class EvidenceAtom:
    """A single positive fact suitable for narrative composition."""

    capability: str
    source: str = ""
    evidence_level: str = "direct"
    priority: int = 1

    @property
    def phrase(self) -> str:
        """Return an atomic professional phrase, never a sentence template."""
        capability = _natural_capability(self.capability)
        source = _natural_source(self.source)
        if source and source.casefold() != capability.casefold():
            return _compress_atom_phrase(capability, source)
        return capability



_SEMANTIC_GROUPS = {
    "project_delivery": (
        "project management", "project manager", "programme", "program",
        "project delivery", "implementation", "deployment", "transformation",
    ),
    "resource_governance": (
        "budget", "resource", "vendor", "governance", "commercial",
    ),
    "systems": (
        "sap", "successfactors", "hris", "system", "integration", "migration",
    ),
    "process": ("process design", "process redesign", "operating model", "workflow"),
    "data": ("power bi", "analytics", "data", "reporting", "dashboard"),
    "leadership": (
        "stakeholder", "leadership", "international", "multi-country",
        "change management", "team",
    ),
}


def _semantic_group(value: str) -> str:
    lowered = _clean_fragment(value).casefold()
    # Specific technologies and process capabilities take precedence over generic
    # words such as implementation, project or programme.
    priority = ("systems", "process", "data", "resource_governance", "leadership", "project_delivery")
    for group in priority:
        if any(marker in lowered for marker in _SEMANTIC_GROUPS[group]):
            return group
    return "other"


def _compress_atom_phrase(capability: str, source: str) -> str:
    combined = f"{capability} {source}".casefold()
    group = _semantic_group(combined)
    if group == "project_delivery":
        return "project delivery"
    if group == "resource_governance":
        if "budget" in combined or "resource" in combined:
            return "responsibility for budgets and resources"
        return "operational governance"
    if group == "systems":
        terms = [term for term in ("SAP SuccessFactors", "SAP", "HRIS") if term.casefold() in combined]
        return f"hands-on experience with {_human_join(terms)}" if terms else capability
    if group == "process":
        return "end-to-end process design"
    if group == "data":
        return "data and analytics delivery"
    if group == "leadership":
        return "cross-functional leadership"
    return capability if capability else source


def _compressed_strength_phrases(strengths: Sequence[str], rationale: str) -> tuple[str, ...]:
    """Merge only redundant structured atoms while preserving specific achievements."""
    atoms = _evidence_atoms(strengths, rationale)
    phrases: list[str] = []
    structured_groups: dict[str, list[EvidenceAtom]] = {}

    for atom in atoms:
        # Complete achievements already carry useful specificity and should not
        # be reduced to a generic taxonomy label.
        if not atom.source:
            phrase = _clean_fragment(atom.capability)
            if phrase and phrase.casefold() not in {item.casefold() for item in phrases}:
                phrases.append(phrase)
            continue
        group = _semantic_group(f"{atom.capability} {atom.source}")
        structured_groups.setdefault(group, []).append(atom)

    # The common project + resources pair is expressed once, without repeating
    # the same evidence connector or paraphrasing both internal labels.
    if "project_delivery" in structured_groups and "resource_governance" in structured_groups:
        phrases.append("project management with budget and resource ownership")
        structured_groups.pop("project_delivery")
        structured_groups.pop("resource_governance")

    for group, group_atoms in structured_groups.items():
        atom = group_atoms[0]
        capability = _natural_capability(atom.capability)
        source = _natural_source(atom.source)
        if group == "project_delivery":
            phrase = "project management"
        elif group == "resource_governance":
            phrase = "budget and resource management"
        elif group == "systems":
            phrase = _human_join((source, capability))
        elif group == "process":
            phrase = _human_join((source, capability)) or "process design"
        elif group == "data":
            phrase = _human_join((source, capability))
        elif group == "leadership":
            phrase = _human_join((source, capability))
        else:
            phrase = _human_join((source, capability))
        if phrase and phrase.casefold() not in {item.casefold() for item in phrases}:
            phrases.append(phrase)

    return tuple(phrases)

def _candidate_possessive(name: str) -> str:
    return f"{name}'" if name.rstrip().endswith("s") else f"{name}'s"


def _sentence_word_overlap(first: str, second: str) -> float:
    stop = {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for",
        "with", "is", "are", "was", "were", "this", "that", "by", "from",
    }
    words_a = {w for w in re.findall(r"[a-z0-9]+", first.casefold()) if w not in stop and len(w) > 2}
    words_b = {w for w in re.findall(r"[a-z0-9]+", second.casefold()) if w not in stop and len(w) > 2}
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / min(len(words_a), len(words_b))


def narrative_quality_issues(text: str) -> tuple[str, ...]:
    """Return deterministic lexical-quality warnings for regression tests."""
    issues: list[str] = []
    lowered = str(text or "").casefold()
    for phrase in (
        "supported by evidence of",
        "the most compelling evidence is the",
        "the most compelling evidence comes from the",
        "the case is supported by the",
    ):
        if lowered.count(phrase) > 0:
            issues.append(f"forbidden connector: {phrase}")
    sentences = _sentences(text)
    for index, sentence in enumerate(sentences):
        words = re.findall(r"[a-z]+", sentence.casefold())
        for size in (3, 4):
            grams = [tuple(words[i:i+size]) for i in range(max(0, len(words)-size+1))]
            if len(grams) != len(set(grams)):
                issues.append(f"repeated {size}-gram in sentence {index + 1}")
                break
    for index in range(len(sentences) - 1):
        if _sentence_word_overlap(sentences[index], sentences[index + 1]) >= 0.65:
            issues.append(f"high lexical overlap between sentences {index + 1} and {index + 2}")
    return tuple(dict.fromkeys(issues))

def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    if not normalized:
        return []
    normalized = re.sub(r"^[^:]{2,80}:\s*(?=\d{1,3}%\b)", "", normalized)
    return [
        item.strip(" -")
        for item in re.split(r"(?<=[.!?])\s+|\s*;\s*", normalized)
        if item.strip(" -")
    ]


def _clean_fragment(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip(" .;:-")
    # Strip sentence-level connectors before the value is used as an atom.
    changed = True
    while changed:
        changed = False
        for connector in _LEADING_CONNECTORS:
            updated = re.sub(rf"^{re.escape(connector)}\s+", "", text, flags=re.I)
            if updated != text:
                text = updated.strip(" .;:-")
                changed = True
    text = re.sub(r"^(tool|function|skill|requirement)\s+", "", text, flags=re.I)
    text = re.sub(r"^(direct evidence of|direct evidence:|transferable evidence:)\s*", "", text, flags=re.I)
    for raw, replacement in _PROFESSIONAL_TERMS.items():
        text = re.sub(rf"\b{re.escape(raw)}\b", replacement, text, flags=re.I)
    return text


def _polarity(value: str) -> str:
    lowered = _clean_fragment(value).casefold()
    if not lowered:
        return "empty"
    if any(marker in lowered for marker in _METADATA_MARKERS):
        return "metadata"
    if any(marker in lowered for marker in _NEGATIVE_MARKERS):
        return "negative"
    if any(marker in lowered for marker in _UNCERTAINTY_MARKERS):
        return "uncertain"
    if any(marker in lowered for marker in _POSITIVE_MARKERS):
        return "positive"
    return "neutral"


def _is_eligibility(value: str) -> bool:
    lowered = _clean_fragment(value).casefold()
    return any(marker in lowered for marker in _ELIGIBILITY_MARKERS)


def _human_join(values: Sequence[str]) -> str:
    cleaned: list[str] = []
    for value in values:
        item = _clean_fragment(value)
        if item and item.casefold() not in {entry.casefold() for entry in cleaned}:
            cleaned.append(item)
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])}, and {cleaned[-1]}"


def _topic_from_sentence(sentence: str) -> str:
    patterns = (
        r"no evidence found for\s+(.+)",
        r"does not provide sufficient evidence to confirm(?: the role-critical requirement for| the requirement for)?\s+(.+)",
        r"insufficient(?:ly)? evidenced(?: for| in)?\s+(.+)",
        r"partially evidenced through transferable experience(?: in)?\s*(.+)",
        r"principal decision uncert(?:ainty|ainties) (?:concern|concerns|is|are)\s+(.+)",
        r"main decision uncert(?:ainty|ainties) (?:concern|concerns|is|are)\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.I)
        if match:
            topic = _clean_fragment(match.group(1))
            topic = re.sub(r"\bThis is an evidence uncertainty.*$", "", topic, flags=re.I).strip(" .")
            return topic
    return ""


def evidence_topics(rationale: str, risks: Iterable[str] = ()) -> tuple[str, ...]:
    topics: list[str] = []
    for sentence in _sentences(rationale):
        topic = _topic_from_sentence(sentence)
        if topic and topic.casefold() not in {item.casefold() for item in topics}:
            topics.append(topic)
    for risk in risks or ():
        topic = _clean_fragment(risk)
        if topic and topic.casefold() not in {item.casefold() for item in topics}:
            topics.append(topic)
    return tuple(topics[:3])


def _strength_priority(value: str) -> tuple[int, int]:
    lowered = _clean_fragment(value).casefold()
    if _is_eligibility(value):
        return (0, -len(value))
    if any(token in lowered for token in (
        "delivered", "implemented", "deployed", "transformation", "migration",
        "integration", "programme", "program", "project", "measurable",
        "improved", "reduced", "increased", "adoption",
    )):
        return (5, -len(value))
    if any(token in lowered for token in (
        "owned", "ownership", "designed", "managed", "governance",
        "stakeholder", "leadership", "international", "multi-country",
    )):
        return (4, -len(value))
    if any(token in lowered for token in (
        "sap", "successfactors", "power bi", "hris", "analytics", "testing",
        "data", "process", "vendor", "budget", "resource",
    )):
        return (3, -len(value))
    return (1, -len(value))


def _natural_capability(value: str) -> str:
    text = _clean_fragment(value)
    text = re.sub(r"\bsupports the candidate'?s capability in\b.*$", "", text, flags=re.I).strip(" .")
    text = re.sub(r"\bcapability in\s+", "", text, flags=re.I)
    # Capability labels read more naturally in lower case inside a sentence.
    if text and not re.match(r"^(SAP|HRIS|API|UAT|Power BI|Led|Delivered|Implemented|Deployed|Designed|Managed|Owned)\b", text):
        text = text[0].lower() + text[1:]
    return text


def _natural_source(value: str) -> str:
    text = _clean_fragment(value)
    replacements = {
        "project manager": "project-management responsibilities",
        "resources": "budget and resource responsibilities",
    }
    normalized = replacements.get(text.casefold(), text)
    if normalized and not re.match(r"^(SAP|HRIS|API|UAT|Power BI)\b", normalized):
        normalized = normalized[0].lower() + normalized[1:]
    return normalized


def _atom_from_strength(value: str) -> EvidenceAtom | None:
    raw = _clean_fragment(value)
    if not raw or _is_eligibility(raw) or _polarity(raw) != "positive":
        return None

    # Current engine format: "Direct evidence of X supports ... in Y".
    match = re.search(
        r"(?:direct|transferable) evidence of\s+(.+?)\s+supports the candidate'?s capability in\s+(.+)$",
        str(value or ""),
        flags=re.I,
    )
    if match:
        source = _clean_fragment(match.group(1))
        capability = _clean_fragment(match.group(2))
        level = "transferable" if str(value).casefold().startswith("transferable") else "direct"
        return EvidenceAtom(capability, source, level, _strength_priority(value)[0])

    # Future/clean engine format: "Y, supported by direct evidence of X".
    match = re.search(
        r"(.+?),?\s+supported by\s+(direct|transferable) evidence of\s+(.+)$",
        raw,
        flags=re.I,
    )
    if match:
        return EvidenceAtom(
            _clean_fragment(match.group(1)),
            _clean_fragment(match.group(3)),
            match.group(2).casefold(),
            _strength_priority(value)[0],
        )

    return EvidenceAtom(raw, "", "direct", _strength_priority(value)[0])


def _evidence_atoms(strengths: Sequence[str], rationale: str) -> tuple[EvidenceAtom, ...]:
    atoms: list[EvidenceAtom] = []
    for item in strengths or ():
        atom = _atom_from_strength(item)
        if atom and atom.phrase.casefold() not in {entry.phrase.casefold() for entry in atoms}:
            atoms.append(atom)

    if not atoms:
        for sentence in _sentences(rationale):
            atom = _atom_from_strength(sentence)
            if atom and atom.phrase.casefold() not in {entry.phrase.casefold() for entry in atoms}:
                atoms.append(atom)

    return tuple(sorted(atoms, key=lambda item: (item.priority, len(item.phrase) * -1), reverse=True))


def _strength_phrase(strengths: Sequence[str], rationale: str) -> str:
    return _human_join(_compressed_strength_phrases(strengths, rationale)[:2])


def _fit_language(score: float) -> str:
    if score >= 80:
        return "a strong overall match"
    if score >= 65:
        return "a credible match with important points to validate"
    if score >= 50:
        return "a plausible but incomplete match"
    return "a limited match on the evidence currently available"


def executive_summary(role_title: str, candidates: Sequence[object]) -> str:
    if not candidates:
        return (
            f"The {role_title} mission is ready for candidate evidence. Upload the job description "
            "and CVs to begin the official analysis."
        )

    lead = candidates[0]
    alternative = candidates[1] if len(candidates) > 1 else None
    strengths = _strength_phrase(getattr(lead, "strengths", ()), getattr(lead, "rationale", ""))
    topics = evidence_topics(getattr(lead, "rationale", ""), getattr(lead, "risks", ()))

    if strengths:
        text = (
            f"{lead.name} currently leads the {role_title} shortlist. "
            f"The profile is distinguished by {strengths}, rather than tenure alone."
        )
    else:
        text = (
            f"{lead.name} currently leads the {role_title} shortlist, although the available evidence "
            "does not yet reveal a clearly differentiated project or measurable achievement."
        )

    if topics:
        text += (
            f" The principal decision uncertainty concerns {_human_join(topics)}. "
            "A focused interview should test these areas through specific examples of personal ownership and measurable results."
        )
    else:
        text += (
            " A focused interview should confirm personal ownership, delivery scope and measurable results "
            "behind the most relevant claims."
        )

    if alternative:
        text += (
            f" {alternative.name} remains the closest alternative; the final choice should therefore depend on "
            "the specificity and credibility of the examples provided at interview, not the ranking alone."
        )
    return text


def _reasoning_strength_phrase(value: str) -> str:
    """Vary generic compressed wording in the reasoning block."""
    normalized = _clean_fragment(value)
    if normalized.casefold() == "project management with budget and resource ownership":
        return "project management accountability with budget and resource control"
    return normalized


def candidate_assessment(candidate: object) -> str:
    score = float(getattr(candidate, "match_score", 0.0) or 0.0)
    name = str(getattr(candidate, "name", "The candidate"))
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))

    paragraph = f"{name} presents {_fit_language(score)} for the role, reflected in an official match of {score:.0f}%."
    if strengths:
        reasoning_strengths = _reasoning_strength_phrase(strengths)
        paragraph += (
            f" The strongest support comes from {reasoning_strengths}; these elements are more decision-relevant than simply meeting "
            "the minimum experience threshold."
        )
    else:
        paragraph += (
            " The available documentation does not yet provide a clearly differentiated project, implementation or "
            "measurable achievement on which to anchor the case."
        )
    if topics:
        paragraph += (
            f" The remaining decision uncertainties are {_human_join(topics)}. They should be treated as questions "
            "for verification, not established gaps."
        )
    return paragraph


def recruiter_reasoning(candidate: object) -> tuple[str, ...]:
    assessment = candidate_assessment(candidate)
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))
    paragraphs = [assessment]

    focuses = tuple(getattr(candidate, "validation_focus", ()) or ())
    if topics:
        implication = (
            "The practical implication is to test these unresolved areas through one comparable assignment. "
            "Ask the candidate to separate personal decisions from team contribution, describe the systems and "
            "stakeholders involved, and quantify the result."
        )
    elif focuses:
        first = _clean_fragment(focuses[0])
        first = re.sub(r"^establish whether\s+", "clarify whether ", first, flags=re.I)
        implication = (
            f"The practical implication is to {first[0].lower() + first[1:]}. "
            "Probe personal decisions, delivery scope, trade-offs and measurable outcomes."
        )
    else:
        implication = (
            "The practical implication is to explore one highly comparable assignment in depth, covering personal "
            "decisions, operating scope, stakeholder complexity, trade-offs and measurable outcomes."
        )
    paragraphs.append(implication)
    return tuple(paragraphs)


def leading_candidate_insight(candidate: object) -> str:
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))
    if strengths and topics:
        return f"The leading profile is differentiated by {strengths}. The principal point to validate is {_human_join(topics)}."
    if strengths:
        return f"The leading profile is differentiated by {strengths}."
    if topics:
        return f"The lead position is credible, but {_human_join(topics)} remains the principal point to validate."
    return "The leading profile shows the strongest overall alignment, with interview evidence now required to confirm depth of ownership and impact."


def alternative_insight(lead: object, alternative: object) -> str:
    topics = evidence_topics(getattr(alternative, "rationale", ""), getattr(alternative, "risks", ()))
    strengths = _strength_phrase(getattr(alternative, "strengths", ()), getattr(alternative, "rationale", ""))
    if strengths and topics:
        return (
            f"{alternative.name} remains the strongest alternative, supported by {strengths}. The comparison will turn on "
            f"whether the candidate can substantiate {_human_join(topics)} with direct ownership and measurable impact."
        )
    if strengths:
        return f"{alternative.name} remains the strongest alternative, supported by {strengths}."
    if topics:
        return f"{alternative.name} remains the strongest alternative, but {_human_join(topics)} requires stronger evidence before a final decision."
    return f"{alternative.name} remains the strongest alternative and should be compared on depth of ownership and demonstrated impact."
