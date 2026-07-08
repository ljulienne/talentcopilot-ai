from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_skill_bars(report):
    import streamlit as st

    if not report.skills:
        st.info("No skills available.")
        return

    for skill in report.skills:
        st.write(f"**{skill.name}**")
        st.progress(max(0, min(100, skill.level)) / 100)
        if skill.evidence:
            st.caption(skill.evidence)


def _render_evidence(report):
    import streamlit as st

    if not report.evidence:
        st.info("No evidence available.")
        return

    for item in report.evidence:
        with st.expander(f"{item.title} · {item.strength}"):
            st.write(item.detail)


def _render_risks(report):
    import streamlit as st

    if not report.risks:
        st.success("No major risk detected in the current candidate report.")
        return

    for risk in report.risks:
        st.warning(f"**{risk.title}** — {risk.detail}")


def render_candidate_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    reports = CandidateWorkspaceService().build_all(session)

    enterprise_hero(
        "Candidate Workspace",
        "Review one candidate at a time with evidence, AI recommendation and interview focus.",
        "Analysis",
    )

    if not reports:
        st.info("No active candidate analysis. Load the Enterprise Demo to populate this workspace.")
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            reports = CandidateWorkspaceService().build_all(session)
            st.success("Enterprise demo loaded.")

    if not reports:
        return

    candidate_names = [report.candidate_name for report in reports]
    selected_name = st.selectbox("Select candidate", candidate_names)
    report = reports[candidate_names.index(selected_name)]

    metric_grid([
        ("Candidate", report.candidate_name, f"Rank #{report.rank}"),
        ("Match Score", f"{report.match_score:.0f}%", "AI matching"),
        ("Recommendation", report.recommendation, "Decision signal"),
        ("Workspace", "Candidate", "360° view"),
    ])

    insight_card(
        "Executive Summary",
        report.executive_summary,
        "AI Summary",
    )

    tab_overview, tab_skills, tab_evidence, tab_risks, tab_interview = st.tabs([
        "Overview",
        "Skills",
        "Evidence",
        "Risks",
        "Interview Focus",
    ])

    with tab_overview:
        section_title("Candidate Overview")
        st.write(f"**Recommendation:** {report.recommendation}")
        st.write(f"**Match score:** {report.match_score:.0f}%")

    with tab_skills:
        section_title("Skills")
        _render_skill_bars(report)

    with tab_evidence:
        section_title("Evidence")
        _render_evidence(report)

    with tab_risks:
        section_title("Risks")
        _render_risks(report)

    with tab_interview:
        section_title("Interview Focus")
        if report.interview_focus:
            for item in report.interview_focus:
                st.write(f"- {item}")
        else:
            st.info("No interview focus generated yet.")
