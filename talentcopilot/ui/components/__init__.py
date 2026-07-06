import streamlit as st


def section_title(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def card(title: str, body: str = "", icon: str = "📌"):
    with st.container():
        st.markdown(f"### {icon} {title}")
        if body:
            st.write(body)


def metric_card(label: str, value, delta=None, help_text: str = ""):
    st.metric(label=label, value=value, delta=delta, help=help_text or None)


def assistant_panel(title: str = "AI Assistant", body: str = ""):
    st.info(f"**{title}**\n\n{body}" if body else f"**{title}**")


def status_badge(label: str, status: str = "info"):
    icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
    }
    st.markdown(f"{icons.get(status, 'ℹ️')} **{label}**")


def insight_card(title: str, body: str = "", confidence: str = ""):
    with st.container():
        st.markdown(f"### {title}")
        if body:
            st.write(body)
        if confidence:
            st.caption(f"Confidence: {confidence}")


def recommendation_card(title: str, body: str = "", level: str = "info"):
    if level == "success":
        st.success(f"**{title}**\n\n{body}")
    elif level == "warning":
        st.warning(f"**{title}**\n\n{body}")
    elif level == "error":
        st.error(f"**{title}**\n\n{body}")
    else:
        st.info(f"**{title}**\n\n{body}")


def divider():
    st.divider()


try:
    from talentcopilot.ui.components.reasoning_cards import render_reasoning_report
except Exception:
    pass
