from talentcopilot.ui.design_system.components import (
    activity_item, empty_state, enterprise_hero, insight_card,
    metric_grid, next_action_card, section_title, status_badge,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_design_system_showcase():
    import streamlit as st
    apply_enterprise_theme()
    enterprise_hero("TalentCopilot Design System", "Reusable Enterprise components for TalentCopilot workspaces.", "UI Showcase")
    section_title("Metrics")
    metric_grid([("Candidates", "12", "+3"), ("Interviews", "5", "This week"), ("Decision readiness", "91%", "+8%"), ("Evidence coverage", "96%", "High")])
    section_title("Badges")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: status_badge("Primary", "primary")
    with c2: status_badge("AI", "ai")
    with c3: status_badge("Success", "success")
    with c4: status_badge("Warning", "warning")
    with c5: status_badge("Danger", "danger")
    section_title("AI Insight Cards")
    insight_card("Review top-ranked candidate", "Alice Martin has strong evidence for HRIS transformation and stakeholder management.", "AI Priority")
    insight_card("Validate leadership depth", "Interview validation is recommended.", "Risk-Aware AI")
    section_title("Activity Feed")
    activity_item("09:41", "Recruitment loaded", "Transformation Lead scenario started.")
    activity_item("09:42", "Candidates analyzed", "3 candidate analyses available.")
    activity_item("09:43", "Report ready", "Executive report preview generated.")
    section_title("Next Action")
    next_action_card("Open Candidate Workspace", "Review the top-ranked candidate before moving to the Decision Board.", "Open workspace")
    section_title("Empty State")
    empty_state("No recruitment selected", "Load the Enterprise Demo or create a new recruitment to begin.", "Load demo")
