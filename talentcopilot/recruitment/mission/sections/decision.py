from __future__ import annotations

from ..state import RecruitmentMissionState


def render_decision(state: RecruitmentMissionState) -> None:
    import streamlit as st

    if not state.has_analysis:
        st.info("A decision recommendation requires an official ranking.")
        return
    lead = state.candidates[0]
    st.metric("Current recommendation", lead.name, f"{lead.match_score:.0f}% official match")
    st.write(f"**Decision signal:** {lead.recommendation}")
    st.warning("TalentCopilot supports the hiring team; the final hiring decision requires human validation.")
