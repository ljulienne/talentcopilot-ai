from __future__ import annotations

from ..state import RecruitmentMissionState
from ..narrative import recruiter_reasoning


def render_reasoning(state: RecruitmentMissionState) -> None:
    import streamlit as st

    for candidate in state.candidates:
        with st.expander(f"Why {candidate.name} ranks #{candidate.rank}", expanded=candidate.rank == 1):
            for paragraph in recruiter_reasoning(candidate):
                st.write(paragraph)
            st.caption(
                "This advisory narrative interprets the existing evidence and does not recalculate "
                "the official score, rank or recommendation."
            )
