from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_dashboard_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Decision Center",
        "Monitor the main signals that support recruiter decisions.",
        "Decision Intelligence",
    )

    metric_row([
        ("Decision Score", "Ready"),
        ("Confidence", "Tracked"),
        ("Evidence Quality", "Visible"),
        ("Risk", "Controlled"),
    ])

    st.subheader("Decision signals")
    capability_grid([
        ("Match signal", "Role alignment based on skills and requirements."),
        ("Evidence quality", "Strength and specificity of supporting evidence."),
        ("Risk profile", "Detected gaps, weak evidence or validation needs."),
        ("Human validation", "Guidance on when recruiter review is required."),
    ])

    st.subheader("Current context")
    context_panel()
