from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Iterable

from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.navigation_actions import request_page
from talentcopilot.ui.project_hub import build_project_summaries
from talentcopilot.storage.recruitment_store import list_recruitments


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
        .tc-brief-hero{padding:2.1rem 2.25rem;border-radius:26px;background:linear-gradient(135deg,#0f172a 0%,#172554 52%,#312e81 100%);color:#fff;margin-bottom:1.35rem;box-shadow:0 20px 50px rgba(15,23,42,.18)}
        .tc-brief-kicker{font-size:.78rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;color:#c7d2fe;margin-bottom:.7rem}
        .tc-brief-hero h1{font-size:2.55rem;letter-spacing:-.045em;line-height:1.05;margin:0 0 .7rem}
        .tc-brief-hero p{font-size:1.04rem;color:#e0e7ff;max-width:820px;margin:0}
        .tc-brief-card{padding:1.15rem 1.2rem;border:1px solid #e2e8f0;border-radius:19px;background:#fff;min-height:210px;box-shadow:0 8px 28px rgba(15,23,42,.055)}
        .tc-brief-card h3{font-size:1.13rem;margin:.55rem 0 .3rem;color:#0f172a}
        .tc-brief-question{font-weight:750;color:#334155;margin-bottom:.55rem}
        .tc-brief-copy{color:#64748b;font-size:.91rem;line-height:1.45;min-height:64px}
        .tc-brief-meta{font-size:.8rem;color:#64748b;margin-top:.7rem;padding-top:.65rem;border-top:1px solid #f1f5f9}
        .tc-brief-status{display:inline-block;border-radius:999px;padding:.25rem .58rem;font-size:.72rem;font-weight:850;letter-spacing:.02em}
        .tc-ready{background:#dcfce7;color:#166534}.tc-attention{background:#fef3c7;color:#92400e}.tc-partial{background:#ede9fe;color:#5b21b6}.tc-locked{background:#f1f5f9;color:#475569}
        .tc-priority{padding:1rem 1.1rem;border-radius:16px;border:1px solid #e2e8f0;background:#fff;margin-bottom:.65rem}
        .tc-priority strong{display:block;color:#0f172a;margin-bottom:.25rem}.tc-priority span{color:#64748b;font-size:.9rem}
        .tc-ai-brief{padding:1.25rem 1.3rem;border-radius:19px;background:#f8fafc;border:1px solid #dbeafe;margin-bottom:1rem}
        .tc-ai-brief strong{color:#3730a3}.tc-ai-brief p{margin:.4rem 0 0;color:#475569}
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

    tone_icons = {"attention": "⚠", "success": "✓", "info": "•"}
    for priority in priorities:
        icon = tone_icons.get(priority.tone, "•")
        st.markdown(
            f'<div class="tc-priority"><strong>{icon} {escape(priority.title)}</strong><span>{escape(priority.detail)}</span></div>',
            unsafe_allow_html=True,
        )


def render_executive_briefing() -> None:
    import streamlit as st

    _styles()
    session = get_streamlit_session()
    snapshot = _session_snapshot(session)
    domains = build_briefing_domains(session)
    priorities = build_priorities(session)

    st.markdown(
        """
        <div class="tc-brief-hero">
          <div class="tc-brief-kicker">TalentCopilot · AI Talent Intelligence Platform</div>
          <h1>What would you like to diagnose today?</h1>
          <p>Start with a real HR question. TalentCopilot checks whether the available evidence is sufficient, then guides you toward a clear and explainable decision.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if snapshot["has_recruitment"]:
        brief = (
            f"The active recruitment is <strong>{escape(snapshot['role_title'])}</strong>. "
            f"{snapshot['analyzed_count']} of {snapshot['candidate_count']} candidates have been analysed. "
            "Recruitment Intelligence is available now; broader diagnostics remain data-gated."
        )
    else:
        brief = (
            "No recruitment is active yet. Recruitment Intelligence can be activated with a job description and candidate CVs. "
            "Other diagnostics will unlock only when their required organizational evidence is available."
        )
    st.markdown(f'<div class="tc-ai-brief"><strong>Today’s AI brief</strong><p>{brief}</p></div>', unsafe_allow_html=True)

    st.subheader("Today’s priorities")
    _render_priorities(priorities)

    st.subheader("Choose a diagnostic")
    for row_start in range(0, len(domains), 3):
        row = domains[row_start:row_start + 3]
        columns = st.columns(3)
        for offset, (column, domain) in enumerate(zip(columns, row)):
            with column:
                _render_domain(domain, row_start + offset)

    st.subheader("Recent projects")
    try:
        projects = build_project_summaries(session, list_recruitments())[:4]
    except Exception:
        projects = build_project_summaries(session, ())[:4]
    if projects:
        project_columns = st.columns(min(4, len(projects)))
        for column, project in zip(project_columns, projects):
            with column:
                st.markdown(
                    f'<div class="tc-priority"><strong>{escape(project.title)}</strong><span>{project.analyzed_count}/{project.candidate_count} analysed · {escape(project.next_action)}</span></div>',
                    unsafe_allow_html=True,
                )
        if st.button("View all projects", key="briefing_view_projects"):
            request_page("Projects", reason="Opened the Project Hub from the Executive Brief.")
            st.rerun()
    else:
        st.caption("No project yet. Start with Recruitment Intelligence to create your first decision project.")

    st.subheader("Ask TalentCopilot")
    prompt = st.text_input(
        "Describe the HR decision you need to make",
        placeholder="Example: Who are the strongest candidates for this role, and what should I verify before interviewing them?",
        label_visibility="collapsed",
    )
    if prompt:
        lowered = prompt.lower()
        if any(term in lowered for term in ("candidate", "recruit", "hire", "interview", "cv")):
            st.success("This question belongs to Recruitment Intelligence.")
            if st.button("Open Recruitment Workspace", key="briefing_prompt_recruitment"):
                request_page("Recruitment Workspace", reason="TalentCopilot routed your question to Recruitment Intelligence.")
                st.rerun()
        elif any(term in lowered for term in ("collaboration", "silo", "department", "organization", "ona")):
            st.info("This question belongs to Organization or Collaboration Intelligence. TalentCopilot will verify data readiness before analysis.")
            if st.button("Open Organization Intelligence", key="briefing_prompt_organization"):
                request_page("Organization Intelligence", reason="TalentCopilot routed your question to Organization Intelligence.")
                st.rerun()
        else:
            st.info("TalentCopilot needs a little more context to route this decision. Mention the role, team, workforce question or risk you want to diagnose.")


def render_home() -> None:
    """Compatibility entry point used by the current navigation registry."""
    render_executive_briefing()
