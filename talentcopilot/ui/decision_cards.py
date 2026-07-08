
from typing import Any


def render_decision_intelligence_card(decision_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Decision Intelligence")

    if decision_report is None:
        st.info("No decision report available yet.")
        return

    recommendation = getattr(decision_report, "recommendation", "-")
    recommendation = getattr(recommendation, "value", recommendation)

    confidence = getattr(decision_report, "confidence", "-")
    confidence = getattr(confidence, "value", confidence)

    human_validation = getattr(decision_report, "human_validation", "-")
    human_validation = getattr(human_validation, "value", human_validation)

    col1, col2, col3 = st.columns(3)
    col1.metric("Recommendation", recommendation)
    col2.metric("Decision Score", f"{getattr(decision_report, 'decision_score', 0):.0f}%")
    col3.metric("Confidence", confidence)

    st.info(getattr(decision_report, "executive_summary", ""))

    if getattr(decision_report, "concerns", None):
        with st.expander("Concerns"):
            for concern in decision_report.concerns:
                st.warning(
                    f"**{getattr(concern, 'title', 'Concern')}** — "
                    f"{getattr(concern, 'explanation', '')}"
                )

    if getattr(decision_report, "interview_focus", None):
        with st.expander("Interview Focus"):
            for item in decision_report.interview_focus:
                st.write(f"- {item}")

    st.caption(f"Human validation: {human_validation}")


def render_decision_summary_badge(decision_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    if decision_report is None:
        st.metric("AI Decision", "Not available")
        return

    recommendation = getattr(decision_report, "recommendation", "-")
    recommendation = getattr(recommendation, "value", recommendation)

    st.metric(
        "AI Decision",
        recommendation,
        f"{getattr(decision_report, 'decision_score', 0):.0f}% decision score",
    )
