from __future__ import annotations

from ..state import RecruitmentMissionState


def render_interview(state: RecruitmentMissionState) -> None:
    import streamlit as st

    shortlist = [item for item in state.candidates if item.rank <= 3]
    if not shortlist:
        st.info("Interview preparation becomes available after candidate analysis.")
        return
    for candidate in shortlist:
        with st.expander(f"{candidate.name} · validation focus"):
            if candidate.risks:
                for risk in candidate.risks:
                    st.warning(risk)
            else:
                st.write("Validate the strongest claims, scope of ownership and measurable outcomes.")
            st.caption("Detailed interview intelligence remains available through the existing service layer.")
