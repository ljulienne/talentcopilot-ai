from __future__ import annotations

from html import escape

from talentcopilot.models.mission import MissionCanvas
from talentcopilot.models.mission_workspace import MissionHealth, MissionWorkspaceSnapshot
from talentcopilot.services.mission_workspace import build_mission_workspace
from talentcopilot.ui.navigation_actions import request_page


def _tone(health: MissionHealth) -> str:
    return {
        MissionHealth.STRONG: "strong",
        MissionHealth.NEEDS_ATTENTION: "attention",
        MissionHealth.AT_RISK: "risk",
    }[health]


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-mission-shell{margin-top:1.25rem;padding:1.35rem;border:1px solid #dbe4f0;border-radius:24px;background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);box-shadow:0 16px 42px rgba(15,23,42,.08)}
        .tc-mission-head{display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;margin-bottom:1rem}.tc-mission-kicker{font-size:.72rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#6366f1}.tc-mission-title{font-size:1.55rem;font-weight:820;color:#0f172a;margin:.2rem 0}.tc-mission-stage{color:#64748b;font-size:.9rem}
        .tc-health{display:inline-block;border-radius:999px;padding:.36rem .7rem;font-size:.76rem;font-weight:850}.tc-health-strong{background:#dcfce7;color:#166534}.tc-health-attention{background:#fef3c7;color:#92400e}.tc-health-risk{background:#fee2e2;color:#991b1b}
        .tc-panel{padding:1rem;border-radius:18px;border:1px solid #e2e8f0;background:#fff;min-height:180px}.tc-panel h4{margin:0 0 .6rem;color:#0f172a}.tc-panel p,.tc-panel li{color:#475569;font-size:.89rem;line-height:1.45}
        .tc-action{padding:.8rem .9rem;border-radius:14px;background:#eef2ff;border:1px solid #c7d2fe;margin-bottom:.55rem}.tc-action strong{display:block;color:#312e81}.tc-action span{font-size:.82rem;color:#475569}.tc-gain{float:right;font-weight:800;color:#047857}
        .tc-journal{padding:.65rem 0;border-bottom:1px solid #eef2f7}.tc-journal:last-child{border-bottom:none}.tc-journal strong{display:block;color:#0f172a;font-size:.9rem}.tc-journal span{color:#64748b;font-size:.82rem}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_mission_workspace(canvas: MissionCanvas, session=None) -> MissionWorkspaceSnapshot:
    import streamlit as st

    snapshot = build_mission_workspace(canvas, session)
    _styles()
    tone = _tone(snapshot.health)

    st.markdown(
        f"""
        <div class="tc-mission-shell">
          <div class="tc-mission-head">
            <div><div class="tc-mission-kicker">Mission Cockpit</div><div class="tc-mission-title">{escape(snapshot.mission_title)}</div><div class="tc-mission-stage">{escape(snapshot.domain_label)} · {escape(snapshot.stage)}</div></div>
            <span class="tc-health tc-health-{tone}">{escape(snapshot.health.value)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Mission readiness", f"{snapshot.readiness}%", "Decision preparedness")
    m2.metric("Decision confidence", f"{snapshot.decision_confidence}%", "Evidence-based")
    m3.metric("Current stage", snapshot.stage, snapshot.domain_label)

    left, center, right = st.columns([1.05, 1.2, 1.05])
    with left:
        st.markdown('<div class="tc-panel"><h4>Mission health</h4>', unsafe_allow_html=True)
        for item in snapshot.health_reasons:
            st.write(f"• {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    with center:
        st.markdown('<div class="tc-panel"><h4>Next best actions</h4>', unsafe_allow_html=True)
        for index, action in enumerate(snapshot.next_actions, start=1):
            gain = f'<span class="tc-gain">+{action.readiness_gain}%</span>' if action.readiness_gain else ""
            st.markdown(
                f'<div class="tc-action">{gain}<strong>{index}. {escape(action.title)}</strong><span>{escape(action.reason)}</span></div>',
                unsafe_allow_html=True,
            )
        if not snapshot.next_actions:
            st.caption("No additional action has been generated yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="tc-panel"><h4>Mission journal</h4>', unsafe_allow_html=True)
        for entry in snapshot.journal:
            st.markdown(
                f'<div class="tc-journal"><strong>{escape(entry.label)}</strong><span>{escape(entry.detail)}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.info(snapshot.reasoning)
    primary = snapshot.next_actions[0] if snapshot.next_actions else None
    target = primary.target_page if primary else canvas.target_page
    if target and st.button("Continue with the recommended action", key=f"mission_workspace_continue_{canvas.domain.value}", type="primary"):
        request_page(target, reason=f"Continued from Mission Cockpit: {snapshot.mission_title}.")
        st.rerun()

    return snapshot
