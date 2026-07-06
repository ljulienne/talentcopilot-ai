import streamlit as st

from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceViewModel


def render_interview_panel(view_model: DecisionWorkspaceViewModel) -> None:
    st.subheader("Interview Intelligence")

    if not view_model.interview_guide:
        st.info("No interview guide available yet.")
        return

    st.write(view_model.interview_guide.interview_focus)

    for question in view_model.interview_guide.questions[:3]:
        with st.expander(question.question, expanded=False):
            st.markdown("**Objective**")
            st.write(question.objective)

            st.markdown("**Strong answer should include**")
            for item in question.strong_answer_should_include:
                st.write(f"- {item}")

            st.markdown("**Red flags**")
            for item in question.red_flags:
                st.write(f"- {item}")
