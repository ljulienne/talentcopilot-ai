from typing import Any, Iterable


def session_action_bar():
    import streamlit as st

    from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
    from talentcopilot.services.streamlit_session_bridge import (
        clear_streamlit_session,
        get_streamlit_session,
        set_streamlit_session,
    )

    col1, col2, col3 = st.columns([2, 2, 4])

    with col1:
        if st.button("Create demo recruitment session"):
            set_streamlit_session(create_demo_recruitment_session())
            st.success("Demo recruitment session created.")

    with col2:
        if st.button("Clear session"):
            clear_streamlit_session()
            st.info("Session cleared.")

    session = get_streamlit_session()
    with col3:
        if session:
            st.caption(f"Active session: {session.session_id} · {session.role_title}")
        else:
            st.caption("No active recruitment session.")

    return session


def session_overview(session: Any):
    import streamlit as st

    if session is None:
        st.info("No recruitment session available. Create a demo session to explore the workflow.")
        return

    cols = st.columns(4)
    cols[0].metric("Role", session.role_title)
    cols[1].metric("Candidates", session.candidate_count)
    cols[2].metric("Analyzed", session.analyzed_count)
    cols[3].metric("Errors", session.error_count)


def ranked_candidates_table(session: Any):
    import streamlit as st

    if session is None or not getattr(session, "analyses", None):
        st.info("No candidate analyses available yet.")
        return

    rows = []
    for analysis in session.ranked_analyses:
        decision = "-"
        if analysis.decision_report:
            decision = getattr(
                analysis.decision_report.recommendation,
                "value",
                analysis.decision_report.recommendation,
            )

        rows.append({
            "Rank": analysis.rank,
            "Candidate": analysis.candidate_name,
            "Match Score": analysis.match_score,
            "Status": analysis.status.value,
            "Decision": decision,
        })

    st.dataframe(rows, use_container_width=True)


def candidate_detail_cards(session: Any):
    import streamlit as st

    if session is None or not getattr(session, "analyses", None):
        st.info("No candidate detail available.")
        return

    for analysis in session.ranked_analyses:
        with st.expander(f"#{analysis.rank} {analysis.candidate_name} — Match {analysis.match_score:.0f}%"):
            st.write(f"Status: {analysis.status.value}")

            if analysis.decision_report:
                st.markdown("**Decision**")
                recommendation = getattr(
                    analysis.decision_report.recommendation,
                    "value",
                    analysis.decision_report.recommendation,
                )
                st.write(recommendation)
                st.caption(getattr(analysis.decision_report, "executive_summary", ""))

            if analysis.recruiter_copilot_report:
                st.markdown("**Recruiter Copilot**")
                st.write(analysis.recruiter_copilot_report.recruiter_summary)

            if analysis.errors:
                for error in analysis.errors:
                    st.warning(error)


def copilot_guidance(session: Any):
    import streamlit as st

    if session is None:
        st.info("No active session.")
        return

    has_guidance = False
    for analysis in session.ranked_analyses:
        report = analysis.recruiter_copilot_report
        if not report:
            continue

        has_guidance = True
        with st.expander(f"{analysis.candidate_name} — Recruiter guidance"):
            st.write(report.recruiter_summary)
            if report.actions:
                st.markdown("**Recommended actions**")
                for action in report.actions:
                    st.write(f"- {action.title}: {action.rationale}")
            if report.interview_questions:
                st.markdown("**Interview questions**")
                for question in report.interview_questions[:3]:
                    st.write(f"- {question.question}")

    if not has_guidance:
        st.info("No recruiter guidance available yet.")


def report_readiness(session: Any):
    import streamlit as st

    if session is None:
        st.info("No active session.")
        return

    st.write("This recruitment session is ready for reporting if candidate analyses are available.")
    session_overview(session)
    ranked_candidates_table(session)
