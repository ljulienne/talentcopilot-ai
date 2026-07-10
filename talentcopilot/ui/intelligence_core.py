import streamlit as st

from talentcopilot.intelligence_core.models import ExecutiveBrief, OrganizationInsight


def render_executive_brief(brief: ExecutiveBrief) -> None:
    st.markdown("### Executive intelligence")
    st.subheader(brief.headline)
    st.write(brief.narrative)

    c1, c2, c3 = st.columns(3)
    c1.metric("Confidence", f"{brief.confidence_percent}%")
    c2.metric("Evidence quality", brief.evidence_quality)
    c3.metric("Decision readiness", brief.decision_readiness.value)

    if brief.recommended_decisions:
        st.markdown("#### Recommended decisions")
        for index, decision in enumerate(brief.recommended_decisions, start=1):
            st.write(f"{index}. {decision}")


def render_insight(insight: OrganizationInsight, expanded: bool = False) -> None:
    icon = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢",
    }.get(insight.severity.value, "🔵")

    with st.expander(
        f"{icon} {insight.title} — {insight.severity.value}",
        expanded=expanded,
    ):
        st.write(insight.current_situation)
        st.markdown(f"**Business impact:** {insight.business_impact}")
        st.caption(
            f"Confidence {insight.confidence_percent}% · "
            f"Evidence {insight.evidence_quality} · "
            f"Decision readiness {insight.decision_readiness.value}"
        )

        st.markdown("**Evidence**")
        for evidence in insight.evidence:
            st.write(f"- **{evidence.label}:** {evidence.detail}")

        st.markdown("**Recommended actions**")
        for recommendation in insight.recommendations:
            st.write(
                f"- **{recommendation.priority} — {recommendation.timeframe}:** "
                f"{recommendation.action}"
            )
