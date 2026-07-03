import streamlit as st


def timeline_card(talent: dict):
    history = talent.get("application_history", []) or []

    st.markdown(
        """
<div class="tc-card">
<h2>🕒 Candidate Timeline</h2>
<p class="tc-muted">Recruitment history and key candidate events.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if not history:
        st.info("No timeline history available yet.")
        return

    for record in history:
        title = record.get("recruitment_title", "Untitled Recruitment")
        score = record.get("score", 0)
        recommendation = record.get("recommendation", "-")
        summary = record.get("executive_summary", "")

        st.write(f"**{title}** — {score}% match")
        st.caption(f"Recommendation: {recommendation}")

        if summary:
            st.write(summary)

        st.divider()
