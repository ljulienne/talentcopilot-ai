from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.services.talent_intelligence_service import TalentIntelligenceService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _shortlist(report):
    import streamlit as st

    rows = [
        {
            "Rank": item.rank,
            "Candidate": item.candidate_name,
            "Match": item.match_score,
            "Top Skills": ", ".join(item.top_skills),
            "Sourcing Note": item.sourcing_note,
        }
        for item in report.shortlist
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No internal shortlist available.")


def _skills(report):
    import streamlit as st

    if not report.skill_signals:
        st.info("No skill signals available.")
        return

    for signal in report.skill_signals:
        st.write(f"**{signal.name}**")
        st.progress(max(0, min(100, signal.coverage)) / 100)
        st.caption(f"Evidence count: {signal.evidence_count}")


def render_talent_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    service = TalentIntelligenceService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Talent Intelligence",
        "Understand internal talent coverage and prepare sourcing actions.",
        "Analysis",
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
        ("Role", report.role_title, "Talent scope"),
        ("Shortlist", str(len(report.shortlist)), "Internal candidates"),
        ("Skill Signals", str(len(report.skill_signals)), "Detected"),
        ("Search Readiness", f"{report.search_readiness}%", "Sourcing confidence"),
    ])

    insight_card(
        "Talent Search Readiness",
        f"The current internal talent pool has a search readiness of {report.search_readiness}%. Use skill signals to decide whether external sourcing is needed.",
        "Talent Intelligence",
    )

    tab_shortlist, tab_skills, tab_recommendations = st.tabs([
        "Internal Shortlist",
        "Skill Signals",
        "Recommendations",
    ])

    with tab_shortlist:
        section_title("Internal Shortlist")
        _shortlist(report)

    with tab_skills:
        section_title("Skill Signals")
        _skills(report)

    with tab_recommendations:
        section_title("Talent Recommendations")
        for recommendation in report.recommendations:
            st.write(f"- **{recommendation.priority}** · {recommendation.title}: {recommendation.detail}")
