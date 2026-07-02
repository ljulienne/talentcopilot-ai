
import streamlit as st

from talentcopilot.config import APP_VERSION
from talentcopilot.ui.components import section_title, metric_card, assistant_panel, card


def render_settings():
    st.markdown("""
    <div class="tc-hero">
        <h1>⚙️ Settings</h1>
        <h3>Application configuration</h3>
        <p class="tc-muted">
        Review TalentCopilot configuration and supported capabilities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    section_title(
        "Application",
        "Current application status and configuration."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Version", APP_VERSION, "Current release")

    with col2:
        metric_card("Status", "Beta", "V1 in progress", "#10B981")

    with col3:
        metric_card("Max CV Uploads", "50", "Per recruitment", "#4F46E5")

    card(
        "Supported Languages",
        "English, French and Mandarin are supported through the multilingual Talent Knowledge Base.",
        "FR / EN / ZH"
    )

    card(
        "AI Provider",
        "TalentCopilot currently uses OpenAI through a centralized AI provider module.",
        "OpenAI"
    )

    assistant_panel(
        "Product Note",
        "Settings are intentionally simple for the V1. Advanced configuration will be added later only if it improves recruiter decision-making."
    )
