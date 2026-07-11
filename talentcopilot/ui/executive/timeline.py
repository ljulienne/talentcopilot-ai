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
    # Remove leading indentation from HTML fragments. Otherwise Markdown may
    # interpret the HTML as a code block and display the tags as raw text.
    normalized_content = "".join(fragment.strip() for fragment in content)
    trace_html = f'<div class="tc-exec-trace">{normalized_content}</div>'

    st.markdown(
        trace_html,
        unsafe_allow_html=True,
    )
