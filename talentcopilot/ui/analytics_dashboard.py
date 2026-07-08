from talentcopilot.services.analytics_dashboard_service import AnalyticsDashboardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _signals(report):
    import streamlit as st

    for signal in report.signals:
        with st.expander(f"{signal.area} · {signal.status} · {signal.score}%"):
            st.progress(max(0, min(100, signal.score)) / 100)
            st.write(signal.detail)


def _funnel(report):
    import streamlit as st

    rows = [
        {
            "Stage": stage.name,
            "Count": stage.count,
            "Conversion": f"{stage.conversion}%",
        }
        for stage in report.funnel
    ]
    st.dataframe(rows, use_container_width=True)


def render_analytics_dashboard():
    import streamlit as st

    apply_enterprise_theme()

    service = AnalyticsDashboardService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Analytics Dashboard",
        "Track recruitment health, conversion, readiness and decision signals.",
        "Recruitment Analytics",
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

    metric_grid([(k.label, k.value, k.delta) for k in report.kpis[:4]])

    insight_card(
        "Global Recruitment Readiness",
        f"This recruitment has a global readiness score of {report.global_readiness}%. Review weak signals before final decision.",
        "Analytics",
    )

    tab_overview, tab_funnel, tab_signals, tab_recommendations = st.tabs([
        "Overview",
        "Funnel",
        "Signals",
        "Recommendations",
    ])

    with tab_overview:
        metric_grid([(k.label, k.value, k.delta) for k in report.kpis])
        st.progress(max(0, min(100, report.global_readiness)) / 100)

    with tab_funnel:
        section_title("Recruitment Funnel")
        _funnel(report)

    with tab_signals:
        section_title("Recruitment Signals")
        _signals(report)

    with tab_recommendations:
        section_title("Analytics Recommendations")
        for item in report.recommendations:
            st.write(f"- {item}")
