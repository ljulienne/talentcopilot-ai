from __future__ import annotations

from ..state import RecruitmentMissionState


def render_interview(state: RecruitmentMissionState) -> None:
    import streamlit as st

    shortlist = [item for item in state.candidates if item.rank <= 3]
    if not shortlist:
        st.info("Interview preparation becomes available after candidate analysis.")
        return
    for candidate in shortlist:
        with st.expander(f"{candidate.name} · decision-focused interview priorities"):
            st.caption(
                "Each priority is designed to resolve a specific uncertainty in the current evidence, "
                "not to repeat generic interview questions."
            )
            for index, focus in enumerate(candidate.validation_focus, start=1):
                st.markdown(f"**Priority {index}**")
                st.info(focus)
            st.caption("Detailed questions, positive signals and warning signals are available in Interview Intelligence.")
