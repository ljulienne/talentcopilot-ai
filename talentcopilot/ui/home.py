
import streamlit as st
from talentcopilot.ui.components import card, assistant_panel, section_title


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
        section_title(
            "Welcome to TalentCopilot",
            "Create a recruitment, analyze CVs, compare candidates and generate recruiter-ready reports."
        )

        card(
            "🚀 Start a new recruitment",
            "Create a recruitment context, upload one job description and analyze up to 50 CVs.",
            "Recommended"
        )

        card(
            "⚖️ Compare candidates",
            "Compare 2 to 5 shortlisted candidates side by side with scores, gaps, risks and languages.",
            "V1"
        )

        card(
            "📄 Generate recruiter reports",
            "Export a PDF summary with ranking, recommendations, gaps and interview questions.",
            "PDF"
        )

    with col2:
        assistant_panel(
            "Recruiter Copilot",
            "Start by creating a new recruitment. Then upload your job description and CVs from the Dashboard."
        )

        card(
            "🌍 Multilingual",
            "French, English and Mandarin support through the Talent Knowledge Base.",
            "FR / EN / ZH"
        )

        card(
            "🧠 Explainable AI",
            "TalentCopilot explains recommendations with evidence, gaps and interview focus points.",
            "Trust"
        )
