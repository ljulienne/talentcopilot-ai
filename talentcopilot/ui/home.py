
def render_home():
    try:
        import streamlit as st

        st.title("TalentCopilot-AI")
        st.subheader("AI Recruitment Intelligence Platform")

        st.write(
            "Analyze candidates, review evidence, understand risks, "
            "and support recruitment decisions with explainable AI."
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Core", "Matching")
        col2.metric("AI", "Explainable")
        col3.metric("Decision", "Ready")

    except Exception:
        return
