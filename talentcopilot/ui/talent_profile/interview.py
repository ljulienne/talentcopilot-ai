import streamlit as st

from talentcopilot.interview.interview_generator import generate_interview_guide
from talentcopilot.ui.components import metric_card, section_title


def _render_bullets(items):
    if not items:
        st.info("No item available.")
        return

    for item in items:
        st.write(f"• {item}")


def render_interview(talent):
    guide = generate_interview_guide(talent)

    section_title(
        "Interview Intelligence",
        "Structured interview guide generated from the talent profile.",
    )

    col1, col2 = st.columns(2)

    with col1:
        metric_card(
            "Best Recommendation",
            guide.get("best_recommendation", "-"),
            "Based on best application",
        )

    with col2:
        metric_card(
            "Interview Focus Areas",
            len(guide.get("interview_focus", [])),
            "Suggested focus points",
        )

    with st.expander("Technical Questions", expanded=True):
        _render_bullets(guide.get("technical_questions", []))

    with st.expander("Behavioral Questions", expanded=True):
        _render_bullets(guide.get("behavioral_questions", []))

    with st.expander("Risk Validation Questions", expanded=True):
        _render_bullets(guide.get("risk_validation_questions", []))

    with st.expander("Role Fit Questions", expanded=True):
        _render_bullets(guide.get("role_fit_questions", []))

    with st.expander("Interview Focus", expanded=True):
        _render_bullets(guide.get("interview_focus", []))
