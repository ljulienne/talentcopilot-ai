from talentcopilot.services.product_overview_service import ProductOverviewService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_product_overview():
    import streamlit as st

    apply_enterprise_theme()

    overview = ProductOverviewService().build()

    enterprise_hero(
        "Product Overview",
        overview.value_proposition,
        overview.tagline,
    )

    metric_grid([
        ("Product", "TalentCopilot", "Enterprise"),
        ("Workspaces", str(len(overview.workspaces)), "Business views"),
        ("Personas", str(len(overview.personas)), "Supported"),
        ("Principles", str(len(overview.principles)), "AI governance"),
    ])

    insight_card(
        "Positioning",
        "TalentCopilot is not only a CV matching tool. It is a decision intelligence layer for recruitment.",
        "Product Strategy",
    )

    tab_principles, tab_workspaces, tab_personas, tab_demo = st.tabs([
        "Principles",
        "Workspaces",
        "Personas",
        "Demo Flow",
    ])

    with tab_principles:
        section_title("Product Principles")
        for principle in overview.principles:
            st.write(f"- {principle}")

    with tab_workspaces:
        section_title("Workspace Map")
        for workspace in overview.workspaces:
            with st.expander(workspace.name):
                st.write(f"**Question:** {workspace.question}")
                st.write(f"**Value:** {workspace.value}")

    with tab_personas:
        section_title("Personas")
        rows = [
            {"Persona": persona.name, "Need": persona.need, "Primary Workspace": persona.workspace}
            for persona in overview.personas
        ]
        st.dataframe(rows, use_container_width=True)

    with tab_demo:
        section_title("Demo Flow")
        for index, step in enumerate(overview.demo_flow, start=1):
            st.write(f"{index}. {step}")
