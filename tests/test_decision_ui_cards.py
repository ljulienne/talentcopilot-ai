from talentcopilot.ui.decision_cards import (
    render_decision_intelligence_card,
    render_decision_summary_badge,
)
from talentcopilot.models.decision import (
    DecisionReport,
    HiringRecommendation,
    DecisionConfidence,
    HumanValidationLevel,
)


def test_decision_ui_helpers_are_importable_and_safe_without_streamlit():
    report = DecisionReport(
        candidate_name="Alice",
        role_title="Role",
        recommendation=HiringRecommendation.HIRE,
        decision_score=75,
        confidence=DecisionConfidence.MEDIUM,
        human_validation=HumanValidationLevel.RECOMMENDED,
        executive_summary="Continue process.",
    )

    render_decision_intelligence_card(report)
    render_decision_summary_badge(report)
