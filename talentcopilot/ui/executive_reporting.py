from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.executive_reporting_service import ExecutiveReportingService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _shortlist_table(report):
    import streamlit as st

    rows = [
        {
            "Rank": candidate.rank,
            "Candidate": candidate.candidate_name,
            "Match": candidate.match_score,
            "Recommendation": candidate.recommendation,
            "Decision Readiness": candidate.decision_readiness,
        }
        for candidate in report.shortlist
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No shortlist available.")


def _risks(report):
    import streamlit as st

    if not report.risks:
        st.success("No risk available.")
        return

    for risk in report.risks:
        if risk.severity.lower() == "low":
            st.info(f"**{risk.title}** — {risk.detail}")
        elif risk.severity.lower() == "high":
            st.error(f"**{risk.title}** — {risk.detail}")
        else:
            st.warning(f"**{risk.title}** — {risk.detail}")


def render_executive_reporting():
    import streamlit as st

    apply_enterprise_theme()

    service = ExecutiveReportingService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Executive Reporting",
        "Prepare stakeholder-ready summaries and exportable recruitment reports.",
        "Reporting",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = service.build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {report.role_title}")

    metric_grid([
        ("Role", report.role_title, "Report scope"),
        ("Shortlist", str(len(report.shortlist)), "Candidates"),
        ("Risks", str(len(report.risks)), "Identified"),
        ("Session", report.session_id[:8] if report.session_id else "-", "Active"),
    ])

    insight_card("Executive Summary", report.executive_summary, "Executive Brief")

    tab_shortlist, tab_risks, tab_recommendations, tab_export = st.tabs([
        "Shortlist",
        "Risks",
        "Recommendations",
        "Export",
    ])

    with tab_shortlist:
        section_title("Shortlist")
        _shortlist_table(report)

    with tab_risks:
        section_title("Risk Summary")
        _risks(report)

    with tab_recommendations:
        section_title("Recommendations")
        for item in report.recommendations:
            st.write(f"- {item}")

        section_title("Next Steps")
        for item in report.next_steps:
            st.write(f"- {item}")

    with tab_export:
        section_title("Markdown Export")
        markdown_report = service.to_markdown(report)
        st.download_button(
            "Download Executive Report",
            data=markdown_report,
            file_name="talentcopilot_executive_report.md",
            mime="text/markdown",
        )
        st.markdown(markdown_report)
