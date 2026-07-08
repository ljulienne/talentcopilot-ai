from talentcopilot.services.hybrid_decision_board_service import HybridDecisionBoardService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_board(board):
    import streamlit as st

    metric_grid([
        ("Role", board.role_title, "Hybrid Board"),
        ("Candidates", str(board.total_candidates), "Compared"),
        ("Top Candidate", board.top_candidate.candidate_name if board.top_candidate else "-", "Final ranking"),
        ("Top Score", str(board.top_candidate.final_score) if board.top_candidate else "-", "Final score"),
    ])

    rows = [
        {
            "Rank": candidate.rank,
            "Candidate": candidate.candidate_name,
            "Final": candidate.final_score,
            "Decision Fit": candidate.decision_fit_score,
            "Semantic": candidate.semantic_score,
            "Career": candidate.career_score,
            "Hybrid": candidate.hybrid_score,
            "Readiness": candidate.readiness_level,
            "Action": candidate.action_recommendation,
        }
        for candidate in board.candidates
    ]
    st.dataframe(rows, use_container_width=True)

    names = [candidate.candidate_name for candidate in board.candidates]
    if not names:
        return

    selected = st.selectbox("Candidate detail", names)
    candidate = board.candidates[names.index(selected)]

    tab_summary, tab_gaps, tab_interview = st.tabs(["Summary", "Gaps", "Interview Focus"])

    with tab_summary:
        section_title(candidate.candidate_name)
        st.write(f"**Readiness:** {candidate.readiness_level}")
        st.write(f"**Action:** {candidate.action_recommendation}")
        st.write("**Top strengths**")
        st.write(candidate.top_strengths or ["No major strength detected."])

    with tab_gaps:
        section_title("Gaps")
        st.write(candidate.gaps or ["No critical gap detected."])

    with tab_interview:
        section_title("Interview Focus")
        st.write(candidate.interview_focus or ["Validate critical role requirements."])


def render_hybrid_decision_board():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Hybrid Decision Board",
        "Compare candidates using Decision Core and Hybrid Intelligence signals.",
        "Release 2.0 — Sprint 4G",
    )

    insight_card(
        "Decision-ready comparison",
        "This page consolidates decision fit, semantic matching, career intelligence and interview priorities.",
        "Hybrid Decision Intelligence",
    )

    service = HybridDecisionBoardService()

    if st.button("Run Hybrid Decision Board demo"):
        with st.spinner("Building hybrid decision board..."):
            _render_board(service.run_demo().board)
