from __future__ import annotations


def render_section(title: str, subtitle: str = "") -> None:
    import streamlit as st

    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
