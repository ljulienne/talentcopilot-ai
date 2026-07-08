from talentcopilot.ui.enterprise_components import capability_grid, hero, metric_row, safe_render
from talentcopilot.ui.feature_restoration_components import page_purpose


@safe_render
def render_home_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "TalentCopilot-AI",
        "Explainable recruitment intelligence, from candidate analysis to decision support.",
        "Product Home",
    )

    page_purpose(
        "Home",
        "Understand what the product does and where to start.",
        [
            "Start a recruitment workflow.",
            "Understand the product architecture.",
            "Navigate to the right area depending on your task.",
        ],
    )

    metric_row([
        ("Version", "v0.7.6"),
        ("Architecture", "Enterprise"),
        ("AI", "Explainable"),
        ("Workflow", "Session-driven"),
    ])

    st.subheader("Navigation logic")
    capability_grid([
        ("Start", "Create or open a recruitment context."),
        ("Analyze", "Review candidates, talent pool and comparisons."),
        ("Decide", "Use decision intelligence and recruiter guidance."),
        ("Deliver", "Prepare reports and exports."),
    ])
