"""Deterministic, consultant-grade recruitment narratives.

This presentation layer never recalculates scores, ranks or recommendations.
It translates official evidence into concise, fluent, decision-oriented prose.
"""

from __future__ import annotations

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
    "hris", "sap", "successfactors", "implementation", "deployment",
)

_ELIGIBILITY_MARKERS = (
    "years of experience", "years evidenced", "minimum ",
    "required level of seniority", "education requirement", "language requirement",
)



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
        r"principal decision uncertainties concern\s+(.+)",
        r"main decision uncertainties concern\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.I)
        if match:
            return _clean_fragment(match.group(1))
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
        "data", "process", "vendor", "budget",
    )):
        return (3, -len(value))
    return (1, -len(value))



def _positive_strengths(strengths: Sequence[str], rationale: str) -> tuple[str, ...]:
    values: list[str] = []
    for item in strengths or ():
        cleaned = _clean_fragment(item)
        if not cleaned or _is_eligibility(cleaned):
            continue
        if _polarity(cleaned) != "positive":
            continue
        if cleaned.casefold() not in {entry.casefold() for entry in values}:
            values.append(cleaned)

    if not values:
        for sentence in _sentences(rationale):
            cleaned = _clean_fragment(sentence)
            if not cleaned or _is_eligibility(cleaned):
                continue
            if _polarity(cleaned) != "positive":
                continue
            if cleaned.casefold() not in {entry.casefold() for entry in values}:
                values.append(cleaned)

    return tuple(sorted(values, key=_strength_priority, reverse=True))



def _strength_phrase(strengths: Sequence[str], rationale: str) -> str:
    return _human_join(_positive_strengths(strengths, rationale)[:2])



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
            f"The case is supported by {strengths}, rather than tenure alone."
        )
    else:
        text = (
            f"{lead.name} currently leads the {role_title} shortlist, "
            "although the available evidence does not yet reveal a single clearly differentiated achievement."
        )

    if topics:
        text += (
            f" The principal decision uncertainty is the depth of direct experience in {_human_join(topics)}. "
            "This should be clarified through concrete examples of personal ownership and measurable impact."
        )
    else:
        text += (
            " The interview should now confirm the candidate's personal ownership, delivery scope and measurable impact "
            "behind the most relevant claims."
        )

    if alternative:
        text += (
            f" {alternative.name} remains the closest alternative, so the final decision should rest on the quality "
            "and specificity of the interview evidence rather than on ranking alone."
        )
    return text



def candidate_assessment(candidate: object) -> str:
    score = float(getattr(candidate, "match_score", 0.0) or 0.0)
    name = str(getattr(candidate, "name", "The candidate"))
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))

    paragraph = f"{name} presents {_fit_language(score)} for the role, reflected in an official match of {score:.0f}%."
    if strengths:
        paragraph += f" The most compelling evidence is {strengths}; these elements are more decision-relevant than simply meeting the minimum experience threshold."
    else:
        paragraph += (
            " The profile is viable, but the available documentation does not yet provide a clearly differentiated "
            "project, implementation or measurable achievement to anchor the case."
        )
    if topics:
        paragraph += (
            f" The main decision uncertainties concern {_human_join(topics)}. The evidence is not yet sufficient to determine "
            "whether this represents a genuine capability gap or simply an under-documented area of experience."
        )
    return paragraph



def _distinct_positive_context(candidate: object, excluded: str) -> str:
    selected: list[str] = []
    excluded_lower = excluded.casefold()
    for sentence in _sentences(getattr(candidate, "rationale", "")):
        cleaned = _clean_fragment(sentence)
        lowered = cleaned.casefold()
        if not cleaned or lowered in excluded_lower:
            continue
        if _polarity(cleaned) != "positive" or _is_eligibility(cleaned):
            continue
        selected.append(cleaned.rstrip(".") + ".")
    return " ".join(selected[:1])



def recruiter_reasoning(candidate: object) -> tuple[str, ...]:
    assessment = candidate_assessment(candidate)
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))
    context = _distinct_positive_context(candidate, assessment)
    paragraphs = [assessment]

    if context:
        paragraphs.append("This evidence is particularly relevant because " + context[0].lower() + context[1:])

    focuses = tuple(getattr(candidate, "validation_focus", ()) or ())
    if focuses:
        first = _clean_fragment(focuses[0])
        implication = (
            "The practical implication is clear: the interview should " + first[0].lower() + first[1:] + ("" if first.endswith(".") else ".")
        )
    elif topics:
        implication = (
            f"The practical implication is to test {_human_join(topics)} through one concrete example, establishing the candidate's "
            "personal decisions, delivery scope, stakeholders and measurable outcome."
        )
    else:
        implication = (
            "The practical implication is to validate one highly comparable assignment in depth, including the candidate's personal "
            "decisions, operating scope, stakeholders and measurable outcome."
        )
    paragraphs.append(implication)
    return tuple(paragraphs)



def leading_candidate_insight(candidate: object) -> str:
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))
    if strengths and topics:
        return (
            f"The leading profile is differentiated by {strengths}. The principal point to validate is {_human_join(topics)}."
        )
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
        return (
            f"{alternative.name} remains the strongest alternative, but {_human_join(topics)} requires stronger evidence before a final decision."
        )
    return f"{alternative.name} remains the strongest alternative and should be compared on depth of ownership and demonstrated impact."
