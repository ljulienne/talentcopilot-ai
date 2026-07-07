from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, workflow_steps, safe_render


@safe_render
def render_home_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "TalentCopilot-AI",
        "An explainable AI recruitment intelligence platform for evidence-based hiring decisions.",
        "Home",
    )

    metric_row([
        ("Platform", "v0.6"),
        ("AI Layer", "Explainable"),
        ("Decision", "Human-in-loop"),
        ("Workflow", "Ready"),
    ])

    st.subheader("What TalentCopilot does")
    capability_grid([
        ("Analyze candidates", "Assess profiles against role requirements with structured signals."),
        ("Explain evidence", "Highlight why a candidate appears aligned or risky."),
        ("Support decisions", "Combine match, confidence, risk and uncertainty."),
        ("Guide recruiters", "Prepare next actions and interview focus points."),
    ])

    st.subheader("Recommended workflow")
    workflow_steps([
        "Create or open a recruitment context.",
        "Review candidates and talent pool profiles.",
        "Use Decision Workspace to inspect evidence and risks.",
        "Use Recruiter Copilot to prepare next steps.",
    ])

    context_panel()
