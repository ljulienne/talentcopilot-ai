"""Recruitment portfolio intelligence and active-mission analytics UI."""

from __future__ import annotations

from html import escape

from talentcopilot.services.analytics_dashboard_service import AnalyticsDashboardService
from talentcopilot.services.recruitment_portfolio_intelligence import (
    RecruitmentPortfolioIntelligenceService,
)
from talentcopilot.services.recruitment_project_portfolio import build_project_summaries
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.storage.recruitment_store import list_recruitments
from talentcopilot.ui.design_system.components import enterprise_hero, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-portfolio-note{padding:.9rem 1rem;border:1px solid #dce5f0;border-radius:15px;background:linear-gradient(135deg,#f9fbff,#f4f8fc);color:#52637a;font-size:.82rem;line-height:1.5;margin:.55rem 0 1rem}
        .tc-alert-card{padding:1rem 1.05rem;border:1px solid #dce5f0;border-radius:17px;background:#fff;box-shadow:0 7px 20px rgba(24,45,78,.05);margin:.55rem 0}
        .tc-alert-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:.45rem}
        .tc-alert-title{color:#14213d;font-size:.93rem;font-weight:850}.tc-alert-meta{color:#728198;font-size:.7rem;margin-top:.12rem}
        .tc-alert-copy{color:#53647c;font-size:.8rem;line-height:1.48}.tc-alert-action{margin-top:.52rem;color:#294fb9;font-size:.76rem;font-weight:750}
        .tc-alert-badge{display:inline-block;padding:.22rem .54rem;border-radius:999px;font-size:.67rem;font-weight:850}
        .tc-severity-critical{background:#fee2e2;color:#991b1b}.tc-severity-high{background:#ffedd5;color:#9a3412}.tc-severity-medium{background:#fef3c7;color:#92400e}.tc-severity-info{background:#dbeafe;color:#1d4ed8}
        .tc-owner-card{padding:.85rem .95rem;border:1px solid #dce5f0;border-radius:15px;background:#fcfdff;min-height:120px}
        .tc-owner-name{color:#14213d;font-size:.9rem;font-weight:850}.tc-owner-line{color:#62738a;font-size:.76rem;margin-top:.3rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _active_mission_signals(report) -> None:
    import streamlit as st

    for signal in report.signals:
        with st.expander(f"{signal.area} · {signal.status} · {signal.score}%"):
            st.progress(max(0, min(100, signal.score)) / 100)
            st.write(signal.detail)


def _active_mission_funnel(report) -> None:
    import streamlit as st

    rows = [
        {
            "Stage": stage.name,
            "Count": stage.count,
            "Conversion": f"{stage.conversion}%",
        }
        for stage in report.funnel
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_portfolio_overview(report) -> None:
    import streamlit as st

    left, right = st.columns([1.2, .8])
    with left:
        section_title("Lifecycle distribution")
        lifecycle_rows = [
            {
                "Stage": item.label,
                "Projects": item.project_count,
                "Candidates": item.candidate_count,
            }
            for item in report.lifecycle_metrics
        ]
        st.dataframe(lifecycle_rows, use_container_width=True, hide_index=True)

    with right:
        section_title("Last activity")
        freshness_rows = [
            {
                "Activity band": item.label,
                "Projects": item.project_count,
            }
            for item in report.freshness_metrics
        ]
        st.dataframe(freshness_rows, use_container_width=True, hide_index=True)

    section_title("Portfolio guidance")
    for recommendation in report.recommendations:
        st.write(f"• {recommendation}")

    st.markdown(
        f'<div class="tc-portfolio-note">{escape(report.limitation)}</div>',
        unsafe_allow_html=True,
    )


def _render_attention_queue(report) -> None:
    import streamlit as st

    if not report.alerts:
        st.success("No project currently requires operational attention based on saved workflow state.")
        return

    st.caption(
        "One primary operational alert is shown per project to avoid duplicate or competing recommendations."
    )
    for alert in report.alerts:
        age_text = (
            f"{alert.activity_age_days} days since last activity"
            if alert.activity_age_days is not None
            else "Last activity unavailable"
        )
        severity_class = alert.severity.casefold()
        st.markdown(
            f"""
            <div class="tc-alert-card">
              <div class="tc-alert-top">
                <div>
                  <div class="tc-alert-title">{escape(alert.project_title)}</div>
                  <div class="tc-alert-meta">{escape(alert.category)} · {escape(alert.priority)} priority · {escape(alert.owner)} · {escape(age_text)}</div>
                </div>
                <span class="tc-alert-badge tc-severity-{escape(severity_class)}">{escape(alert.severity)}</span>
              </div>
              <div class="tc-alert-copy">{escape(alert.summary)}</div>
              <div class="tc-alert-action">Next action · {escape(alert.recommended_action)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Open Projects", type="primary", key="portfolio_intelligence_open_projects"):
        request_page("Projects", reason="Opened from the recruitment portfolio attention queue.")
        st.rerun()


def _render_owner_load(report) -> None:
    import streamlit as st

    if not report.owner_load:
        st.info("Save recruitment projects and assign owners to activate workload visibility.")
        return

    columns = st.columns(3)
    for index, owner in enumerate(report.owner_load):
        with columns[index % 3]:
            st.markdown(
                f"""
                <div class="tc-owner-card">
                  <div class="tc-owner-name">{escape(owner.owner)}</div>
                  <div class="tc-owner-line">{owner.project_count} open project(s)</div>
                  <div class="tc-owner-line">{owner.critical_or_high_count} high or critical</div>
                  <div class="tc-owner-line">{owner.decision_ready_count} decision ready · {owner.attention_count} requiring attention</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.caption(
        "Workload is descriptive only. TalentCopilot does not infer recruiter capacity from project counts."
    )


def _render_active_mission(session) -> None:
    import streamlit as st

    report = AnalyticsDashboardService().build(session)
    if session is None or not getattr(session, "ranked_analyses", None):
        st.info(
            "No analyzed recruitment is active. Reopen a saved project to review mission-level analytics."
        )
        if st.button("Open Projects", key="analytics_active_open_projects"):
            request_page("Projects", reason="Choose a project for active-mission analytics.")
            st.rerun()
        return

    st.caption(f"Active recruitment: {report.role_title}")
    metric_grid([(item.label, item.value, item.delta) for item in report.kpis])

    left, right = st.columns([1, 1])
    with left:
        section_title("Recruitment funnel")
        _active_mission_funnel(report)
    with right:
        section_title("Mission signals")
        _active_mission_signals(report)

    section_title("Mission recommendations")
    for item in report.recommendations:
        st.write(f"• {item}")


def render_analytics_dashboard() -> None:
    import streamlit as st

    apply_enterprise_theme()
    _styles()

    active_session = get_streamlit_session()
    try:
        stored_recruitments = list_recruitments()
    except Exception:
        stored_recruitments = []

    projects = build_project_summaries(active_session, stored_recruitments)
    report = RecruitmentPortfolioIntelligenceService().build(projects)

    enterprise_hero(
        "Recruitment Portfolio Intelligence",
        "See lifecycle distribution, operational attention and accountable next actions across saved recruitments.",
        "Portfolio Analytics",
    )

    metric_grid(
        [
            ("Open projects", str(report.active_project_count), "Archived excluded"),
            ("Candidates", str(report.candidate_count), "Across open projects"),
            ("Decision ready", str(report.decision_ready_count), "Awaiting a final decision"),
            ("Attention required", str(report.attention_project_count), "One primary alert per project"),
        ]
    )

    if not projects:
        st.info(
            "No saved recruitment project is available yet. Save a project to activate cross-project intelligence."
        )
        if st.button("Open Projects", type="primary", key="portfolio_analytics_empty_projects"):
            request_page("Projects", reason="Save a project to enable portfolio analytics.")
            st.rerun()
        return

    overview_tab, alerts_tab, workload_tab, mission_tab = st.tabs(
        ["Portfolio health", "Attention queue", "Owner workload", "Active mission"]
    )

    with overview_tab:
        _render_portfolio_overview(report)

    with alerts_tab:
        _render_attention_queue(report)

    with workload_tab:
        _render_owner_load(report)

    with mission_tab:
        _render_active_mission(active_session)
