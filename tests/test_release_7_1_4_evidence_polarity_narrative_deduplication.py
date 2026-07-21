from types import SimpleNamespace

from talentcopilot.recruitment.mission.narrative import (
    candidate_assessment,
    executive_summary,
    leading_candidate_insight,
    recruiter_reasoning,
)


def _candidate(name="Louis Julienne", score=84, strengths=(), rationale="", focuses=()):
    return SimpleNamespace(
        name=name,
        rank=1,
        match_score=score,
        recommendation="Strong Hire",
        strengths=tuple(strengths),
        rationale=rationale,
        risks=(),
        validation_focus=tuple(focuses),
    )


def test_neutral_scoring_metadata_is_never_used_as_positive_evidence():
    candidate = _candidate(
        strengths=(
            "People leadership is not a decisive criterion",
            "Geographic scope is not a decisive criterion",
            "Led a multi-country HR transformation programme",
        ),
        rationale="The principal decision uncertainty concerns SAP.",
    )
    text = candidate_assessment(candidate)
    assert "multi-country HR transformation" in text
    assert "not a decisive criterion" not in text


def test_summary_is_fluent_and_does_not_repeat_scores_or_recommendations():
    lead = _candidate(
        strengths=("Led a multi-country HR transformation programme",),
        rationale="The principal decision uncertainty concerns SAP and Process Design.",
    )
    alternative = SimpleNamespace(
        name="Vincent Blakoe", rank=2, match_score=80, recommendation="Interview",
        strengths=("Implemented HR reporting improvements",), rationale="", risks=(), validation_focus=(),
    )
    text = executive_summary("HRIS Manager", (lead, alternative))
    assert "84%" not in text
    assert "Strong Hire" not in text
    assert "not a decisive criterion" not in text
    assert "multi-country HR transformation" in text
    assert "Vincent Blakoe" in text


def test_recruiter_reasoning_blocks_are_complementary_not_repetitive():
    candidate = _candidate(
        strengths=("Led a multi-country HR transformation programme",),
        rationale="The principal decision uncertainty concerns SAP and Process Design.",
        focuses=("Establish whether SAP experience included direct system ownership",),
    )
    paragraphs = recruiter_reasoning(candidate)
    joined = " ".join(paragraphs)
    assert len(paragraphs) == 2
    assert joined.count("SAP") <= 2
    assert joined.casefold().count("official match") <= 1
    assert "strong hire" not in joined.casefold()
    assert "The practical implication" in joined


def test_no_positive_evidence_fallback_is_honest_not_invented():
    candidate = _candidate(
        strengths=(
            "People leadership is not a decisive criterion",
            "17 years of experience",
        ),
        rationale="The principal decision uncertainty concerns SAP.",
    )
    text = candidate_assessment(candidate)
    assert "does not yet provide a clearly differentiated project" in text
    assert "not a decisive criterion" not in text
    assert "17 years" not in text


def test_key_insight_excludes_metadata_language():
    candidate = _candidate(
        strengths=(
            "Geographic scope is not a decisive criterion",
            "Delivered a global HR process redesign",
        ),
        rationale="The main decision uncertainty concerns SAP SuccessFactors.",
    )
    insight = leading_candidate_insight(candidate)
    assert "global HR process redesign" in insight
    assert "not a decisive criterion" not in insight
