"""Deterministic, consultant-grade recruitment narratives.

This presentation layer never recalculates scores, ranks or recommendations.
It translates the official evidence into concise, fluent and decision-oriented
prose while keeping eligibility evidence separate from true differentiators.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence


_ROBOTIC_PREFIXES = (
    "evidence found for ",
    "no evidence found for ",
    "the resume does not provide sufficient evidence to confirm ",
)

_ELIGIBILITY_MARKERS = (
    "years of experience",
    "years evidenced",
    "minimum ",
    "required level of seniority",
    "education requirement",
    "language requirement",
)

_PROFESSIONAL_TERMS = {
    "sap": "SAP",
    "sap successfactors": "SAP SuccessFactors",
    "power bi": "Power BI",
    "hris": "HRIS",
    "api": "API",
    "uat": "UAT",
    "core hr": "Core HR",
}


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
    text = re.sub(r"^(tool|function|skill|requirement)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(direct evidence of|direct evidence:|transferable evidence:)\s*", "", text, flags=re.I)
    for raw, replacement in _PROFESSIONAL_TERMS.items():
        text = re.sub(rf"\b{re.escape(raw)}\b", replacement, text, flags=re.I)
    return text


def _topic_from_sentence(sentence: str) -> str:
    patterns = (
        r"no evidence found for\s+(.+)",
        r"does not provide sufficient evidence to confirm(?: the role-critical requirement for| the requirement for)?\s+(.+)",
        r"insufficient(?:ly)? evidenced(?: for| in)?\s+(.+)",
        r"partially evidenced through transferable experience(?: in)?\s*(.+)",
        r"principal decision uncertainties concern\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.IGNORECASE)
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


def _human_join(values: Sequence[str]) -> str:
    cleaned = [_clean_fragment(value) for value in values if _clean_fragment(value)]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])}, and {cleaned[-1]}"


def _is_eligibility_strength(value: str) -> bool:
    lowered = _clean_fragment(value).casefold()
    return any(marker in lowered for marker in _ELIGIBILITY_MARKERS)


def _rank_strengths(strengths: Sequence[str]) -> tuple[str, ...]:
    """Prioritise capability and achievement evidence over eligibility checks."""
    cleaned: list[str] = []
    for item in strengths or ():
        value = _clean_fragment(item)
        if value and value.casefold() not in {entry.casefold() for entry in cleaned}:
            cleaned.append(value)

    def priority(value: str) -> tuple[int, int]:
        lowered = value.casefold()
        if _is_eligibility_strength(value):
            return (0, len(value))
        if any(token in lowered for token in (
            "led", "delivered", "implemented", "deployed", "transformation",
            "migration", "integration", "governance", "project", "programme",
            "measurable", "improved", "reduced", "increased", "adoption",
        )):
            return (4, len(value))
        if any(token in lowered for token in (
            "ownership", "managed", "leadership", "stakeholder", "international",
            "multi-country", "operating scope",
        )):
            return (3, len(value))
        if any(token in lowered for token in (
            "SAP", "successfactors", "power bi", "HRIS", "analytics", "testing",
            "data", "process", "vendor", "budget",
        )):
            return (2, len(value))
        return (1, len(value))

    return tuple(sorted(cleaned, key=priority, reverse=True))


def _strength_phrase(strengths: Sequence[str], rationale: str) -> str:
    ranked = _rank_strengths(strengths)
    differentiators = [item for item in ranked if not _is_eligibility_strength(item)]
    if differentiators:
        return _human_join(differentiators[:2])

    positive: list[str] = []
    for sentence in _sentences(rationale):
        lowered = sentence.casefold()
        if any(prefix in lowered for prefix in _ROBOTIC_PREFIXES):
            continue
        if any(word in lowered for word in ("insufficient", "uncertain", "missing", "gap")):
            continue
        if re.search(r"\bofficial (mission fit|match)\b|\bevidence confidence\b", lowered):
            continue
        cleaned = _clean_fragment(sentence)
        if cleaned and not _is_eligibility_strength(cleaned):
            positive.append(cleaned)
    return _human_join(positive[:1])


def _fit_language(score: float) -> str:
    if score >= 80:
        return "a strong and credible match"
    if score >= 65:
        return "a credible match with material points to validate"
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

    text = (
        f"{lead.name} currently leads the {role_title} shortlist with an official match of "
        f"{lead.match_score:.0f}%."
    )
    if strengths:
        text += f" The lead position is primarily supported by {strengths}, rather than tenure alone."
    else:
        text += " The lead position reflects the strongest overall alignment in the evidence currently available."

    if topics:
        text += (
            f" The principal decision uncertainty concerns {_human_join(topics)}. This should be tested through "
            "specific examples of ownership and impact rather than treated as a confirmed capability gap."
        )
    else:
        text += (
            " The remaining decision should focus on the depth of personal ownership, operating scope "
            "and measurable outcomes behind the strongest claims."
        )

    if alternative:
        gap = max(0.0, float(lead.match_score) - float(alternative.match_score))
        text += (
            f" {alternative.name} is the closest alternative at {alternative.match_score:.0f}%, "
            f"a {gap:.0f}-point gap. The final choice should therefore be based on the quality of evidence "
            "gathered in interview, not on the score alone."
        )
    return text


def candidate_assessment(candidate: object) -> str:
    score = float(getattr(candidate, "match_score", 0.0) or 0.0)
    name = str(getattr(candidate, "name", "The candidate"))
    recommendation = str(getattr(candidate, "recommendation", "Review required") or "Review required")
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))

    paragraph = (
        f"{name} presents {_fit_language(score)} for the role. The official match is {score:.0f}%, "
        f"supporting a current recommendation of {recommendation}."
    )
    if strengths:
        paragraph += (
            f" The profile is most persuasive where it demonstrates {strengths}; these elements are more "
            "decision-relevant than simply meeting the minimum experience threshold."
        )
    if topics:
        paragraph += (
            f" The main decision uncertainties concern {_human_join(topics)}. The available documentation does not yet "
            "show whether this reflects a genuine capability gap or experience that is simply under-documented."
        )
    else:
        paragraph += (
            " The interview should now test the depth of the strongest evidence, especially the candidate's "
            "personal decisions, operating scope and measurable contribution."
        )
    return paragraph


def _substantive_evidence(candidate: object) -> str:
    assessment = candidate_assessment(candidate).casefold()
    candidates: list[str] = []
    for sentence in _sentences(getattr(candidate, "rationale", "")):
        cleaned = _clean_fragment(sentence)
        lowered = cleaned.casefold()
        if not cleaned or len(cleaned) <= 30:
            continue
        if lowered in assessment:
            continue
        if re.search(r"\bofficial (mission fit|match)\b|\bevidence confidence\b", lowered):
            continue
        if lowered.startswith(("recommendation:", "the current recommendation")):
            continue
        if any(prefix in lowered for prefix in _ROBOTIC_PREFIXES):
            continue
        candidates.append(cleaned.rstrip(".") + ".")
    return " ".join(candidates[:2])


def recruiter_reasoning(candidate: object) -> tuple[str, ...]:
    assessment = candidate_assessment(candidate)
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))
    evidence = _substantive_evidence(candidate)

    paragraphs = [assessment]

    if evidence:
        paragraphs.append(
            "The evidence base adds useful context: " + evidence[0].lower() + evidence[1:]
        )
    elif strengths:
        paragraphs.append(
            f"From a recruiter's perspective, the strongest case rests on {strengths}. "
            "This is the evidence that should carry the most weight in comparing the candidate with the rest of the shortlist."
        )

    focuses = tuple(getattr(candidate, "validation_focus", ()) or ())
    if focuses:
        first = _clean_fragment(focuses[0])
        implication = (
            "The practical implication is to use the interview to "
            + first[0].lower()
            + first[1:]
            + ("" if first.endswith(".") else ".")
        )
    elif topics:
        implication = (
            f"The practical implication is to test {_human_join(topics)} through one concrete example. "
            "The interviewer should establish the candidate's personal decisions, delivery scope, stakeholders and measurable outcome."
        )
    else:
        implication = (
            "The practical implication is to validate the strongest claims through one detailed example, "
            "including the candidate's personal decisions, operating scope, stakeholders and measurable outcome."
        )
    paragraphs.append(implication)

    return tuple(paragraphs)


def leading_candidate_insight(candidate: object) -> str:
    return candidate_assessment(candidate)


def alternative_insight(lead: object, alternative: object) -> str:
    gap = max(
        0.0,
        float(getattr(lead, "match_score", 0.0)) - float(getattr(alternative, "match_score", 0.0)),
    )
    topics = evidence_topics(getattr(alternative, "rationale", ""), getattr(alternative, "risks", ()))
    text = (
        f"{alternative.name} is the strongest alternative at {alternative.match_score:.0f}%, "
        f"{gap:.0f} points behind {lead.name}."
    )
    if topics:
        text += (
            f" The comparison turns primarily on whether the candidate can substantiate {_human_join(topics)} "
            "with direct ownership and measurable impact."
        )
    else:
        text += (
            " The comparison should focus on depth of ownership and demonstrated impact in the most role-critical areas."
        )
    return text
