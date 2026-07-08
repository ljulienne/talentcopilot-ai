from typing import Any


def _value(value: Any) -> str:
    return getattr(value, "value", str(value))


def render_decision_intelligence_card(decision_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Decision Intelligence")

    if decision_report is None:
        st.info("No decision report available yet.")
        return

    recommendation = _value(getattr(decision_report, "recommendation", "-"))
    confidence = _value(getattr(decision_report, "confidence", "-"))
    human_validation = _value(getattr(decision_report, "human_validation", "-"))
    decision_score = float(getattr(decision_report, "decision_score", 0) or 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Recommendation", recommendation)
    col2.metric("Decision Score", f"{decision_score:.0f}%")
    col3.metric("Confidence", confidence)
    col4.metric("Human Validation", human_validation)

    summary = getattr(decision_report, "executive_summary", "")
    if summary:
        st.info(summary)

    concerns = getattr(decision_report, "concerns", []) or []
    if concerns:
        with st.expander("Concerns"):
            for concern in concerns:
                st.warning(
                    f"**{getattr(concern, 'title', 'Concern')}** — "
                    f"{getattr(concern, 'explanation', '')}"
                )

    focus = getattr(decision_report, "interview_focus", []) or []
    if focus:
        with st.expander("Interview Focus"):
            for item in focus:
                st.write(f"- {item}")


def render_decision_summary_badge(decision_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    if decision_report is None:
        st.metric("AI Decision", "Not available")
        return

    recommendation = _value(getattr(decision_report, "recommendation", "-"))
    decision_score = float(getattr(decision_report, "decision_score", 0) or 0)

    st.metric("AI Decision", recommendation, f"{decision_score:.0f}% decision score")
