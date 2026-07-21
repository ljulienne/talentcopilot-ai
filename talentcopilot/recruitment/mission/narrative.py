"""Deterministic, consultant-grade recruitment narratives.

This presentation layer does not recalculate scores, ranks or recommendations.
It translates existing official evidence into concise decision-oriented prose.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence


_ROBOTIC_PREFIXES = (
    "evidence found for ",
    "no evidence found for ",
    "the resume does not provide sufficient evidence to confirm ",
)


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    if not normalized:
        return []
    # Remove an old candidate/employer prefix while retaining the substantive text.
    normalized = re.sub(r"^[^:]{2,80}:\s*(?=\d{1,3}%\b)", "", normalized)
    return [item.strip(" -") for item in re.split(r"(?<=[.!?])\s+|\s*;\s*", normalized) if item.strip(" -")]


def _clean_fragment(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip(" .;:-")
    text = re.sub(r"^(tool|function|skill|requirement)\s+", "", text, flags=re.IGNORECASE)
    return text


def _topic_from_sentence(sentence: str) -> str:
    patterns = (
        r"no evidence found for\s+(.+)",
        r"does not provide sufficient evidence to confirm(?: the role-critical requirement for| the requirement for)?\s+(.+)",
        r"insufficient(?:ly)? evidenced(?: for| in)?\s+(.+)",
        r"partially evidenced through transferable experience(?: in)?\s*(.+)",
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


def _strength_phrase(strengths: Sequence[str], rationale: str) -> str:
    items = [_clean_fragment(item) for item in strengths if _clean_fragment(item)]
    if items:
        return _human_join(items[:2])

    positive = []
    for sentence in _sentences(rationale):
        lowered = sentence.casefold()
        if not any(prefix in lowered for prefix in _ROBOTIC_PREFIXES) and not any(
            word in lowered for word in ("insufficient", "uncertain", "missing", "gap")
        ):
            positive.append(_clean_fragment(sentence))
    return _human_join(positive[:1])


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

    opening = (
        f"{lead.name} currently leads the {role_title} shortlist with an official match of "
        f"{lead.match_score:.0f}%."
    )
    support = (
        f" The position is supported by evidence of {strengths}."
        if strengths
        else " The current lead reflects the strongest overall alignment in the available evidence."
    )
    uncertainty = (
        f" The principal decision uncertainty concerns {_human_join(topics)}, which should be tested through targeted evidence rather than treated as a confirmed capability gap."
        if topics
        else " The remaining decision should focus on validating the depth of ownership, operating scope and measurable outcomes behind the strongest claims."
    )
    comparison = ""
    if alternative:
        gap = max(0.0, float(lead.match_score) - float(alternative.match_score))
        comparison = (
            f" {alternative.name} is the closest alternative at {alternative.match_score:.0f}%, "
            f"a {gap:.0f}-point gap, so the final choice should be based on the quality of evidence gathered in interview rather than score alone."
        )
    return opening + support + uncertainty + comparison


def candidate_assessment(candidate: object) -> str:
    score = float(getattr(candidate, "match_score", 0.0) or 0.0)
    name = str(getattr(candidate, "name", "The candidate"))
    recommendation = str(getattr(candidate, "recommendation", "Review required") or "Review required")
    strengths = _strength_phrase(getattr(candidate, "strengths", ()), getattr(candidate, "rationale", ""))
    topics = evidence_topics(getattr(candidate, "rationale", ""), getattr(candidate, "risks", ()))

    if score >= 80:
        fit = "a strong and credible match"
    elif score >= 65:
        fit = "a credible match with material points to validate"
    elif score >= 50:
        fit = "a plausible but incomplete match"
    else:
        fit = "a limited match on the evidence currently available"

    paragraph = f"{name} presents {fit}, reflected in an official match of {score:.0f}% and a recommendation of {recommendation}."
    if strengths:
        paragraph += f" The strongest support for the profile comes from {strengths}."
    if topics:
        paragraph += (
            f" Confidence is constrained by limited evidence concerning {_human_join(topics)}. "
            "These points should be treated as decision uncertainties until the candidate provides concrete examples of personal ownership and impact."
        )
    else:
        paragraph += (
            " The interview should now test the depth of the evidence already identified, with particular attention to personal ownership, decision scope and measurable outcomes."
        )
    return paragraph


def recruiter_reasoning(candidate: object) -> tuple[str, ...]:
    assessment = candidate_assessment(candidate)
    rationale_sentences = _sentences(getattr(candidate, "rationale", ""))
    substantive = []
    for sentence in rationale_sentences:
        cleaned = _clean_fragment(sentence)
        if cleaned and cleaned.casefold() not in assessment.casefold() and len(cleaned) > 20:
            substantive.append(cleaned + ("" if cleaned.endswith((".", "!", "?")) else "."))

    evidence = ""
    if substantive:
        evidence = (
            "The underlying evidence indicates that "
            + " ".join(substantive[:2])[0].lower()
            + " ".join(substantive[:2])[1:]
        )

    focuses = tuple(getattr(candidate, "validation_focus", ()) or ())
    implication = ""
    if focuses:
        first = _clean_fragment(focuses[0])
        implication = (
            "The practical implication is to use the interview to "
            + first[0].lower()
            + first[1:]
            + ("" if first.endswith(".") else ".")
        )

    return tuple(item for item in (assessment, evidence, implication) if item)


def leading_candidate_insight(candidate: object) -> str:
    return candidate_assessment(candidate)


def alternative_insight(lead: object, alternative: object) -> str:
    gap = max(0.0, float(getattr(lead, "match_score", 0.0)) - float(getattr(alternative, "match_score", 0.0)))
    topics = evidence_topics(getattr(alternative, "rationale", ""), getattr(alternative, "risks", ()))
    text = (
        f"{alternative.name} is the strongest alternative at {alternative.match_score:.0f}%, "
        f"{gap:.0f} points behind {lead.name}."
    )
    if topics:
        text += f" The comparison turns primarily on whether the candidate can substantiate {_human_join(topics)}."
    else:
        text += " The comparison should focus on depth of ownership and demonstrated impact in the most role-critical areas."
    return text
