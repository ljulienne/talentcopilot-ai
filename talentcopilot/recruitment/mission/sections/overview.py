from __future__ import annotations

from ..state import RecruitmentMissionState


def render_overview(state: RecruitmentMissionState) -> None:
    import streamlit as st

    st.write(f"**Current stage:** {state.stage}")
    st.write(f"**Analysis coverage:** {state.analyzed_count}/{state.candidate_count} candidates")
    if state.has_analysis:
        st.success(f"The official ranking is available. {state.recommended_candidate} currently leads.")
    else:
        st.info("Upload and analyse candidates to generate the official ranking.")
