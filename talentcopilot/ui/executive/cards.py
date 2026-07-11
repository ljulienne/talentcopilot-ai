from __future__ import annotations

from html import escape
from typing import Iterable

from .theme import THEME


TONE_COLORS = {
    "primary": THEME.primary,
    "ai": THEME.ai,
    "success": THEME.success,
    "warning": THEME.warning,
    "danger": THEME.danger,
    "neutral": THEME.muted,
}


def normalize_percent(value: float | int) -> int:
    numeric = float(value)
    if 0 <= numeric <= 1:
        numeric *= 100
    return max(0, min(100, round(numeric)))


def tone_color(tone: str) -> str:
    return TONE_COLORS.get((tone or "").lower(), THEME.primary)


def render_metric_card(
    label: str,
    value: str | int | float,
    *,
    detail: str = "",
    tone: str = "primary",
) -> None:
    import streamlit as st

    color = tone_color(tone)
    st.markdown(
        f"""
        <div class="tc-exec-card" style="border-top:3px solid {color};">
          <div class="tc-exec-label">{escape(str(label))}</div>
          <div class="tc-exec-value">{escape(str(value))}</div>
          <div class="tc-exec-body">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_health_card(
    score: float | int,
    *,
    label: str = "Executive health",
    status: str | None = None,
) -> None:
    import streamlit as st

    percent = normalize_percent(score)
    if status is None:
        status = "Strong" if percent >= 80 else "Watch" if percent >= 60 else "At risk"
    tone = "success" if percent >= 80 else "warning" if percent >= 60 else "danger"
    color = tone_color(tone)

    st.markdown(
        f"""
        <div class="tc-exec-card">
          <div class="tc-exec-label">{escape(label)}</div>
          <div class="tc-exec-value">{percent} / 100</div>
          <span class="tc-exec-badge" style="color:{color};background:{color}14;">{escape(status)}</span>
          <div class="tc-exec-progress"><span style="width:{percent}%;background:{color};"></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_confidence_card(confidence: float | int, *, detail: str = "") -> None:
    percent = normalize_percent(confidence)
    tone = "success" if percent >= 80 else "warning" if percent >= 60 else "danger"
    render_metric_card("Confidence", f"{percent}%", detail=detail, tone=tone)


def render_priority_card(
    title: str,
    *,
    priority: str = "Medium",
    body: str = "",
) -> None:
    priority_key = priority.strip().lower()
    tone = "danger" if priority_key in {"critical", "high"} else "warning" if priority_key == "medium" else "success"
    render_metric_card(priority, title, detail=body, tone=tone)


def render_evidence_card(title: str, evidence: Iterable[str], *, tone: str = "ai") -> None:
    import streamlit as st

    items = [str(item) for item in evidence if str(item).strip()]
    color = tone_color(tone)
    body = "".join(f"<li>{escape(item)}</li>" for item in items) or "<li>No evidence available.</li>"
    st.markdown(
        f"""
        <div class="tc-exec-card" style="border-left:4px solid {color};">
          <div class="tc-exec-label">Evidence</div>
          <div style="font-weight:850;margin-top:.25rem;">{escape(title)}</div>
          <ul class="tc-exec-body">{body}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(
    action: str,
    *,
    impact: str = "Medium",
    rationale: str = "",
) -> None:
    render_metric_card(
        "Recommended action",
        action,
        detail=f"Impact: {impact}. {rationale}".strip(),
        tone="ai",
    )
