from typing import Any


def render_recruiter_copilot_card(copilot_report: Any) -> None:
    """
    Streamlit rendering helper for Recruiter Copilot v2.
    Safe to import in non-Streamlit contexts.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Recruiter Copilot v2")
    st.info(copilot_report.headline)
    st.write(copilot_report.recruiter_summary)

    col1, col2 = st.columns(2)
    col1.metric("Actions", len(copilot_report.actions))
    col2.metric("Alerts", len(copilot_report.alerts))

    if copilot_report.actions:
        with st.expander("Recommended Actions", expanded=True):
            for action in copilot_report.actions:
                st.write(f"**{_value(action.priority)} — {action.title}**")
                st.caption(action.rationale)

    if copilot_report.alerts:
        with st.expander("Alerts"):
            for alert in copilot_report.alerts:
                st.warning(f"**{alert.title} ({_value(alert.severity)})** — {alert.message}")
                if alert.mitigation:
                    st.caption(f"Mitigation: {alert.mitigation}")

    if copilot_report.interview_questions:
        with st.expander("Interview Questions"):
            for question in copilot_report.interview_questions:
                st.write(f"**{question.competency}**")
                st.write(question.question)
                st.caption(f"Purpose: {question.purpose}")
                st.caption(f"Positive signal: {question.positive_signal}")
                st.caption(f"Red flag: {question.red_flag}")

    with st.expander("Stakeholder Summary"):
        st.write(copilot_report.stakeholder_summary)

    st.success(copilot_report.closing_recommendation)


def render_recruiter_copilot_summary(copilot_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.metric("Recruiter Copilot", copilot_report.headline)
    if copilot_report.has_high_priority_alerts:
        st.warning("High-priority recruiter validation required.")


def _value(value: Any) -> str:
    return getattr(value, "value", str(value))
