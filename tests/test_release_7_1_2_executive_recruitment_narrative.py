from types import SimpleNamespace

from talentcopilot.recruitment.mission.narrative import (
    candidate_assessment,
    executive_summary,
    recruiter_reasoning,
)


def _candidate(name, rank, score, rationale, recommendation, strengths=(), focuses=()):
    return SimpleNamespace(
        name=name,
        rank=rank,
        match_score=score,
        rationale=rationale,
        recommendation=recommendation,
        strengths=tuple(strengths),
        risks=(),
        validation_focus=tuple(focuses),
    )


def test_executive_summary_is_decision_oriented_and_compares_candidates():
    lead = _candidate(
        "Louis Julienne", 1, 84,
        "Evidence found for HRIS leadership. No evidence found for SAP configuration.",
        "Strong Hire",
        strengths=("Led an HR technology transformation",),
    )
    alternative = _candidate(
        "Vincent Blakoe", 2, 80,
        "Strong HR operations experience. No evidence found for Power BI.",
        "Interview",
    )
    text = executive_summary("HRIS Manager", (lead, alternative))
    assert "currently leads" in text
    assert "closest alternative" in text
    assert "decision uncertainty" in text
    assert "Evidence found for" not in text


def test_candidate_assessment_distinguishes_uncertainty_from_confirmed_gap():
    candidate = _candidate(
        "Loretta Danielson", 4, 56,
        "The resume does not provide sufficient evidence to confirm HRIS ownership. No evidence found for SAP.",
        "Review",
        strengths=("Ten years of HR experience",),
    )
    text = candidate_assessment(candidate)
    assert "plausible but incomplete match" in text
    assert "decision uncertainties" in text
    assert "confirmed capability gap" not in text
    assert "HRIS ownership" in text


def test_recruiter_reasoning_uses_paragraphs_not_bullet_dump():
    candidate = _candidate(
        "Vincent Blakoe", 2, 80,
        "The candidate demonstrates relevant HR operations experience. No evidence found for enterprise HRIS ownership.",
        "Interview",
        focuses=("Establish whether enterprise HRIS ownership is genuine",),
    )
    paragraphs = recruiter_reasoning(candidate)
    assert len(paragraphs) >= 2
    assert all(not paragraph.lstrip().startswith("-") for paragraph in paragraphs)
    assert any("practical implication" in paragraph for paragraph in paragraphs)


def test_candidate_narratives_are_personalized():
    first = _candidate("A", 1, 84, "No evidence found for SAP.", "Strong Hire")
    second = _candidate("B", 2, 70, "No evidence found for Power BI.", "Interview")
    assert candidate_assessment(first) != candidate_assessment(second)
