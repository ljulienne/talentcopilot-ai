from talentcopilot.ui.talent_locator_cards import (
    render_talent_locator_empty_state,
    render_talent_locator_results,
)
from talentcopilot.models.talent_locator import TalentLocatorReport


def test_talent_locator_ui_helpers_are_importable_and_safe_without_streamlit():
    report = TalentLocatorReport(
        role_title="Role",
        total_candidates=0,
        results=[],
        summary="No candidates.",
    )

    render_talent_locator_results(report)
    render_talent_locator_empty_state()
