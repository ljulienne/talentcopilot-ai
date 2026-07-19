from __future__ import annotations

from ..state import RecruitmentMissionState


def render_comparison(state: RecruitmentMissionState) -> None:
    import streamlit as st

    if len(state.candidates) < 2:
        st.info("At least two analysed candidates are required.")
        return
    lead = state.candidates[0]
    rows = []
    for candidate in state.candidates:
        rows.append({
            "Rank": candidate.rank,
            "Candidate": candidate.name,
            "Official match": f"{candidate.match_score:.0f}%",
            "Gap to lead": f"{max(0.0, lead.match_score - candidate.match_score):.0f} pts",
            "Recommendation": candidate.recommendation,
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
