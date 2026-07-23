from __future__ import annotations

from html import escape
from typing import Iterable, Tuple


_TONES = {
    "primary": ("#3730A3", "#EEF2FF", "#C7D2FE", "●"),
    "ai": ("#6D28D9", "#F5F3FF", "#DDD6FE", "✦"),
    "success": ("#166534", "#F0FDF4", "#BBF7D0", "✓"),
    "warning": ("#92400E", "#FFFBEB", "#FDE68A", "!"),
    "danger": ("#991B1B", "#FEF2F2", "#FECACA", "!"),
    "info": ("#075985", "#F0F9FF", "#BAE6FD", "i"),
    "neutral": ("#475569", "#F8FAFC", "#E2E8F0", "○"),
    "muted": ("#64748B", "#F8FAFC", "#E2E8F0", "—"),
}


def enterprise_hero(title: str, subtitle: str, badge: str = "TalentCopilot Enterprise"):
    import streamlit as st
    st.markdown(
        f'''<div class="tc-hero"><div class="tc-badge">{escape(str(badge))}</div>'''
        f'''<h1>{escape(str(title))}</h1><p>{escape(str(subtitle))}</p></div>''',
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(
        f'<div class="tc-section-title">{escape(str(title))}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="tc-section-subtitle">{escape(str(subtitle))}</div>',
            unsafe_allow_html=True,
        )


def metric_grid(metrics: Iterable[Tuple[str, str, str]]):
    import streamlit as st
    metrics = list(metrics)
    cols = st.columns(len(metrics) if metrics else 1)
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta)


def insight_card(title: str, body: str, badge: str = "AI Insight"):
    import streamlit as st
    st.markdown(
        f'''<div class="tc-insight"><div class="tc-status" style="color:#6D28D9;background:#F5F3FF;border-color:#DDD6FE;">✦ {escape(str(badge))}</div>'''
        f'''<div style="font-size:1.03rem;font-weight:800;margin-top:.55rem;">{escape(str(title))}</div>'''
        f'''<div class="tc-muted" style="margin-top:.25rem;">{escape(str(body))}</div></div>''',
        unsafe_allow_html=True,
    )


def status_badge(label: str, tone: str = "primary"):
    import streamlit as st
    foreground, background, border, symbol = _TONES.get(tone, _TONES["primary"])
    st.markdown(
        f'''<span class="tc-status" style="color:{foreground};background:{background};border-color:{border};">'''
        f'''<span aria-hidden="true">{symbol}</span>{escape(str(label))}</span>''',
        unsafe_allow_html=True,
    )


def activity_item(time: str, title: str, detail: str):
    import streamlit as st
    st.markdown(
        f'''<div class="tc-activity"><div style="font-weight:800;color:#4F46E5;min-width:54px;">{escape(str(time))}</div>'''
        f'''<div><div style="font-weight:800;">{escape(str(title))}</div>'''
        f'''<div class="tc-muted">{escape(str(detail))}</div></div></div>''',
        unsafe_allow_html=True,
    )


def next_action_card(
    title: str,
    body: str,
    action_label: str = "Continue",
    key: str | None = None,
):
    """Render a next-action card with a stable unique Streamlit key."""
    import hashlib
    import inspect
    import streamlit as st

    st.markdown(
        f'''<div class="tc-card"><div class="tc-status" style="color:#3730A3;background:#EEF2FF;border-color:#C7D2FE;">● Next best action</div>'''
        f'''<h3 style="margin:.55rem 0 .25rem;">{escape(str(title))}</h3>'''
        f'''<p class="tc-muted" style="margin:0;">{escape(str(body))}</p></div>''',
        unsafe_allow_html=True,
    )

    if key is None:
        caller_frame = inspect.currentframe().f_back
        callsite = (
            f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"
            if caller_frame is not None
            else "unknown"
        )
        identity = f"{callsite}|{title}|{body}|{action_label}"
        digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:20]
        key = f"tc_next_action_{digest}"

    return st.button(action_label, key=key, type="primary", use_container_width=True)


def empty_state(
    title: str,
    body: str,
    action_label: str = "",
    *,
    key: str | None = None,
):
    import hashlib
    import streamlit as st

    st.markdown(
        f'''<div class="tc-card" style="text-align:center;padding:2rem 1.4rem;">'''
        f'''<div class="tc-status" style="color:#475569;background:#F8FAFC;border-color:#E2E8F0;">○ Action required</div>'''
        f'''<h3 style="margin:.7rem 0 .3rem;">{escape(str(title))}</h3>'''
        f'''<p class="tc-muted" style="margin:0 auto;max-width:620px;">{escape(str(body))}</p></div>''',
        unsafe_allow_html=True,
    )
    if action_label:
        if key is None:
            digest = hashlib.sha1(f"{title}|{body}|{action_label}".encode("utf-8")).hexdigest()[:16]
            key = f"tc_empty_state_{digest}"
        return st.button(action_label, key=key, type="primary")
    return False
