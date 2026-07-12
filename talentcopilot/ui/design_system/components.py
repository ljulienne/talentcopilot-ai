from typing import Iterable, Tuple


def enterprise_hero(title: str, subtitle: str, badge: str = "TalentCopilot Enterprise"):
    import streamlit as st
    st.markdown(f'''<div class="tc-hero"><div class="tc-badge">{badge}</div><h1>{title}</h1><p>{subtitle}</p></div>''', unsafe_allow_html=True)


def section_title(title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f'<div class="tc-section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def metric_grid(metrics: Iterable[Tuple[str, str, str]]):
    import streamlit as st
    metrics = list(metrics)
    cols = st.columns(len(metrics) if metrics else 1)
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta)


def insight_card(title: str, body: str, badge: str = "AI Insight"):
    import streamlit as st
    st.markdown(f'''<div class="tc-insight"><strong>{badge}</strong><div style="font-size:1.03rem;font-weight:800;margin-top:0.25rem;">{title}</div><div class="tc-muted">{body}</div></div>''', unsafe_allow_html=True)


def status_badge(label: str, tone: str = "primary"):
    import streamlit as st
    color_map = {"primary": "#2563EB", "ai": "#7C3AED", "success": "#22C55E", "warning": "#F59E0B", "danger": "#EF4444"}
    color = color_map.get(tone, color_map["primary"])
    st.markdown(f'''<span class="tc-status" style="color:{color};background:{color}14;border-color:{color}33;">{label}</span>''', unsafe_allow_html=True)


def activity_item(time: str, title: str, detail: str):
    import streamlit as st
    st.markdown(f'''<div class="tc-activity"><div style="font-weight:800;color:#2563EB;min-width:54px;">{time}</div><div><div style="font-weight:800;">{title}</div><div class="tc-muted">{detail}</div></div></div>''', unsafe_allow_html=True)


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
        f"""
        <div class="tc-card">
            <div
                class="tc-badge"
                style="
                    background:#EEF2FF;
                    color:#3730A3;
                    border-color:#C7D2FE;
                "
            >
                Next Best Action
            </div>
            <h3 style="margin:0.35rem 0;">{title}</h3>
            <p class="tc-muted">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if key is None:
        caller_frame = inspect.currentframe().f_back

        if caller_frame is not None:
            callsite = (
                f"{caller_frame.f_code.co_filename}:"
                f"{caller_frame.f_lineno}"
            )
        else:
            callsite = "unknown"

        identity = (
            f"{callsite}|{title}|{body}|{action_label}"
        )

        digest = hashlib.sha1(
            identity.encode("utf-8")
        ).hexdigest()[:20]

        key = f"tc_next_action_{digest}"

    return st.button(
        action_label,
        key=key,
    )



def empty_state(title: str, body: str, action_label: str = ""):
    import streamlit as st
    st.markdown(f'''<div class="tc-card" style="text-align:center;padding:2rem;"><h3 style="margin-bottom:0.3rem;">{title}</h3><p class="tc-muted">{body}</p></div>''', unsafe_allow_html=True)
    if action_label:
        st.button(action_label)
