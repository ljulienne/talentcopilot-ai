
def footer(*args, **kwargs):
    try:
        import streamlit as st
        st.markdown("---")
        st.caption("TalentCopilot-AI")
    except Exception:
        return
