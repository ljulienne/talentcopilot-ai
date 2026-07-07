from typing import Any


def render_decision_intelligence_card(decision_report: Any) -> None:
    """
    Streamlit rendering helper for the Decision Intelligence report.
    Safe to import in non-Streamlit contexts.
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Decision Intelligence")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Recommendation", _value(decision_report.recommendation))
    col2.metric("Decision Score", f"{decision_report.decision_score:.0f}%")
    col3.metric("Confidence", _value(decision_report.confidence))
    col4.metric("Human Validation", _value(decision_report.human_validation))

    st.info(decision_report.executive_summary)

    with st.expander("Decision Signals"):
        for signal in decision_report.signals:
            st.write(
                f"**{signal.name}** — {signal.score:.0f}/100 "
                f"(weight {signal.weight:.0%})"
            )
            st.caption(signal.explanation)

    if decision_report.strengths:
        with st.expander("Decision Strengths"):
            for strength in decision_report.strengths:
                st.success(f"**{strength.title}** — {strength.explanation}")

    if decision_report.concerns:
        with st.expander("Decision Concerns"):
            for concern in decision_report.concerns:
                st.warning(f"**{concern.title} ({concern.severity})** — {concern.explanation}")
                if concern.mitigation:
                    st.caption(f"Mitigation: {concern.mitigation}")

    if decision_report.interview_focus:
        with st.expander("Interview Focus"):
            for item in decision_report.interview_focus:
                st.write(f"- {item}")

    if decision_report.next_steps:
        with st.expander("Recommended Next Steps"):
            for item in decision_report.next_steps:
                st.write(f"- {item}")


def render_decision_summary_badge(decision_report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.metric(
        "AI Decision",
        _value(decision_report.recommendation),
        f"{decision_report.decision_score:.0f}% decision score",
    )


def _value(value: Any) -> str:
    return getattr(value, "value", str(value))
