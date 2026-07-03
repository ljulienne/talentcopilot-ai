import streamlit as st


def skills_card(talent: dict):
    skills = talent.get("detected_skills", {}) or {}

    st.markdown(
        """
<div class="tc-card">
<h2>🧩 Skills Intelligence</h2>
<p class="tc-muted">Detected skills and capability domains.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if not skills:
        st.info("No structured skills detected yet.")
        return

    for category, values in skills.items():
        with st.expander(category, expanded=True):
            st.write(", ".join(sorted(set(values))))
