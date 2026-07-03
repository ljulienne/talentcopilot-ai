import streamlit as st

from talentcopilot.ui.design_system.colors import (
    PRIMARY,
    AI,
    SUCCESS,
    WARNING,
    DANGER,
    BACKGROUND,
    CARD,
    TEXT,
    TEXT_SECONDARY,
    BORDER,
)

def apply_theme():

    st.markdown(
        f"""
<style>

html, body, [class*="css"] {{
    background:{BACKGROUND};
    color:{TEXT};
    font-family:Inter, sans-serif;
}}

section.main {{
    background:{BACKGROUND};
}}

.tc-card {{
    background:{CARD};
    border:1px solid {BORDER};
    border-radius:16px;
    padding:20px;
    margin-bottom:16px;
}}

.tc-title {{
    font-size:34px;
    font-weight:700;
    color:{TEXT};
}}

.tc-subtitle {{
    font-size:18px;
    color:{TEXT_SECONDARY};
}}

div[data-testid="stMetric"] {{
    background:white;
    border-radius:14px;
    padding:12px;
    border:1px solid {BORDER};
}}

.stButton>button {{
    background:{PRIMARY};
    color:white;
    border-radius:10px;
    border:none;
    font-weight:600;
}}

.stButton>button:hover {{
    background:{AI};
}}

</style>
""",
        unsafe_allow_html=True,
    )
