from talentcopilot.services.blueprint_overview_service import BlueprintOverviewService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_blueprint_overview():
    import streamlit as st

    apply_enterprise_theme()

    overview = BlueprintOverviewService().build()

    enterprise_hero(
        "Blueprint Overview",
        overview.positioning,
        overview.title,
    )

    metric_grid([
        ("Blueprint", "v1.0", "Foundation"),
        ("Principles", str(len(overview.principles)), "Accepted"),
        ("Architecture Layers", str(len(overview.layers)), "Target"),
        ("Next Chapters", str(len(overview.next_chapters)), "Planned"),
    ])

    insight_card(
        "Architecture shift",
        "TalentCopilot will now evolve from UI-first development to Blueprint-driven Decision Intelligence architecture.",
        "Product Architecture",
    )

    tab_principles, tab_layers, tab_next = st.tabs([
        "Principles",
        "Architecture Layers",
        "Next Chapters",
    ])

    with tab_principles:
        section_title("Founding principles")
        for principle in overview.principles:
            with st.expander(principle.name):
                st.write(principle.detail)

    with tab_layers:
        section_title("Target architecture")
        for layer in overview.layers:
            st.info(f"**{layer.name}** — {layer.purpose}")

    with tab_next:
        section_title("Upcoming blueprint chapters")
        for chapter in overview.next_chapters:
            st.write(f"- {chapter}")
