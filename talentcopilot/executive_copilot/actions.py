from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CopilotActionItem:
    title: str
    impact: str
    source_question_id: str


def add_action_item(item: CopilotActionItem) -> bool:
    """Add an action to the current Streamlit session without duplicates."""
    import streamlit as st

    current = st.session_state.setdefault("executive_copilot_action_plan", [])
    if any(existing.get("title") == item.title for existing in current):
        return False
    current.append(
        {
            "title": item.title,
            "impact": item.impact,
            "source_question_id": item.source_question_id,
        }
    )
    return True


def get_action_plan() -> tuple[CopilotActionItem, ...]:
    import streamlit as st

    return tuple(
        CopilotActionItem(
            title=str(item.get("title", "")),
            impact=str(item.get("impact", "")),
            source_question_id=str(item.get("source_question_id", "")),
        )
        for item in st.session_state.get("executive_copilot_action_plan", [])
        if item.get("title")
    )


def remove_action_item(title: str) -> None:
    import streamlit as st

    st.session_state["executive_copilot_action_plan"] = [
        item
        for item in st.session_state.get("executive_copilot_action_plan", [])
        if item.get("title") != title
    ]
