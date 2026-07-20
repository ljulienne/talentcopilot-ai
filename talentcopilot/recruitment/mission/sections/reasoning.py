from __future__ import annotations

from ..state import RecruitmentMissionState


def render_reasoning(state: RecruitmentMissionState) -> None:
    import streamlit as st

    for candidate in state.candidates:
        with st.expander(f"Why {candidate.name} ranks #{candidate.rank}", expanded=candidate.rank == 1):
            rationale = candidate.rationale or candidate.recommendation
            for paragraph in [item.strip() for item in str(rationale).split("\n\n") if item.strip()]:
                st.write(paragraph)
            if candidate.strengths:
                st.markdown("**Evidence highlights**")
                for item in candidate.strengths:
                    st.write(f"- {item}")
            st.caption("This explanation presents existing evidence and does not recalculate the official score.")
