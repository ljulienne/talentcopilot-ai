from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable


@dataclass(frozen=True)
class TimelineStep:
    title: str
    detail: str = ""
    status: str = "complete"


def render_timeline(steps: Iterable[TimelineStep], *, title: str = "Decision trace") -> None:
    import streamlit as st

    normalized = list(steps)
    st.markdown(f"#### {escape(title)}")
    if not normalized:
        st.caption("No trace available.")
        return

    content = []
    for index, step in enumerate(normalized, start=1):
        content.append(
            f"""
            <div class="tc-exec-trace-item">
              <div class="tc-exec-label">Step {index}</div>
              <div style="font-weight:850;">{escape(step.title)}</div>
              <div class="tc-exec-body">{escape(step.detail)}</div>
            </div>
            """
        )
    st.markdown(f'<div class="tc-exec-trace">{"".join(content)}</div>', unsafe_allow_html=True)
