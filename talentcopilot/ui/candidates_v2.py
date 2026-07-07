from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_candidates_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Candidates",
        "Review candidate profiles through evidence-first intelligence.",
        "Candidate Workspace",
    )

    metric_row([
        ("Profiles", "Ready"),
        ("Skills", "Mapped"),
        ("Evidence", "Reviewed"),
        ("Risks", "Flagged"),
    ])

    st.subheader("Candidate analysis zones")
    capability_grid([
        ("Profile summary", "Understand the candidate background and experience."),
        ("Competency reasoning", "Review strengths, gaps and evidence by competency."),
        ("Confidence & uncertainty", "Assess how reliable the AI interpretation is."),
        ("Interview focus", "Prepare targeted validation questions."),
    ])

    context_panel()
