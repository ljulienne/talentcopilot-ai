from __future__ import annotations


def render_section(
    title: str,
    subtitle: str = "",
    *,
    description: str | None = None,
) -> None:
    """Render a consistent Executive UI section heading.

    ``description`` is supported as an alias for ``subtitle`` so that
    existing Executive Copilot views remain backward-compatible.
    """
    import streamlit as st

    effective_subtitle = description if description is not None else subtitle

    st.markdown(f"### {title}")
    if effective_subtitle:
        st.caption(effective_subtitle)
