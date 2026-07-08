from typing import Iterable, List, Tuple


def enterprise_hero(title: str, subtitle: str, badge: str = "TalentCopilot Enterprise"):
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-hero">
            <div class="tc-badge">{badge}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    st.markdown(
        f"""
        <div class="tc-priority">
            <strong>{badge}</strong>
            <div style="font-size:1.02rem;font-weight:700;margin-top:0.25rem;">{title}</div>
            <div class="tc-muted">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def activity_item(time: str, title: str, detail: str):
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-activity">
            <div style="font-weight:700;color:#2563EB;min-width:52px;">{time}</div>
            <div>
                <div style="font-weight:700;">{title}</div>
                <div class="tc-muted">{detail}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def next_action_card(title: str, body: str, action_label: str = "Continue"):
    import streamlit as st

    st.markdown(
        f"""
        <div class="tc-shell-card">
            <div class="tc-badge" style="background:#EEF2FF;color:#3730A3;border-color:#C7D2FE;">Next Best Action</div>
            <h3 style="margin:0.4rem 0;">{title}</h3>
            <p class="tc-muted">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(action_label)
