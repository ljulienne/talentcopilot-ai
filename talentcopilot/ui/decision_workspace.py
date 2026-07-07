from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_decision_workspace(*args, **kwargs):
    import streamlit as st

    hero(
        "Decision Workspace",
        "Central workspace for explainable, human-in-the-loop hiring decisions.",
        "Decision Workspace",
    )

    metric_row([
        ("Match", "Integrated"),
        ("Governance", "Enabled"),
        ("Decision Engine", "Ready"),
        ("Copilot", "Connected"),
    ])

    st.subheader("Decision workflow")
    capability_grid([
        ("AI Decision Card", "Consolidate recommendation, confidence and risk."),
        ("Governance review", "Inspect uncertainty, evidence quality and validation needs."),
        ("Recruiter action", "Move from analysis to next-step guidance."),
        ("Auditability", "Keep decisions explainable and reviewable."),
    ])

    context_panel()
