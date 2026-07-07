from talentcopilot.ui.enterprise_components import capability_grid, context_panel, hero, metric_row, safe_render


@safe_render
def render_talent_pool_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Talent Pool",
        "Organize and explore internal candidates before launching deeper analysis.",
        "Talent Intelligence",
    )

    metric_row([
        ("Search", "Ready"),
        ("Pipeline", "Structured"),
        ("Shortlist", "Supported"),
        ("Locator", "Enabled"),
    ])

    st.subheader("Talent pool capabilities")
    capability_grid([
        ("Internal search", "Find candidates already available in the pool."),
        ("Shortlisting", "Prepare a focused list for role analysis."),
        ("Talent Locator", "Rank profiles against role requirements."),
        ("Future connectors", "Architecture ready for authorized external integrations."),
    ])

    context_panel()
