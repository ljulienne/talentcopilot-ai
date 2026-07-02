import streamlit as st

from talentcopilot.storage.recruitment_store import (
    list_recruitments,
    load_recruitment,
    delete_recruitment,
)
from talentcopilot.ui.components import section_title, assistant_panel, metric_card


def _restore_recruitment(recruitment):
    st.session_state.current_recruitment = recruitment
    st.session_state.recruitment_context = recruitment.get("context")
    st.session_state.analysis_batch = recruitment.get("analysis_batch")
    st.success(f"Recruitment opened: {recruitment.get('title', 'Untitled Recruitment')}")


def render_open_recruitment():
    st.markdown("""
    <div class="tc-hero">
        <h1>📂 Open Recruitment</h1>
        <h3>Resume a saved recruitment analysis</h3>
        <p class="tc-muted">
        Open a previous recruitment and restore its context, analysis results and reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

    section_title(
        "Saved Recruitments",
        "Select a previous recruitment to continue your work."
    )

    recruitments = list_recruitments()

    if not recruitments:
        assistant_panel(
            "Recruiter Copilot",
            "No saved recruitment found yet. Create a new recruitment, analyze candidates, then save it from the Dashboard."
        )
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Saved Recruitments", len(recruitments), "Available projects")

    with col2:
        analyzed = sum(1 for item in recruitments if item.get("candidate_count", 0) > 0)
        metric_card("Analyzed", analyzed, "With candidate results")

    with col3:
        latest = recruitments[0].get("updated_at", "-")
        metric_card("Last Update", latest[:10] if latest else "-", "Most recent save")

    st.divider()

    for item in recruitments:
        title = item.get("title", "Untitled Recruitment")
        recruitment_id = item.get("id")
        candidate_count = item.get("candidate_count", 0)
        updated_at = item.get("updated_at", "-")

        with st.container():
            col_info, col_open, col_delete = st.columns([5, 1.5, 1.5])

            with col_info:
                st.subheader(title)
                st.caption(f"ID: {recruitment_id}")
                st.write(f"Candidates analyzed: **{candidate_count}**")
                st.caption(f"Last updated: {updated_at}")

            with col_open:
                if st.button("Open", key=f"open_{recruitment_id}", use_container_width=True):
                    recruitment = load_recruitment(recruitment_id)
                    _restore_recruitment(recruitment)

            with col_delete:
                if st.button("Delete", key=f"delete_{recruitment_id}", use_container_width=True):
                    delete_recruitment(recruitment_id)
                    st.warning(f"Deleted: {title}")
                    st.rerun()

            st.divider()
