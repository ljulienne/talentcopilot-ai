from talentcopilot.ui.recruiter_copilot_cards import (
    render_recruiter_copilot_card,
    render_recruiter_copilot_summary,
)
from talentcopilot.models.recruiter_copilot import RecruiterCopilotReport


def test_recruiter_copilot_ui_helpers_are_importable_and_safe_without_streamlit():
    report = RecruiterCopilotReport(
        candidate_name="Alice",
        role_title="Role",
        headline="Hire — Decision score 75/100",
        recruiter_summary="Summary",
    )

    render_recruiter_copilot_card(report)
    render_recruiter_copilot_summary(report)
