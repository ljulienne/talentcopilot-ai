
import streamlit as st


def interview_card(talent: dict):

    questions = talent.get("interview_questions", [])

    st.markdown(
        """
<div class="tc-card">

<h2>🎤 Interview Preparation</h2>

<p class="tc-muted">
Suggested interview questions generated from the candidate profile.
</p>

</div>
""",
        unsafe_allow_html=True,
    )

    if not questions:
        st.info("No interview questions available yet.")
        return

    for i, question in enumerate(questions, start=1):
        st.write(f"**{i}.** {question}")
