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


def candidate_card(candidate, score=None, rank=None):
    name = candidate.get("name", "Unknown candidate") if isinstance(candidate, dict) else str(candidate)

    with st.container():
        title = f"{rank}. {name}" if rank else name
        st.markdown(f"### 👤 {title}")

        if score is not None:
            st.metric("Score", score)

        if isinstance(candidate, dict):
            if candidate.get("summary"):
                st.write(candidate["summary"])
            if candidate.get("skills"):
                st.caption("Skills: " + ", ".join(candidate["skills"]))


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


def footer():
    st.markdown("---")
    st.caption("TalentCopilot-AI · AI Recruitment Decision Intelligence")


try:
    from talentcopilot.ui.components.reasoning_cards import render_reasoning_report
except Exception:
    pass
