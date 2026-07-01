
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .tc-hero {
        background: linear-gradient(135deg, #EEF2FF, #F8FAFC);
        padding: 32px;
        border-radius: 24px;
        border: 1px solid #E5E7EB;
        margin-bottom: 24px;
    }
    .tc-card {
        background: white;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        margin-bottom: 16px;
    }
    .tc-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #EEF2FF;
        color: #4338CA;
        font-weight: 600;
        font-size: 13px;
    }
    .tc-muted { color: #64748B; }
    </style>
    """, unsafe_allow_html=True)
