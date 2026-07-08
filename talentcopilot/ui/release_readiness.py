from talentcopilot.services.release_readiness_service import ReleaseReadinessService
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_release_readiness():
    import streamlit as st

    apply_enterprise_theme()

    report = ReleaseReadinessService().build()

    enterprise_hero(
        "Release Readiness",
        "Validate navigation, imports and core shell health before demo or deployment.",
        "Administration",
    )

    metric_grid([
        ("Readiness Score", f"{report.score}%", report.status),
        ("Checks", str(len(report.checks)), "Automated"),
        ("Status", report.status, "Release shell"),
        ("Next Step", "Reboot" if report.score == 100 else "Fix checks", "Streamlit"),
    ])

    section_title("Health Checks")
    for check in report.checks:
        if check.status == "OK":
            st.success(f"{check.name} — {check.detail}")
        else:
            st.error(f"{check.name} — {check.detail}")

    section_title("Recommendations")
    for recommendation in report.recommendations:
        st.write(f"- {recommendation}")
