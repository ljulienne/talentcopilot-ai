from __future__ import annotations

from ..state import RecruitmentMissionState


def _markdown(state: RecruitmentMissionState) -> str:
    lines = [f"# Recruitment Mission — {state.role_title}", "", state.summary, "", "## Official ranking"]
    for item in state.candidates:
        lines.append(f"{item.rank}. **{item.name}** — {item.match_score:.0f}% — {item.recommendation}")
    lines.extend(["", "_Final hiring accountability remains with the human decision team._"])
    return "\n".join(lines)


def render_report(state: RecruitmentMissionState) -> None:
    import streamlit as st

    report = _markdown(state)
    st.download_button(
        "Download mission brief",
        data=report,
        file_name="talentcopilot_recruitment_mission.md",
        mime="text/markdown",
        key="tc60a_mission_report",
    )
    st.markdown(report)
