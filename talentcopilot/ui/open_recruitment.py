import streamlit as st

from talentcopilot.storage.recruitment_store import (
    list_recruitments,
    load_recruitment,
    delete_recruitment,
    duplicate_recruitment,
)
from talentcopilot.ui.components import section_title, assistant_panel, metric_card


def _restore_recruitment(recruitment):
    st.session_state.current_recruitment = recruitment
    st.session_state.recruitment_context = recruitment.get("context")
    st.session_state.analysis_batch = recruitment.get("analysis_batch")
    st.success(f"Recruitment opened: {recruitment.get('title', 'Untitled Recruitment')}")


def _get_status(item):
    if item.get("candidate_count", 0) > 0:
        return "Complete"
    return "Draft"


def render_open_recruitment():
    st.markdown("""
    <div class="tc-hero">
        <h1>📂 Recruitment Manager</h1>
        <h3>Open, search and manage saved recruitment projects</h3>
        <p class="tc-muted">
        Resume previous analyses, duplicate projects or clean up old recruitments.
        </p>
    </div>
    """, unsafe_allow_html=True)

    recruitments = list_recruitments()

    if not recruitments:
        assistant_panel(
            "Recruiter Copilot",
            "No saved recruitment found yet. Create a new recruitment, analyze candidates, then save it from the Dashboard."
        )
        return

    col1, col2, col3 = st.columns(3)

    complete_count = sum(1 for item in recruitments if _get_status(item) == "Complete")
    draft_count = len(recruitments) - complete_count

    with col1:
        metric_card("Saved Recruitments", len(recruitments), "Available projects")

    with col2:
        metric_card("Complete", complete_count, "With candidate results", "#10B981")

    with col3:
        metric_card("Draft", draft_count, "Without analysis yet", "#F59E0B")

    st.divider()

    section_title(
        "Search & Filter",
        "Find a recruitment by title, ID or status."
    )

    search = st.text_input("Search recruitments", placeholder="Search by title or ID...")
    status_filter = st.selectbox("Status", ["All", "Draft", "Complete"])

    filtered = []

    for item in recruitments:
        title = item.get("title", "Untitled Recruitment")
        recruitment_id = item.get("id", "")
        status = _get_status(item)

        matches_search = (
            not search
            or search.lower() in title.lower()
            or search.lower() in recruitment_id.lower()
        )

        matches_status = status_filter == "All" or status == status_filter

        if matches_search and matches_status:
            filtered.append(item)

    st.caption(f"{len(filtered)} recruitment(s) found")

    st.divider()

    if not filtered:
        st.info("No recruitment matches your search.")
        return

    for item in filtered:
        title = item.get("title", "Untitled Recruitment")
        recruitment_id = item.get("id")
        candidate_count = item.get("candidate_count", 0)
        updated_at = item.get("updated_at", "-")
        status = _get_status(item)

        with st.container():
            col_info, col_status, col_open, col_duplicate, col_delete = st.columns(
                [4, 1.3, 1.2, 1.4, 1.2]
            )

            with col_info:
                st.subheader(title)
                st.caption(f"ID: {recruitment_id}")
                st.caption(f"Last updated: {updated_at}")

            with col_status:
                if status == "Complete":
                    st.success("Complete")
                else:
                    st.warning("Draft")
                st.caption(f"{candidate_count} candidate(s)")

            with col_open:
                if st.button("Open", key=f"open_{recruitment_id}", use_container_width=True):
                    recruitment = load_recruitment(recruitment_id)
                    _restore_recruitment(recruitment)

            with col_duplicate:
                if st.button("Duplicate", key=f"duplicate_{recruitment_id}", use_container_width=True):
                    duplicate_recruitment(recruitment_id)
                    st.success("Duplicated")
                    st.rerun()

            with col_delete:
                confirm_key = f"confirm_delete_{recruitment_id}"

                if st.session_state.get(confirm_key):
                    if st.button("Confirm", key=f"confirm_btn_{recruitment_id}", use_container_width=True):
                        delete_recruitment(recruitment_id)
                        st.warning(f"Deleted: {title}")
                        st.rerun()
                else:
                    if st.button("Delete", key=f"delete_{recruitment_id}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

            st.divider()
