from talentcopilot.services.release_summary_service import ReleaseSummaryService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_release_summary():
    import streamlit as st

    apply_enterprise_theme()

    summary = ReleaseSummaryService().build()

    enterprise_hero(
        "Release Summary",
        summary.summary,
        summary.release_name,
    )

    delivered = len([item for item in summary.workspaces if item.status == "Delivered"])

    metric_grid([
        ("Release", "1.0", summary.version),
        ("Workspaces", str(len(summary.workspaces)), "Tracked"),
        ("Delivered", str(delivered), "Ready"),
        ("Next", "Release 1.1", "Recruitment depth"),
    ])

    insight_card(
        "Release 1.0 outcome",
        "TalentCopilot now has a coherent Enterprise shell, stable tests, demo flow and workspace-based navigation.",
        "Product Milestone",
    )

    section_title("Workspace Readiness")
    rows = [
        {"Workspace": item.name, "Status": item.status, "Value": item.value}
        for item in summary.workspaces
    ]
    st.dataframe(rows, use_container_width=True)

    section_title("Next Release Focus")
    for item in summary.next_release_focus:
        st.write(f"- {item}")
