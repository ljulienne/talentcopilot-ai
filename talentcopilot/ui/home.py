
import streamlit as st
from talentcopilot.ui.widgets import card

def render_home():
    st.markdown("""
    <div class="tc-hero">
        <h1>🧠 TalentCopilot AI</h1>
        <h3>AI Recruitment Intelligence Platform</h3>
        <p class="tc-muted">
        Understand every candidate. Explain every hiring decision.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        card(
            "Start a new recruitment",
            "Upload one job description and up to 50 CVs to generate a ranking, candidate insights, gaps, evidence and interview questions.",
            "V1 Ready"
        )

        st.info("Go to **Dashboard** in the sidebar to start a new analysis.")

    with col2:
        card("Multilingual", "French, English and Mandarin support through the Talent Knowledge Base.", "FR / EN / ZH")
        card("Explainable AI", "Scores are supported by evidence, gaps and interview focus points.", "Trust")
