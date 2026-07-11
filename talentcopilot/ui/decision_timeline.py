from __future__ import annotations

import pandas as pd
import streamlit as st

from talentcopilot.intelligence_core.models import (
    DecisionQueue,
    DecisionStatus,
    DecisionTimeline,
)
from talentcopilot.intelligence_core.timeline_engine import DecisionTimelineEngine


def timeline_dataframe(timeline: DecisionTimeline) -> pd.DataFrame:
    rows = []
    for item in timeline.items:
        for event in item.events:
            rows.append(
                {
                    "decision_id": item.decision.decision_id,
                    "decision": item.decision.title,
                    "priority": item.decision.priority.value,
                    "status": event.status.value,
                    "occurred_at": event.occurred_at,
                    "actor": event.actor,
                    "note": event.note,
                }
            )
    return pd.DataFrame(rows)


def render_decision_timeline(queue: DecisionQueue, *, state_key: str = "organization_decision_timeline") -> None:
    st.markdown("### Decision Timeline")
    st.caption(
        "Validate AI proposals, track execution and preserve a traceable history of human decisions."
    )

    engine = DecisionTimelineEngine()
    queue_signature = tuple(item.decision_id for item in queue.decisions)
    signature_key = f"{state_key}_signature"

    if state_key not in st.session_state or st.session_state.get(signature_key) != queue_signature:
        st.session_state[state_key] = engine.initialize(queue)
        st.session_state[signature_key] = queue_signature

    timeline: DecisionTimeline = st.session_state[state_key]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Proposed", timeline.proposed_count)
    c2.metric("Active", timeline.active_count)
    c3.metric("Completed", timeline.completed_count)
    c4.metric("Completion", f"{timeline.completion_rate}%")

    for index, item in enumerate(timeline.items, start=1):
        current = item.current_status
        with st.expander(
            f"{index}. {item.decision.title} — {current.value}",
            expanded=index == 1,
        ):
            st.write(f"**Priority:** {item.decision.priority.value}")
            st.write(f"**Business impact:** {item.decision.business_impact}")
            st.write(f"**Last update:** {item.last_updated or 'Not available'}")

            allowed = engine.allowed_next_statuses(current)
            if allowed:
                options = [status.value for status in allowed]
                next_value = st.selectbox(
                    "Next status",
                    options,
                    key=f"timeline_status_{item.decision.decision_id}",
                )
                note = st.text_input(
                    "Decision note",
                    key=f"timeline_note_{item.decision.decision_id}",
                    placeholder="Reason, owner or next milestone",
                )
                if st.button("Update decision", key=f"timeline_update_{item.decision.decision_id}"):
                    st.session_state[state_key] = engine.transition(
                        timeline,
                        decision_id=item.decision.decision_id,
                        status=DecisionStatus(next_value),
                        note=note,
                    )
                    st.rerun()
            else:
                st.success("This decision has reached a terminal status.")

            st.markdown("**History**")
            for event in reversed(item.events):
                note_text = f" — {event.note}" if event.note else ""
                st.write(f"- {event.occurred_at}: **{event.status.value}** by {event.actor}{note_text}")

    export = timeline_dataframe(timeline)
    st.download_button(
        "Download decision timeline",
        export.to_csv(index=False).encode("utf-8"),
        file_name="talentcopilot_decision_timeline.csv",
        mime="text/csv",
    )
