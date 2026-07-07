from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_recruiter_copilot_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Recruiter Copilot",
        "Turn AI analysis into practical recruiter actions.",
        "Recruiter Guidance",
    )

    metric_row([
        ("Actions", "Suggested"),
        ("Alerts", "Prioritized"),
        ("Questions", "Prepared"),
        ("Summary", "Ready"),
    ])

    st.subheader("Copilot outputs")
    capability_grid([
        ("Next best action", "Move forward, validate, hold or reject with rationale."),
        ("Interview questions", "Ask targeted questions based on risks and gaps."),
        ("Recruiter alerts", "Surface high-priority validation points."),
        ("Stakeholder summary", "Prepare a clear hiring committee summary."),
    ])

    context_panel()
