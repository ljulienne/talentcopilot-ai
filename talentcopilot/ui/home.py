import streamlit as st

from talentcopilot.ui.design_system.components import enterprise_hero
from talentcopilot.ui.design_system.theme import apply_enterprise_theme

from talentcopilot.ui.next_shell import (
    apply_next_style,
    diagnostic_card,
    insight_card,
    recommendation_block,
)


def render_home():
    apply_next_style()
    apply_enterprise_theme()

    enterprise_hero(
        "Executive Brief",
        "TalentCopilot starts with a briefing, not a dashboard: what matters, why it matters, and what decision should come next.",
    )

    recommendation_block(
        "Overall recommendation",
        "Use TalentCopilot as an AI diagnostic layer above existing HR systems. Start with Recruitment Diagnostic today, then expand toward Organization Intelligence and collaboration risk analysis.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        insight_card(
            "What the AI found",
            "The existing engine already supports parsing, matching, reasoning, evidence, interview intelligence and reporting.",
            "Release 0.1A keeps the engine and reframes the experience.",
        )
    with col2:
        insight_card(
            "What changes now",
            "The product is reorganized around diagnostics: recruitment, candidate, interview, organization and reports.",
            "One workspace = one decision.",
        )
    with col3:
        insight_card(
            "What comes next",
            "Organization Intelligence becomes the strategic direction: silos, hidden experts, knowledge flows and collaboration risks.",
            "Preview now, engine later.",
        )

    st.markdown("### Choose an AI diagnostic")
    c1, c2 = st.columns(2)
    with c1:
        diagnostic_card(
            "Recruitment Diagnostic",
            "Did we find the right candidates, and what should be verified before deciding?",
            "Available now",
        )
        diagnostic_card(
            "Candidate Diagnostic",
            "Should this person move forward, and what evidence supports the recommendation?",
            "Available now",
        )
        diagnostic_card(
            "Interview Diagnostic",
            "What must be challenged during the interview to reduce decision uncertainty?",
            "Available now",
        )
    with c2:
        diagnostic_card(
            "Organization Diagnostic",
            "Where are the invisible silos, connectors and collaboration risks?",
            "Preview in Release 0.1A",
        )
        diagnostic_card(
            "Skills Diagnostic",
            "Which capabilities will become critical or scarce?",
            "Planned",
        )
        diagnostic_card(
            "Transformation Diagnostic",
            "What organizational risks could slow down a change program?",
            "Planned",
        )

    st.info("Release 0.1A is a product shell reboot. It simplifies the experience while preserving backend compatibility.")
