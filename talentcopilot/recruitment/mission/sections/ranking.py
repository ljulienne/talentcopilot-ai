from __future__ import annotations

from html import escape

from ..state import RecruitmentMissionState


def render_ranking(state: RecruitmentMissionState) -> None:
    import streamlit as st

    if not state.candidates:
        st.info("No analysed candidate is available yet.")
        return

    for candidate in state.candidates:
        confidence = f" · Confidence {candidate.confidence_score:.0f}%" if candidate.confidence_score is not None else ""
        st.markdown(
            f"""
            <div class="tc60-candidate">
              <div class="tc60-candidate-head"><span class="tc60-name">#{candidate.rank} · {escape(candidate.name)}</span><span class="tc60-score">{candidate.match_score:.0f}%</span></div>
              <div class="tc60-sub">{escape(candidate.recommendation)}{escape(confidence)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
