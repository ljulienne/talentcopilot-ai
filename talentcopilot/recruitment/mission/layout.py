"""Reusable visual shell for Release 6.0A."""

from __future__ import annotations

from html import escape

from .state import RecruitmentMissionState


def apply_mission_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc60-hero{padding:1.45rem 1.55rem;border:1px solid #dbe4f0;border-radius:24px;background:linear-gradient(135deg,#fff 0%,#f6f8ff 100%);box-shadow:0 16px 44px rgba(15,23,42,.07);margin:.4rem 0 1rem}
        .tc60-kicker{font-size:.72rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#4f46e5}.tc60-title{font-size:1.75rem;font-weight:840;color:#0f172a;margin:.24rem 0}.tc60-meta{font-size:.88rem;color:#64748b}
        .tc60-summary{padding:1rem 1.1rem;border-radius:18px;background:#eef2ff;border:1px solid #c7d2fe;color:#312e81;line-height:1.55;margin:.9rem 0 1.1rem}
        .tc60-candidate{padding:1rem 1.05rem;border:1px solid #e2e8f0;border-radius:18px;background:#fff;margin-bottom:.65rem}.tc60-candidate-head{display:flex;justify-content:space-between;gap:1rem}.tc60-name{font-weight:800;color:#0f172a}.tc60-score{font-size:1.2rem;font-weight:850;color:#312e81}.tc60-sub{font-size:.82rem;color:#64748b;margin-top:.2rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_mission_hero(state: RecruitmentMissionState) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc60-hero">
          <div class="tc60-kicker">Recruitment mission</div>
          <div class="tc60-title">{escape(state.role_title)}</div>
          <div class="tc60-meta">{escape(state.stage)} · {state.candidate_count} candidates · Session {escape(state.session_id)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(max(0, min(100, state.progress_percent)) / 100)
    st.caption(f"{state.progress_percent}% complete · {state.stage}")


def render_executive_metrics(state: RecruitmentMissionState) -> None:
    import streamlit as st

    columns = st.columns(4)
    columns[0].metric("Candidates", state.candidate_count, f"{state.analyzed_count} analysed")
    columns[1].metric("Recommended", state.recommended_candidate, f"{state.recommended_score:.0f}% match" if state.has_analysis else "Awaiting analysis")
    columns[2].metric("AI confidence", f"{state.average_confidence:.0f}%" if state.average_confidence is not None else "—", "Official confidence")
    columns[3].metric("Mission status", state.status, state.stage)


def render_ai_summary(state: RecruitmentMissionState) -> None:
    import streamlit as st

    st.markdown(
        f'<div class="tc60-summary"><strong>TalentCopilot guidance</strong><br>{escape(state.summary)}</div>',
        unsafe_allow_html=True,
    )
