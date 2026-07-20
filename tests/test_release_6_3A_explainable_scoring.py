from types import SimpleNamespace

from talentcopilot.explainable_scoring import ExplainableScoringService


def _report(score=76.0):
    return SimpleNamespace(
        candidate_id="candidate-1",
        candidate_name="Example Candidate",
        match_score=score,
        score_breakdown={
            "confidence": 92,
            "mission_fit_industry": 100,
            "mission_fit_function": 75,
            "mission_fit_leadership": 60,
            "mission_fit_experience": 80,
            "mission_fit_business_scope": 70,
            "mission_fit_tools": 50,
            "mission_fit_geography": 100,
            "mission_fit_education_languages": 75,
        },
    )


def test_explanation_preserves_official_mission_fit():
    result = ExplainableScoringService().build(_report(76.0))
    assert result.mission_fit == 76.0
    assert result.reconstructed_score == 76.0


def test_explanation_has_weighted_dimensions_and_evidence():
    result = ExplainableScoringService().build(_report())
    assert len(result.dimensions) == 8
    assert all(item.weight > 0 for item in result.dimensions)
    assert all(item.evidence for item in result.dimensions)
    assert result.positive_contributions
    assert result.penalties


def test_fallback_never_invents_a_second_score():
    report = SimpleNamespace(
        candidate_id="candidate-2",
        candidate_name="Fallback Candidate",
        match_score=63.0,
        score_breakdown={"confidence": 80},
    )
    result = ExplainableScoringService().build(report)
    assert result.mission_fit == 63.0
    assert result.reconstructed_score == 63.0
    assert len(result.dimensions) == 1
