from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import page_purpose, session_required_hint


@safe_render
def render_comparison_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Comparison",
        "Compare candidates side by side using the same session data.",
        "Analyze",
    )

    page_purpose(
        "Comparison",
        "This page is for comparing candidates, not for individual deep-dives.",
        [
            "Compare ranking and match score.",
            "Compare AI decision recommendations.",
            "Identify who should move forward first.",
        ],
    )

    session = get_streamlit_session()
    if not session_required_hint(session):
        return

    rows = []
    for analysis in session.ranked_analyses:
        decision = "-"
        if analysis.decision_report:
            decision = getattr(analysis.decision_report.recommendation, "value", analysis.decision_report.recommendation)

        rows.append({
            "Rank": analysis.rank,
            "Candidate": analysis.candidate_name,
            "Match": analysis.match_score,
            "Decision": decision,
            "Has Copilot": bool(analysis.recruiter_copilot_report),
            "Errors": len(analysis.errors),
        })

    st.dataframe(rows, use_container_width=True)
