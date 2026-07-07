
def render_candidate_comparison(*args, **kwargs):
    try:
        import streamlit as st
        st.title("Comparison")
        st.info("This page is available as a safe fallback. Full UI module will be enhanced in a future sprint.")
    except Exception:
        return
