from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Iterable

from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.navigation_actions import request_page
from talentcopilot.ui.project_hub import build_project_summaries
from talentcopilot.storage.recruitment_store import list_recruitments
from talentcopilot.models.mission import MissionCanvas
from talentcopilot.services.mission_intelligence import understand_mission
from talentcopilot.ui.mission_workspace import render_mission_workspace


@dataclass(frozen=True)
class BriefingDomain:
    key: str
    title: str
    question: str
    description: str
    status: str
    status_tone: str
    metric: str
    target_page: str | None


@dataclass(frozen=True)
class BriefingPriority:
    title: str
    detail: str
    tone: str = "attention"


def _count(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _session_snapshot(session: Any | None) -> dict[str, Any]:
    if session is None:
        return {
            "role_title": "No active recruitment",
            "candidate_count": 0,
            "analyzed_count": 0,
            "has_recruitment": False,
        }

    candidate_count = _count(getattr(session, "candidate_count", 0))
    analyzed_count = _count(getattr(session, "analyzed_count", 0))
    if candidate_count == 0:
        candidates = getattr(session, "candidates", None)
        if candidates is not None:
            try:
                candidate_count = len(candidates)
            except TypeError:
                pass

    return {
        "role_title": str(getattr(session, "role_title", "Active recruitment")),
        "candidate_count": candidate_count,
        "analyzed_count": analyzed_count,
        "has_recruitment": True,
    }


def build_briefing_domains(session: Any | None) -> tuple[BriefingDomain, ...]:
    snapshot = _session_snapshot(session)
    recruitment_ready = snapshot["has_recruitment"] and snapshot["candidate_count"] > 0
    recruitment_status = "Ready" if recruitment_ready else "Start here"
    recruitment_tone = "ready" if recruitment_ready else "attention"
    recruitment_metric = (
        f"{snapshot['analyzed_count']}/{snapshot['candidate_count']} candidates analysed"
        if recruitment_ready
        else "Job description and CVs required"
    )

    return (
        BriefingDomain(
            "hire",
            "Recruitment",
            "Who should we hire?",
            "Create or continue a recruitment, compare candidates and prepare the decision.",
            recruitment_status,
            recruitment_tone,
            recruitment_metric,
            "Recruitment Workspace",
        ),
        BriefingDomain(
            "organize",
            "Organization",
            "How healthy is our organization?",
            "Explore workforce structure, capabilities and organizational signals.",
            "Preview",
            "partial",
            "Organization data required for full diagnostics",
            "Organization Intelligence",
        ),
        BriefingDomain(
            "plan",
            "Workforce Planning",
            "Are we ready for tomorrow?",
            "Anticipate future roles, capacity and capability requirements.",
            "Data required",
            "locked",
            "Workforce history and scenarios required",
            None,
        ),
        BriefingDomain(
            "develop",
            "Succession",
            "Who is ready for critical roles?",
            "Identify critical positions, successors and development priorities.",
            "Data required",
            "locked",
            "Performance, potential and role data required",
            None,
        ),
        BriefingDomain(
            "connect",
            "Collaboration",
            "How effectively do teams collaborate?",
            "Use ONA surveys or collaboration metadata to reveal silos and connectors.",
            "ONA data required",
            "locked",
            "A staff list alone cannot support this analysis",
            "Organization Intelligence",
        ),
        BriefingDomain(
            "protect",
            "Talent Risks",
            "Where are our biggest people risks?",
            "Identify recruitment, succession and knowledge concentration risks.",
            "Planned",
            "partial",
            "Additional HR and organizational evidence required",
            None,
        ),
    )


def build_priorities(session: Any | None) -> tuple[BriefingPriority, ...]:
    snapshot = _session_snapshot(session)
    if not snapshot["has_recruitment"]:
        return (
            BriefingPriority("Start a recruitment diagnostic", "Upload a job description and candidate CVs to activate Recruitment Intelligence."),
            BriefingPriority("Organization diagnostics need evidence", "Import workforce or organizational data before drawing organization-wide conclusions.", "info"),
        )

    remaining = max(snapshot["candidate_count"] - snapshot["analyzed_count"], 0)
    priorities: list[BriefingPriority] = []
    if remaining:
        priorities.append(
            BriefingPriority(
                f"Complete the analysis for {snapshot['role_title']}",
                f"{remaining} candidate(s) still require analysis before a confident shortlist can be produced.",
            )
        )
    else:
        priorities.append(
            BriefingPriority(
                f"Decision ready for {snapshot['role_title']}",
                "Candidate analysis is available. Review evidence, risks and the recommended next action.",
                "success",
            )
        )
    priorities.append(
        BriefingPriority(
            "Keep conclusions aligned with available data",
            "Advanced organization, succession and ONA diagnostics remain gated until the required evidence is imported.",
            "info",
        )
    )
    return tuple(priorities)


def _styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        .tc-home-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1.2rem;padding:.65rem .15rem 1.05rem}
        .tc-home-kicker{font-size:.68rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#3457E5;margin-bottom:.3rem}
        .tc-home-head h1{margin:0;color:#14213D;font-size:clamp(1.65rem,2.6vw,2.25rem);letter-spacing:-.045em;line-height:1.08}
        .tc-home-head p{margin:.4rem 0 0;color:#5B6B82;font-size:.94rem}
        .tc-home-context{display:inline-flex;align-items:center;gap:.45rem;padding:.48rem .72rem;border-radius:999px;background:#FCFDFE;border:1px solid #DCE4F0;color:#53647C;font-size:.72rem;font-weight:760;box-shadow:0 5px 15px rgba(37,54,82,.045);white-space:nowrap}
        .tc-home-dot{width:8px;height:8px;border-radius:50%;background:#22C55E;box-shadow:0 0 0 4px rgba(34,197,94,.11)}
        .tc-home-stat{position:relative;overflow:hidden;padding:1rem 1.05rem;border:1px solid #DCE4F0;border-radius:17px;background:#FCFDFE;min-height:112px;box-shadow:0 7px 22px rgba(37,54,82,.055)}
        .tc-home-stat:after{content:"";position:absolute;width:82px;height:82px;border-radius:50%;right:-34px;top:-38px;background:var(--tc-stat-soft,#EEF2FF)}
        .tc-home-stat-icon{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--tc-stat-soft,#EEF2FF);color:var(--tc-stat,#3457E5);font-weight:900;font-size:1rem}
        .tc-home-stat-label{margin-top:.62rem;color:#5B6B82;font-size:.72rem;font-weight:720}
        .tc-home-stat-value{color:#14213D;font-size:1.55rem;font-weight:900;letter-spacing:-.045em;line-height:1.05;margin-top:.08rem}
        .tc-home-stat-note{color:#718198;font-size:.66rem;margin-top:.2rem}
        .tc-home-panel{height:100%;padding:1.05rem 1.12rem;border:1px solid #DCE4F0;border-radius:18px;background:#FCFDFE;box-shadow:0 8px 24px rgba(37,54,82,.055)}
        .tc-home-panel-head{display:flex;align-items:center;justify-content:space-between;gap:.8rem;margin-bottom:.8rem}
        .tc-home-panel-title{color:#14213D;font-weight:850;font-size:1rem}
        .tc-home-panel-meta{color:#3457E5;font-size:.68rem;font-weight:780}
        .tc-home-role{font-size:1.15rem;color:#14213D;font-weight:880;letter-spacing:-.025em}
        .tc-home-role-meta{color:#5B6B82;font-size:.76rem;margin-top:.2rem}
        .tc-home-progress{height:8px;border-radius:999px;background:#E8EDF6;overflow:hidden;margin:.9rem 0 .45rem}
        .tc-home-progress span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#3457E5,#5368E7 62%,#15B8CF)}
        .tc-home-progress-copy{display:flex;justify-content:space-between;color:#6B7B91;font-size:.69rem}
        .tc-home-priority{display:flex;gap:.72rem;padding:.72rem 0;border-bottom:1px solid #EDF1F7}
        .tc-home-priority:last-child{border-bottom:0}
        .tc-home-priority-icon{display:grid;place-items:center;width:30px;height:30px;flex:0 0 30px;border-radius:9px;background:#EEF2FF;color:#3457E5;font-weight:900}
        .tc-home-priority strong{display:block;color:#263750;font-size:.8rem;margin-bottom:.12rem}
        .tc-home-priority span{display:block;color:#6B7B91;font-size:.7rem;line-height:1.4}
        .tc-home-project{display:grid;grid-template-columns:minmax(180px,1.35fr) .72fr .72fr 1.15fr;gap:.8rem;align-items:center;padding:.74rem .15rem;border-bottom:1px solid #EDF1F7}
        .tc-home-project:last-child{border-bottom:0}
        .tc-home-project-name{font-size:.79rem;color:#25364D;font-weight:820}
        .tc-home-project-sub{font-size:.65rem;color:#7A899D;margin-top:.12rem}
        .tc-home-project-value{font-size:.72rem;color:#53647C}
        .tc-home-mini-track{height:6px;border-radius:999px;background:#E8EDF6;overflow:hidden}
        .tc-home-mini-track span{display:block;height:100%;background:linear-gradient(90deg,#3457E5,#7456E8);border-radius:999px}
        .tc-brief-card{padding:1rem 1.05rem;border:1px solid #DCE4F0;border-radius:17px;background:#FCFDFE;min-height:198px;box-shadow:0 7px 22px rgba(37,54,82,.05)}
        .tc-brief-card h3{font-size:1.05rem;margin:.5rem 0 .28rem;color:#14213D}
        .tc-brief-question{font-weight:760;color:#34465F;margin-bottom:.5rem;font-size:.82rem}
        .tc-brief-copy{color:#6B7B91;font-size:.78rem;line-height:1.45;min-height:58px}
        .tc-brief-meta{font-size:.68rem;color:#718198;margin-top:.62rem;padding-top:.58rem;border-top:1px solid #EDF1F7}
        .tc-brief-status{display:inline-block;border-radius:999px;padding:.22rem .52rem;font-size:.64rem;font-weight:850;letter-spacing:.02em}
        .tc-ready{background:#DCFCE7;color:#166534}.tc-attention{background:#FEF3C7;color:#92400E}.tc-partial{background:#EDE9FE;color:#5B21B6}.tc-locked{background:#EDF1F7;color:#52647D}
        .tc-ai-brief{padding:.95rem 1.05rem;border-radius:16px;background:linear-gradient(135deg,#F9FAFF,#F1F5FF);border:1px solid #DCE3F3;margin:.75rem 0 1rem}
        .tc-ai-brief strong{color:#3457E5}.tc-ai-brief p{margin:.32rem 0 0;color:#53647C;font-size:.8rem}
        .tc-zero-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:2rem;align-items:center;padding:2rem 2.1rem;border:1px solid #D9E3F0;border-radius:24px;background:linear-gradient(135deg,#FCFDFE 0%,#F4F6FF 54%,#EEF9FC 100%);box-shadow:0 18px 46px rgba(37,54,82,.09);margin:.1rem 0 1.25rem}
        .tc-zero-hero:after{content:"";position:absolute;right:-90px;top:-110px;width:310px;height:310px;border-radius:50%;background:radial-gradient(circle,rgba(52,87,229,.16),rgba(21,184,207,.04) 58%,transparent 70%)}
        .tc-zero-copy{position:relative;z-index:2}.tc-zero-kicker{display:inline-flex;align-items:center;gap:.45rem;padding:.3rem .62rem;border-radius:999px;color:#3457E5;background:#EEF2FF;border:1px solid #D9DFFC;font-size:.68rem;font-weight:850;letter-spacing:.06em;text-transform:uppercase}
        .tc-zero-title{margin:.75rem 0 .45rem;color:#14213D;font-size:clamp(1.8rem,3.5vw,2.65rem);font-weight:900;letter-spacing:-.055em;line-height:1.04}.tc-zero-body{max-width:690px;color:#5B6B82;font-size:.98rem;line-height:1.58}
        .tc-zero-steps{position:relative;z-index:2;padding:1rem 1.05rem;border:1px solid rgba(204,216,234,.9);border-radius:18px;background:rgba(252,253,254,.82);backdrop-filter:blur(14px);box-shadow:0 10px 26px rgba(37,54,82,.07)}
        .tc-zero-step{display:flex;gap:.72rem;align-items:flex-start;padding:.68rem 0;border-bottom:1px solid #E9EEF6}.tc-zero-step:last-child{border-bottom:0}.tc-zero-step-num{display:grid;place-items:center;width:28px;height:28px;flex:0 0 28px;border-radius:9px;background:#E8EDFF;color:#3457E5;font-size:.72rem;font-weight:900}.tc-zero-step strong{display:block;color:#263750;font-size:.78rem}.tc-zero-step span{display:block;color:#738198;font-size:.68rem;line-height:1.4;margin-top:.08rem}
        .tc-zero-section-head{display:flex;align-items:end;justify-content:space-between;gap:1rem;margin:1.4rem 0 .75rem}.tc-zero-section-head h2{margin:0;color:#14213D;font-size:1.35rem}.tc-zero-section-head p{margin:0;color:#6B7B91;font-size:.78rem}
        @media(max-width:920px){.tc-zero-hero{grid-template-columns:1fr}.tc-zero-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem}.tc-zero-step{border:0;padding:.25rem}.tc-home-head{display:block}.tc-home-context{margin-top:.7rem}}
        @media(max-width:680px){.tc-zero-hero{padding:1.35rem}.tc-zero-steps{grid-template-columns:1fr}.tc-home-project{grid-template-columns:1fr 1fr}.tc-home-project>div:last-child{grid-column:1/-1}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_domain(domain: BriefingDomain, index: int) -> None:
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-brief-card">
          <span class="tc-brief-status tc-{escape(domain.status_tone)}">{escape(domain.status)}</span>
          <h3>{escape(domain.title)}</h3>
          <div class="tc-brief-question">{escape(domain.question)}</div>
          <div class="tc-brief-copy">{escape(domain.description)}</div>
          <div class="tc-brief-meta">{escape(domain.metric)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    button_label = "Open workspace" if domain.target_page else "Data requirements"
    if st.button(button_label, key=f"briefing_domain_{domain.key}_{index}", use_container_width=True):
        if domain.target_page:
            request_page(domain.target_page, reason=f"Opened from {domain.title} diagnostic.")
            st.rerun()
        else:
            st.session_state[f"briefing_requirements_{domain.key}"] = True
    if st.session_state.get(f"briefing_requirements_{domain.key}"):
        st.info(domain.metric)


def _render_priorities(priorities: Iterable[BriefingPriority]) -> None:
    import streamlit as st

    tone_icons = {"attention": "!", "success": "✓", "info": "i"}
    items = []
    for priority in priorities:
        icon = tone_icons.get(priority.tone, "•")
        items.append(
            f'<div class="tc-home-priority"><div class="tc-home-priority-icon">{escape(icon)}</div>'
            f'<div><strong>{escape(priority.title)}</strong><span>{escape(priority.detail)}</span></div></div>'
        )
    body = "".join(items)
    st.markdown(
        '<div class="tc-home-panel"><div class="tc-home-panel-head">'
        '<div class="tc-home-panel-title">Today’s priorities</div>'
        '<div class="tc-home-panel-meta">AI-guided</div></div>'
        + body
        + '</div>',
        unsafe_allow_html=True,
    )


def _render_mission_canvas(canvas: MissionCanvas) -> None:
    import streamlit as st

    st.markdown("### Mission Canvas")
    c1, c2, c3 = st.columns([1.35, 1, 1])
    c1.metric("Mission", canvas.mission_title, canvas.domain.value.replace("_", " ").title())
    c2.metric("Routing confidence", canvas.confidence, "Business-language interpretation")
    c3.metric("Workflow", f"{len(canvas.recommended_workflow)} steps", "AI-guided")

    st.markdown(
        '<div class="tc-ai-brief"><strong>Objective</strong><p>'
        + escape(canvas.objective)
        + '</p></div>',
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns(3)
    with left:
        st.markdown("**Context understood**")
        st.write(canvas.context)
        if canvas.constraints:
            st.markdown("**Detected constraints**")
            for item in canvas.constraints:
                st.write(f"• {item}")
        else:
            st.caption("No explicit constraint detected yet.")

    with middle:
        st.markdown("**Evidence to provide**")
        for item in canvas.required_inputs:
            st.write(f"• {item}")

    with right:
        st.markdown("**Success criteria**")
        for item in canvas.success_criteria:
            st.write(f"• {item}")

    st.markdown("**Recommended workflow**")
    for index, step in enumerate(canvas.recommended_workflow, start=1):
        st.write(f"{index}. {step}")

    st.caption(canvas.limitation)
    if canvas.target_page:
        if st.button(
            f"Continue to {canvas.mission_title}",
            key=f"mission_canvas_continue_{canvas.domain.value}",
            type="primary",
        ):
            request_page(canvas.target_page, reason=f"Mission routed to {canvas.mission_title}.")
            st.rerun()
    else:
        st.info(
            "This mission is recognized, but its full Studio is not enabled yet. "
            "The required evidence and workflow are shown above without fabricating an analysis."
        )


def _render_mission_prompt(session: Any | None) -> None:
    import streamlit as st

    with st.expander("Describe a new mission", expanded=False):
        st.caption(
            "Start with the business outcome. TalentCopilot will route the mission, "
            "identify the minimum useful evidence and propose the workflow."
        )
        prompt = st.text_area(
            "What are you trying to accomplish?",
            placeholder=(
                "Example: We need to recruit a Global HRIS Director within three months. "
                "International transformation experience is mandatory."
            ),
            label_visibility="collapsed",
            height=120,
            key="enterprise_mission_prompt",
        )

        analyse_clicked = st.button(
            "Understand my mission",
            key="enterprise_mission_analyse",
            type="primary",
            disabled=not bool(prompt.strip()),
        )
        if analyse_clicked:
            st.session_state["enterprise_mission_canvas"] = understand_mission(prompt)

        canvas = st.session_state.get("enterprise_mission_canvas")
        if isinstance(canvas, MissionCanvas):
            _render_mission_canvas(canvas)
            render_mission_workspace(canvas, session)


def _render_zero_state(domains: tuple[BriefingDomain, ...], session: Any | None) -> None:
    import streamlit as st

    st.markdown(
        '<div class="tc-zero-hero"><div class="tc-zero-copy">'
        '<div class="tc-zero-kicker">✦ Evidence-grounded talent decisions</div>'
        '<div class="tc-zero-title">Turn recruitment evidence into confident decisions.</div>'
        '<div class="tc-zero-body">Create a recruitment mission, upload the job description and candidate CVs, '
        'then move from a transparent candidate perspective to structured interviews and a traceable final decision.</div>'
        '</div><div class="tc-zero-steps">'
        '<div class="tc-zero-step"><div class="tc-zero-step-num">1</div><div><strong>Create the mission</strong><span>Define the role and decision context.</span></div></div>'
        '<div class="tc-zero-step"><div class="tc-zero-step-num">2</div><div><strong>Add evidence</strong><span>Upload the job description and candidate CVs.</span></div></div>'
        '<div class="tc-zero-step"><div class="tc-zero-step-num">3</div><div><strong>Review and decide</strong><span>Compare grounded insights without opaque scoring.</span></div></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    action_col, spacer = st.columns([1.05, 2.95])
    with action_col:
        if st.button(
            "Start recruitment mission",
            icon=":material/add_circle:",
            type="primary",
            key="home_zero_start_recruitment",
            use_container_width=True,
        ):
            request_page("Recruitment Overview", reason="Started a recruitment mission from the premium onboarding.")
            st.rerun()

    st.markdown(
        '<div class="tc-zero-section-head"><div><h2>Choose a diagnostic</h2>'
        '<p>Start with the business question; TalentCopilot will request only the evidence required.</p></div></div>',
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    for index, (column, domain) in enumerate(zip(columns, domains[:3])):
        with column:
            _render_domain(domain, index)

    st.markdown(
        '<div class="tc-ai-brief"><strong>Today’s AI brief</strong><p>'
        'No mission is active. Recruitment Intelligence is ready to start; organization and workforce diagnostics remain '
        'evidence-gated until their required datasets are available.</p></div>',
        unsafe_allow_html=True,
    )
    _render_mission_prompt(session)


def render_executive_briefing() -> None:
    import streamlit as st

    _styles()
    session = get_streamlit_session()
    snapshot = _session_snapshot(session)
    domains = build_briefing_domains(session)
    priorities = build_priorities(session)

    try:
        projects = list(build_project_summaries(session, list_recruitments()))
    except Exception:
        projects = list(build_project_summaries(session, ()))

    if not snapshot["has_recruitment"] and not projects:
        _render_zero_state(domains, session)
        return

    active_label = snapshot["role_title"] if snapshot["has_recruitment"] else "No active mission"
    st.markdown(
        f'<div class="tc-home-head"><div><div class="tc-home-kicker">Talent intelligence workspace</div>'
        f'<h1>Welcome back</h1><p>See what matters now, then continue directly to the next evidence-led decision.</p></div>'
        f'<div class="tc-home-context"><span class="tc-home-dot"></span>{escape(active_label)}</div></div>',
        unsafe_allow_html=True,
    )

    total_candidates = sum(project.candidate_count for project in projects)
    total_analyzed = sum(project.analyzed_count for project in projects)
    decision_ready = sum(
        1 for project in projects
        if project.candidate_count > 0 and project.analyzed_count >= project.candidate_count
    )
    stat_items = (
        ("▦", "Active missions", str(len(projects)), "Active and saved workspaces", "#EEF2FF", "#3457E5"),
        ("◇", "Candidates", str(total_candidates), "Across current recruitments", "#ECFEFF", "#16889A"),
        ("✓", "Analysed", str(total_analyzed), "Official analyses available", "#ECFDF5", "#15803D"),
        ("✦", "Decision ready", str(decision_ready), "Missions ready for review", "#F5F3FF", "#7456E8"),
    )
    columns = st.columns(4)
    for column, (icon, label, value, note, soft, tone) in zip(columns, stat_items):
        with column:
            st.markdown(
                f'<div class="tc-home-stat" style="--tc-stat-soft:{soft};--tc-stat:{tone}">'
                f'<div class="tc-home-stat-icon">{escape(icon)}</div>'
                f'<div class="tc-home-stat-label">{escape(label)}</div>'
                f'<div class="tc-home-stat-value">{escape(value)}</div>'
                f'<div class="tc-home-stat-note">{escape(note)}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.25, .85])
    with left:
        candidate_count = snapshot["candidate_count"]
        analyzed_count = snapshot["analyzed_count"]
        progress = round(analyzed_count / candidate_count * 100) if candidate_count else 0
        st.markdown(
            f'<div class="tc-home-panel"><div class="tc-home-panel-head">'
            f'<div class="tc-home-panel-title">Active recruitment</div><div class="tc-home-panel-meta">Current mission</div></div>'
            f'<div class="tc-home-role">{escape(snapshot["role_title"])}</div>'
            f'<div class="tc-home-role-meta">{analyzed_count}/{candidate_count} candidates analysed</div>'
            f'<div class="tc-home-progress"><span style="width:{progress}%"></span></div>'
            f'<div class="tc-home-progress-copy"><span>Analysis progress</span><strong>{progress}%</strong></div></div>',
            unsafe_allow_html=True,
        )
        if snapshot["has_recruitment"]:
            if st.button("Continue active recruitment", type="primary", key="home_continue_active_recruitment", use_container_width=True):
                request_page("Recruitment Overview", reason="Continued the active recruitment from Home.")
                st.rerun()
        else:
            if st.button("Start a recruitment mission", type="primary", key="home_start_recruitment", use_container_width=True):
                request_page("Recruitment Overview", reason="Started a recruitment mission from Home.")
                st.rerun()

    with right:
        _render_priorities(priorities)

    st.markdown("### Active projects")
    if projects:
        project_rows = []
        for project in projects[:5]:
            progress = project.progress_percent
            project_rows.append(
                f'<div class="tc-home-project"><div><div class="tc-home-project-name">{escape(project.title)}</div>'
                f'<div class="tc-home-project-sub">{escape(project.status)} · {escape(project.next_action)}</div></div>'
                f'<div class="tc-home-project-value">{project.candidate_count} candidates</div>'
                f'<div class="tc-home-project-value">{project.analyzed_count} analysed</div>'
                f'<div><div class="tc-home-mini-track"><span style="width:{progress}%"></span></div>'
                f'<div class="tc-home-project-sub">{progress}% complete</div></div></div>'
            )
        st.markdown('<div class="tc-home-panel">' + "".join(project_rows) + '</div>', unsafe_allow_html=True)
        if st.button("View all projects", key="briefing_view_projects"):
            request_page("Projects", reason="Opened the Project Hub from the Executive Brief.")
            st.rerun()
    else:
        st.caption("No project yet. Start with Recruitment Intelligence to create your first decision project.")

    if snapshot["has_recruitment"]:
        brief = (
            f"The active recruitment is <strong>{escape(snapshot['role_title'])}</strong>. "
            f"{snapshot['analyzed_count']} of {snapshot['candidate_count']} candidates have been analysed. "
            "Recruitment Intelligence is available now; broader diagnostics remain data-gated."
        )
    else:
        brief = (
            "No recruitment is active yet. Recruitment Intelligence can be activated with a job description and candidate CVs. "
            "Other diagnostics unlock only when their required organizational evidence is available."
        )
    st.markdown(f'<div class="tc-ai-brief"><strong>Today’s AI brief</strong><p>{brief}</p></div>', unsafe_allow_html=True)

    st.markdown("### Choose a diagnostic")
    for row_start in range(0, len(domains), 3):
        row = domains[row_start:row_start + 3]
        columns = st.columns(3)
        for offset, (column, domain) in enumerate(zip(columns, row)):
            with column:
                _render_domain(domain, row_start + offset)

    _render_mission_prompt(session)



def render_home() -> None:
    """Compatibility entry point used by the current navigation registry."""
    render_executive_briefing()
