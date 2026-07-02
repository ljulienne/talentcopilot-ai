import streamlit as st

from talentcopilot.ai.recruiter_assistant import answer_recruiter_question
from talentcopilot.ui.components import section_title


def render_ask_copilot():
    section_title(
        "Ask TalentCopilot",
        "Ask questions about the active recruitment and candidate ranking."
    )

    question = st.text_input(
        "Your question",
        placeholder="Example: Who should I interview first?",
        key="ask_talentcopilot_question",
    )

    if st.button("💬 Ask TalentCopilot", use_container_width=True):
        recruitment = st.session_state.get("current_recruitment")

        if not recruitment:
            recruitment = {
                "context": st.session_state.get("recruitment_context"),
                "analysis_batch": st.session_state.get("analysis_batch"),
            }

        answer = answer_recruiter_question(question, recruitment)

        st.markdown("### 🧠 TalentCopilot")
        st.markdown(answer)
