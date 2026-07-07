from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_reports_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Reports",
        "Prepare explainable recruitment reports for recruiters and stakeholders.",
        "Reporting",
    )

    metric_row([
        ("Executive Summary", "Ready"),
        ("Evidence", "Included"),
        ("Risks", "Explained"),
        ("Export", "Prepared"),
    ])

    st.subheader("Report sections")
    capability_grid([
        ("Candidate decision card", "Summarize recommendation, score and confidence."),
        ("Evidence report", "Show why the AI reached its conclusion."),
        ("Risk and uncertainty", "Make limitations explicit."),
        ("Interview guide", "Convert analysis into recruiter-ready questions."),
    ])

    context_panel()
