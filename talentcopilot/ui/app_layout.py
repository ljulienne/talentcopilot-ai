
def render_page_shell(title=None, subtitle=None, *args, **kwargs):
    try:
        import streamlit as st
        if title:
            st.title(title)
        if subtitle:
            st.caption(subtitle)
    except Exception:
        return
