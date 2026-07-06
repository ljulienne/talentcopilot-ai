import streamlit as st


def card(title: str, body: str = "", icon: str = "📌"):
    with st.container():
        st.markdown(f"### {icon} {title}")
        if body:
            st.write(body)


def section_title(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def metric_card(label: str, value, help_text: str = ""):
    st.metric(label=label, value=value, help=help_text or None)


def assistant_panel(title: str = "AI Assistant", body: str = ""):
    with st.container():
        st.info(f"**{title}**\n\n{body}" if body else f"**{title}**")
