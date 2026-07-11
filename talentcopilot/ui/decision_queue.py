from __future__ import annotations

import pandas as pd
import streamlit as st

from talentcopilot.intelligence_core.models import (
    AIDecision,
    DecisionPriority,
    DecisionQueue,
)


_PRIORITY_ICON = {
    DecisionPriority.DO_NOW: "🔴",
    DecisionPriority.PLAN: "🟡",
    DecisionPriority.MONITOR: "🟢",
}


def decisions_dataframe(queue: DecisionQueue) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "decision_id": item.decision_id,
                "priority": item.priority.value,
                "decision": item.title,
                "status": item.status.value,
                "business_impact": item.business_impact,
                "effort": item.effort.value,
                "horizon": item.horizon,
                "confidence": item.confidence_percent,
                "source_insight": item.source_insight_title,
                "business_value": item.business_value,
            }
            for item in queue.decisions
        ]
    )


def render_decision_queue(queue: DecisionQueue) -> None:
    st.markdown("### AI Decision Queue")
    st.caption(
        "TalentCopilot converts explainable insights into a prioritized action plan. "
        "Decisions remain proposals until a human validates them."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Do now", queue.do_now_count)
    c2.metric("Plan", queue.plan_count)
    c3.metric("Monitor", queue.monitor_count)

    if not queue.decisions:
        st.info("No decision can be proposed from the current evidence.")
        return

    for index, decision in enumerate(queue.decisions, start=1):
        _render_decision(decision, index=index)

    export = decisions_dataframe(queue)
    st.download_button(
        "Download decision queue",
        export.to_csv(index=False).encode("utf-8"),
        file_name="talentcopilot_ai_decision_queue.csv",
        mime="text/csv",
    
        key="organization_decision_queue_download_csv",)


def _render_decision(decision: AIDecision, *, index: int) -> None:
    icon = _PRIORITY_ICON[decision.priority]
    with st.expander(
        f"{icon} {index}. {decision.title} — {decision.priority.value}",
        expanded=index == 1,
    ):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Status", decision.status.value)
        c2.metric("Impact", decision.business_impact)
        c3.metric("Effort", decision.effort.value)
        c4.metric("Confidence", f"{decision.confidence_percent}%")

        st.markdown(f"**Recommended horizon:** {decision.horizon}")
        st.markdown(f"**Source insight:** {decision.source_insight_title}")
        st.write(decision.rationale)
        if decision.business_value:
            st.markdown(f"**Expected value:** {decision.business_value}")

        st.markdown("**Evidence**")
        for evidence in decision.evidence:
            st.write(f"- {evidence}")
