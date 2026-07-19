"""Reusable Enterprise Workspace Engine for TalentCopilot.

Release 6.0B.2.2 provides a presentation-only shell shared by future
candidate, interview, decision and reporting workspaces.

It deliberately contains no matching, ranking, decision or AI business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import Callable, Optional, Sequence, Tuple


@dataclass(frozen=True)
class WorkspaceMetric:
    label: str
    value: str
    detail: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class WorkspaceStatusStep:
    label: str
    complete: bool = False
    current: bool = False


@dataclass(frozen=True)
class WorkspaceCard:
    title: str
    body: str
    eyebrow: str = ""
    tone: str = "neutral"
    footer: str = ""


@dataclass(frozen=True)
class WorkspaceAction:
    label: str
    key: str
    help_text: str = ""
    primary: bool = False
    disabled: bool = False


@dataclass(frozen=True)
class WorkspaceSection:
    key: str
    title: str
    question: str = ""
    description: str = ""
    expanded: bool = False
    renderer: Optional[Callable[[], None]] = None


@dataclass(frozen=True)
class EnterpriseWorkspaceModel:
    title: str
    eyebrow: str
    subtitle: str = ""
    status: str = ""
    readiness: Optional[int] = None
    summary: str = ""
    metrics: Tuple[WorkspaceMetric, ...] = field(default_factory=tuple)
    steps: Tuple[WorkspaceStatusStep, ...] = field(default_factory=tuple)
    insights: Tuple[WorkspaceCard, ...] = field(default_factory=tuple)
    recommendations: Tuple[WorkspaceCard, ...] = field(default_factory=tuple)
    evidence: Tuple[WorkspaceCard, ...] = field(default_factory=tuple)
    actions: Tuple[WorkspaceAction, ...] = field(default_factory=tuple)
    sections: Tuple[WorkspaceSection, ...] = field(default_factory=tuple)


def clamp_readiness(value: Optional[int]) -> Optional[int]:
    """Normalize readiness for safe Streamlit progress rendering."""
    if value is None:
        return None
    return max(0, min(100, int(value)))


def _tone(value: str) -> str:
    normalized = str(value or "neutral").strip().lower()
    allowed = {"neutral", "positive", "warning", "risk", "info"}
    return normalized if normalized in allowed else "neutral"


def _styles() -> str:
    return """
    <style>
    .tc-ew-hero{padding:1.45rem 1.55rem;border:1px solid #dbe4f0;border-radius:24px;background:linear-gradient(135deg,#fff 0%,#f7f8ff 100%);box-shadow:0 16px 44px rgba(15,23,42,.07)}
    .tc-ew-kicker{font-size:.72rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#4f46e5}
    .tc-ew-title{font-size:1.75rem;font-weight:850;color:#0f172a;margin:.28rem 0}
    .tc-ew-subtitle{font-size:.92rem;color:#64748b;line-height:1.5}
    .tc-ew-meta{display:flex;gap:.55rem;flex-wrap:wrap;margin-top:.8rem}
    .tc-ew-pill{border-radius:999px;padding:.34rem .68rem;font-size:.76rem;font-weight:800;background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe}
    .tc-ew-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.75rem;margin:1rem 0}
    .tc-ew-metric,.tc-ew-card{padding:1rem 1.05rem;border:1px solid #e2e8f0;border-radius:18px;background:#fff}
    .tc-ew-label{font-size:.76rem;font-weight:800;color:#64748b;text-transform:uppercase;letter-spacing:.06em}
    .tc-ew-value{font-size:1.38rem;font-weight:850;color:#0f172a;margin:.28rem 0}
    .tc-ew-detail,.tc-ew-body,.tc-ew-footer{font-size:.82rem;color:#64748b;line-height:1.5}
    .tc-ew-summary{padding:1rem 1.1rem;border-radius:18px;background:#eef2ff;border:1px solid #c7d2fe;color:#312e81;line-height:1.55;margin:1rem 0}
    .tc-ew-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.55rem;margin:1rem 0}
    .tc-ew-step{padding:.72rem .8rem;border:1px solid #e2e8f0;border-radius:14px;background:#fff;font-size:.8rem;color:#64748b}
    .tc-ew-step.done{background:#ecfdf5;border-color:#a7f3d0;color:#065f46}
    .tc-ew-step.current{background:#eef2ff;border-color:#c7d2fe;color:#3730a3;font-weight:800}
    .tc-ew-card{margin:.65rem 0}
    .tc-ew-card.positive{border-color:#bbf7d0;background:#f0fdf4}
    .tc-ew-card.warning{border-color:#fde68a;background:#fffbeb}
    .tc-ew-card.risk{border-color:#fecaca;background:#fef2f2}
    .tc-ew-card.info{border-color:#bae6fd;background:#f0f9ff}
    @media (max-width:760px){.tc-ew-hero{padding:1.15rem}.tc-ew-title{font-size:1.45rem}}
    </style>
    """


def render_workspace_header(model: EnterpriseWorkspaceModel) -> None:
    import streamlit as st

    readiness = clamp_readiness(model.readiness)
    pills = []
    if model.status:
        pills.append(f'<span class="tc-ew-pill">{escape(model.status)}</span>')
    if readiness is not None:
        pills.append(f'<span class="tc-ew-pill">Readiness {readiness}%</span>')

    st.markdown(
        _styles()
        + f'<div class="tc-ew-hero">'
          f'<div class="tc-ew-kicker">{escape(model.eyebrow)}</div>'
          f'<div class="tc-ew-title">{escape(model.title)}</div>'
          f'<div class="tc-ew-subtitle">{escape(model.subtitle)}</div>'
          f'<div class="tc-ew-meta">{"".join(pills)}</div>'
          f'</div>',
        unsafe_allow_html=True,
    )
    if readiness is not None:
        st.progress(readiness / 100)


def render_workspace_metrics(metrics: Sequence[WorkspaceMetric]) -> None:
    import streamlit as st

    if not metrics:
        return
    html = "".join(
        f'<div class="tc-ew-metric">'
        f'<div class="tc-ew-label">{escape(metric.label)}</div>'
        f'<div class="tc-ew-value">{escape(str(metric.value))}</div>'
        f'<div class="tc-ew-detail">{escape(metric.detail)}</div>'
        f'</div>'
        for metric in metrics
    )
    st.markdown(f'<div class="tc-ew-grid">{html}</div>', unsafe_allow_html=True)


def render_workspace_steps(steps: Sequence[WorkspaceStatusStep]) -> None:
    import streamlit as st

    if not steps:
        return
    html = []
    for step in steps:
        css_class = "done" if step.complete else "current" if step.current else ""
        symbol = "✓" if step.complete else "●" if step.current else "○"
        html.append(
            f'<div class="tc-ew-step {css_class}">{symbol} {escape(step.label)}</div>'
        )
    st.markdown(f'<div class="tc-ew-steps">{"".join(html)}</div>', unsafe_allow_html=True)


def render_workspace_cards(title: str, cards: Sequence[WorkspaceCard]) -> None:
    import streamlit as st

    if not cards:
        return
    st.markdown(f"### {title}")
    for card in cards:
        st.markdown(
            f'<div class="tc-ew-card {_tone(card.tone)}">'
            f'<div class="tc-ew-label">{escape(card.eyebrow)}</div>'
            f'<div class="tc-ew-value" style="font-size:1rem">{escape(card.title)}</div>'
            f'<div class="tc-ew-body">{escape(card.body)}</div>'
            f'<div class="tc-ew-footer">{escape(card.footer)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_workspace_actions(
    actions: Sequence[WorkspaceAction],
    on_action: Optional[Callable[[str], None]] = None,
) -> None:
    import streamlit as st

    if not actions:
        return
    st.markdown("### Recommended actions")
    columns = st.columns(min(3, max(1, len(actions))))
    for index, action in enumerate(actions):
        with columns[index % len(columns)]:
            clicked = st.button(
                action.label,
                key=action.key,
                type="primary" if action.primary else "secondary",
                disabled=action.disabled,
                help=action.help_text or None,
                use_container_width=True,
            )
            if clicked and on_action is not None:
                on_action(action.key)


def render_enterprise_workspace(
    model: EnterpriseWorkspaceModel,
    *,
    on_action: Optional[Callable[[str], None]] = None,
) -> None:
    """Render a complete enterprise workspace from presentation-only state."""
    import streamlit as st

    render_workspace_header(model)
    render_workspace_steps(model.steps)
    render_workspace_metrics(model.metrics)

    if model.summary:
        st.markdown(
            f'<div class="tc-ew-summary"><strong>Executive summary</strong><br>'
            f'{escape(model.summary)}</div>',
            unsafe_allow_html=True,
        )

    render_workspace_cards("Key insights", model.insights)
    render_workspace_cards("Recommendations", model.recommendations)
    render_workspace_cards("Evidence", model.evidence)
    render_workspace_actions(model.actions, on_action)

    if model.sections:
        st.markdown("### Detailed workspace")
        for section in model.sections:
            label = section.title
            if section.question:
                label = f"{label} — {section.question}"
            with st.expander(label, expanded=section.expanded):
                if section.description:
                    st.caption(section.description)
                if section.renderer:
                    section.renderer()


__all__ = [
    "EnterpriseWorkspaceModel",
    "WorkspaceAction",
    "WorkspaceCard",
    "WorkspaceMetric",
    "WorkspaceSection",
    "WorkspaceStatusStep",
    "clamp_readiness",
    "render_enterprise_workspace",
    "render_workspace_actions",
    "render_workspace_cards",
    "render_workspace_header",
    "render_workspace_metrics",
    "render_workspace_steps",
]
