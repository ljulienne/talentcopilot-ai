
def render_new_recruitment(*args, **kwargs):
    try:
        import streamlit as st
        st.title("Recruitment Wizard")
        st.info("This page is available as a safe fallback. Full UI module will be enhanced in a future sprint.")
    except Exception:
        return
