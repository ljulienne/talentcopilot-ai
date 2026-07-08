from talentcopilot.services.release_1_1_summary_service import Release11SummaryService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_release_1_1_summary():
    import streamlit as st

    apply_enterprise_theme()

    summary = Release11SummaryService().build()

    enterprise_hero(
        "Release 1.1 Summary",
        summary.product_message,
        summary.title,
    )

    delivered = len([m for m in summary.modules if m.status == "Delivered"])

    metric_grid([
        ("Release", "1.1", summary.version),
        ("Modules", str(len(summary.modules)), "Delivered scope"),
        ("Delivered", str(delivered), "Ready"),
        ("Next Phase", "Blueprint", "Architecture"),
    ])

    insight_card(
        "Release 1.1 outcome",
        "TalentCopilot now supports a complete Enterprise demo workflow. The next strategic step is the Blueprint and Decision Intelligence Core.",
        "Milestone",
    )

    tab_modules, tab_blueprint, tab_next = st.tabs([
        "Modules",
        "Blueprint Readiness",
        "Next Steps",
    ])

    with tab_modules:
        section_title("Delivered modules")
        rows = [
            {"Module": item.name, "Status": item.status, "Value": item.value}
            for item in summary.modules
        ]
        st.dataframe(rows, use_container_width=True)

    with tab_blueprint:
        section_title("Blueprint readiness")
        for item in summary.blueprint_readiness:
            if item.status == "Ready":
                st.success(f"{item.name} — {item.detail}")
            elif item.status == "Pending":
                st.warning(f"{item.name} — {item.detail}")
            else:
                st.info(f"{item.name} — {item.detail}")

    with tab_next:
        section_title("Recommended next steps")
        for step in summary.next_steps:
            st.write(f"- {step}")
