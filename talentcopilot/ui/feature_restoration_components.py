from typing import Any


def page_purpose(title: str, purpose: str, what_you_can_do: list[str]):
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-card">
            <span class="tc-badge">Purpose</span>
            <h2 style="margin-bottom:0.2rem;">{title}</h2>
            <p class="tc-muted">{purpose}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("What this page is for", expanded=False):
        for item in what_you_can_do:
            st.write(f"- {item}")


def session_required_hint(session: Any):
    import streamlit as st

    if session is None:
        st.info("Create a demo recruitment session from Decision Center to populate this page.")
        return False
    return True


def candidate_kpi_strip(session: Any):
    import streamlit as st

    if session is None:
        st.info("No active recruitment session.")
        return

    best_score = 0
    best_candidate = "-"
    if getattr(session, "ranked_analyses", None):
        first = session.ranked_analyses[0]
        best_score = getattr(first, "match_score", 0)
        best_candidate = getattr(first, "candidate_name", "-")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Role", session.role_title)
    col2.metric("Candidates", session.candidate_count)
    col3.metric("Best candidate", best_candidate)
    col4.metric("Best score", f"{best_score:.0f}%")


def decision_summary_for_analysis(analysis: Any):
    import streamlit as st

    decision_report = getattr(analysis, "decision_report", None)
    if not decision_report:
        st.caption("No decision report available.")
        return

    recommendation = getattr(decision_report.recommendation, "value", decision_report.recommendation)
    st.write(f"**Decision:** {recommendation}")
    st.caption(getattr(decision_report, "executive_summary", ""))
