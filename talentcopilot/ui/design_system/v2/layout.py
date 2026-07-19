from contextlib import contextmanager
import streamlit as st
from .components import executive_hero
from .theme import apply_enterprise_v2_theme

@contextmanager
def page_container():
    st.markdown('<div class="tc2-page">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

@contextmanager
def enterprise_page(title: str, *, subtitle=None, eyebrow="TalentCopilot", metadata=None):
    apply_enterprise_v2_theme()
    with page_container():
        executive_hero(title, subtitle=subtitle, eyebrow=eyebrow, metadata=metadata)
        yield
