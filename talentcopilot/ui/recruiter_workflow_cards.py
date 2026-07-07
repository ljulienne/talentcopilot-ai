from typing import Any


def render_recruiter_workflow(report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Enterprise Recruiter Workflow")

    col1, col2, col3 = st.columns(3)
    col1.metric("Role", report.role_title)
    col2.metric("Overall Status", report.overall_status.value)
    col3.metric("Completed Stages", report.completed_count)

    st.info(report.recommended_next_action)

    if report.shortlist_candidate_names:
        st.success("Shortlist-ready: " + ", ".join(report.shortlist_candidate_names))

    if report.blockers:
        with st.expander("Blockers"):
            for blocker in report.blockers:
                st.warning(blocker)

    for stage in report.stages:
        with st.expander(f"{stage.name.value} — {stage.status.value}"):
            st.write(stage.explanation)
            if stage.next_action:
                st.caption(f"Next action: {stage.next_action}")
