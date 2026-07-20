from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _ranking_table(report):
    import streamlit as st

    rows = [
        {
            "Interview Priority": c.interview_priority or c.rank,
            "Mission Rank": c.mission_rank or c.rank,
            "Candidate": c.candidate_name,
            "Mission Fit": c.match_score,
            "Career Fit": c.career_fit_score,
            "AI Confidence": (
                None
                if c.ai_confidence is None
                else c.ai_confidence
            ),
            "Recommendation": c.recommendation,
            "Key Strength": c.key_strength,
            "Key Risk": c.key_risk,
        }
        for c in report.candidates
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No candidates available for comparison.")


def _score_gaps(report):
    import streamlit as st

    if not report.score_gaps:
        st.info("No score gaps available yet.")
        return

    for gap in report.score_gaps:
        st.metric(gap.label, f"{gap.value:.1f} pts", gap.interpretation)


def _matrix(report):
    import streamlit as st

    rows = [
        {
            "Candidate": item.candidate_name,
            "Technical Fit": item.technical_fit,
            "Leadership Fit": item.leadership_fit,
            "Evidence Strength": item.evidence_strength,
            "Decision Readiness": item.decision_readiness,
        }
        for item in report.matrix
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No decision matrix available.")


def render_comparison_workspace():
    import streamlit as st

    apply_enterprise_theme()

    service = ComparisonWorkspaceService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Comparison Workspace",
        "Compare objective Mission Fit with career alignment and recommended interview priority.",
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

    top_candidate = report.candidates[0].candidate_name if report.candidates else "-"
    metric_grid([
        ("Role", report.role_title, "Comparison scope"),
        ("Candidates", str(len(report.candidates)), "Compared"),
        ("Top Candidate", top_candidate, "Current lead"),
        ("Matrix", str(len(report.matrix)), "Rows"),
    ])

    if report.differentiators:
        insight_card("Key Differentiator", report.differentiators[0], "Comparison Insight")

    tab_ranking, tab_gaps, tab_matrix, tab_diff = st.tabs([
        "Ranking",
        "Score Gaps",
        "Decision Matrix",
        "Differentiators",
    ])

    with tab_ranking:
        section_title(
            "Candidate Ranking",
            "Interview Priority may differ from Mission Rank when career evidence changes the recommended order.",
        )
        _ranking_table(report)

    with tab_gaps:
        section_title("Score Gaps")
        _score_gaps(report)

    with tab_matrix:
        section_title("Decision Matrix")
        _matrix(report)

    with tab_diff:
        section_title("Differentiators")
        for item in report.differentiators:
            st.write(f"- {item}")
