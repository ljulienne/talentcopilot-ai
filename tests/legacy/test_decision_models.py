from talentcopilot.models.decision import (
    DecisionReport,
    DecisionSignal,
    HiringRecommendation,
    DecisionConfidence,
    HumanValidationLevel,
)


def test_decision_signal_weighted_score():
    signal = DecisionSignal(
        name="Match",
        score=80,
        weight=0.25,
        explanation="Match signal",
    )

    assert signal.weighted_score == 20


def test_decision_report_positive_recommendation():
    report = DecisionReport(
        candidate_name="Alice",
        role_title="Transformation Lead",
        recommendation=HiringRecommendation.STRONG_HIRE,
        decision_score=90,
        confidence=DecisionConfidence.HIGH,
        human_validation=HumanValidationLevel.STANDARD_REVIEW,
        executive_summary="Strong candidate.",
    )

    assert report.is_positive_recommendation is True
    assert report.concern_count == 0
