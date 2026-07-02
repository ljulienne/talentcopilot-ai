import streamlit as st

from talentcopilot.ui.components import section_title


def render_history(talent):
    section_title(
        "Application History",
        "All recruitment analyses linked to this talent.",
    )

    history = talent.get("application_history", [])

    if not history:
        st.info("No application history available.")
        return

    for record in history:
        st.write(
            f"**{record.get('recruitment_title', 'Untitled Recruitment')}** "
            f"— {record.get('score', 0)}% match"
        )
        st.caption(
            f"Confidence: {record.get('confidence', 0)}% · "
            f"Recommendation: {record.get('recommendation', '-')}"
        )

        summary = record.get("executive_summary")
        if summary:
            st.write(summary)

        st.divider()
