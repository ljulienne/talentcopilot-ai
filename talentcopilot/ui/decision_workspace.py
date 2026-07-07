
def render_decision_workspace(*args, **kwargs):
    try:
        import streamlit as st
        st.title("Decision Workspace")
        st.info("This page is available as a safe fallback. Full UI module will be enhanced in a future sprint.")
    except Exception:
        return
