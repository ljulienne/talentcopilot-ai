from types import SimpleNamespace

from talentcopilot.recruitment.mission.narrative import (
    candidate_assessment,
    executive_summary,
    recruiter_reasoning,
)


def _candidate(strengths=(), rationale="", focuses=()):
    return SimpleNamespace(
        name="Louis Julienne",
        rank=1,
        match_score=84,
        recommendation="Strong Hire",
        strengths=tuple(strengths),
        rationale=rationale,
        risks=(),
        validation_focus=tuple(focuses),
    )


def test_nested_narrative_connectors_are_removed_before_composition():
    candidate = _candidate(
        strengths=(
            "The most compelling evidence comes from Direct evidence of project manager supports the candidate's capability in Project management",
            "Direct evidence of resources supports the candidate's capability in Budget / resource management",
        ),
        rationale="The principal decision uncertainties concern SAP, SAP SuccessFactors, and Process Design.",
    )
    text = candidate_assessment(candidate)
    assert "The most compelling evidence comes from" not in text
    assert "supports the candidate's capability" not in text
    assert "project management" in text.casefold()
    assert "budget and resource" in text.casefold()
    assert "The strongest support comes from The" not in text


def test_executive_summary_is_grammatical_with_legacy_strength_fragments():
    lead = _candidate(
        strengths=(
            "The most compelling evidence comes from Direct evidence of project manager supports the candidate's capability in Project management",
            "Direct evidence of resources supports the candidate's capability in Budget / resource management",
        ),
        rationale="The principal decision uncertainty concerns SAP and Process Design.",
    )
    alternative = SimpleNamespace(
        name="Vincent Blakoe", rank=2, match_score=80, recommendation="Interview",
        strengths=(), rationale="", risks=(), validation_focus=(),
    )
    text = executive_summary("HRIS Manager", (lead, alternative))
    assert "The case is supported by The" not in text
    assert "The most compelling evidence" not in text
    assert "supports the candidate's capability" not in text
    assert "The profile is distinguished by" in text
    assert "Vincent Blakoe" in text


def test_recruiter_reasoning_uses_clean_topics_not_internal_tool_labels():
    candidate = _candidate(
        strengths=("Project management, supported by direct evidence of project manager.",),
        rationale="The principal decision uncertainties concern Tool SAP and Process Design.",
        focuses=("Establish whether Tool SAP is a genuine capability gap or simply under-documented",),
    )
    paragraphs = recruiter_reasoning(candidate)
    joined = " ".join(paragraphs)
    assert len(paragraphs) == 2
    assert "Tool SAP" not in joined
    assert "SAP" in joined
    assert joined.count("The practical implication") == 1
    assert "genuine capability gap or simply under-documented" not in joined


def test_narrative_does_not_repeat_connectors_or_complete_sentences():
    candidate = _candidate(
        strengths=("The case is supported by The most compelling evidence is Led a global HR transformation programme",),
        rationale="The main decision uncertainty concerns SAP SuccessFactors.",
    )
    joined = " ".join(recruiter_reasoning(candidate))
    forbidden = (
        "The case is supported by The",
        "The most compelling evidence is The",
        "The most compelling evidence comes from The",
    )
    assert all(value not in joined for value in forbidden)
    assert "global HR transformation programme" in joined
