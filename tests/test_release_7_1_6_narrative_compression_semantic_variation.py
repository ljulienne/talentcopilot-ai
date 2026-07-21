from types import SimpleNamespace

from talentcopilot.recruitment.mission.narrative import (
    candidate_assessment,
    executive_summary,
    narrative_quality_issues,
    recruiter_reasoning,
)


def _candidate(name="Louis Julienne", strengths=(), rationale="", risks=(), focuses=(), score=84):
    return SimpleNamespace(
        name=name,
        rank=1,
        match_score=score,
        recommendation="Strong Hire",
        strengths=tuple(strengths),
        rationale=rationale,
        risks=tuple(risks),
        validation_focus=tuple(focuses),
    )


def _louis():
    return _candidate(
        strengths=(
            "Direct evidence of project manager supports the candidate's capability in Project management",
            "Direct evidence of resources supports the candidate's capability in Budget / resource management",
        ),
        rationale=(
            "The principal decision uncertainty concerns SAP, SAP SuccessFactors, and Process Design."
        ),
    )


def test_related_capabilities_are_compressed_into_distinct_professional_phrases():
    text = executive_summary("HRIS Manager", (_louis(),))
    lowered = text.casefold()
    assert "project management with budget and resource ownership" in lowered
    assert "project-management responsibilities" not in lowered
    assert "budget and resource responsibilities" not in lowered
    assert "supported by evidence of" not in lowered


def test_executive_summary_avoids_repeating_decision_vocabulary():
    alternative = _candidate(name="Vincent Blakoe", score=80)
    text = executive_summary("HRIS Manager", (_louis(), alternative))
    lowered = text.casefold()
    assert lowered.count("evidence") == 0
    assert lowered.count("ranking") == 1
    assert lowered.count("interview") <= 2
    assert not narrative_quality_issues(text)


def test_recruiter_reasoning_has_a_distinct_role_and_varied_sentence_openings():
    paragraphs = recruiter_reasoning(_louis())
    joined = " ".join(paragraphs)
    assert len(paragraphs) == 2
    assert paragraphs[0].startswith("Louis Julienne presents")
    assert paragraphs[1].startswith("The practical implication")
    assert "currently appears to be the strongest candidate" not in joined
    assert "nearest alternative" not in joined
    assert "supported by evidence of" not in joined.casefold()
    assert "project management accountability" in joined
    assert joined.count("SAP") == 2
    assert not narrative_quality_issues(joined)


def test_uncertainties_are_not_presented_as_confirmed_gaps():
    text = candidate_assessment(_louis())
    assert "questions for verification, not established gaps" in text
    assert "genuine capability gap or simply under-documented" not in text


def test_quality_guard_detects_legacy_connector_and_repeated_ngram():
    flawed = (
        "The profile is supported by evidence of project delivery. "
        "Project delivery project delivery project delivery remains important."
    )
    issues = narrative_quality_issues(flawed)
    assert any("forbidden connector" in issue for issue in issues)
    assert any("repeated" in issue for issue in issues)
