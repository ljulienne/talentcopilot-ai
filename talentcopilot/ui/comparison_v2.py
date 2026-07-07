from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_comparison_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Comparison",
        "Compare candidates using decision-ready signals rather than only raw scores.",
        "Candidate Comparison",
    )

    metric_row([
        ("Candidates", "Comparable"),
        ("Fit", "Weighted"),
        ("Evidence", "Contrasted"),
        ("Decision", "Supported"),
    ])

    st.subheader("Comparison dimensions")
    capability_grid([
        ("Role fit", "Compare alignment with core requirements."),
        ("Evidence depth", "Compare quality and quantity of supporting evidence."),
        ("Risk profile", "Identify which candidate needs more validation."),
        ("Interview priority", "Prepare differentiated interview focus points."),
    ])

    context_panel()
