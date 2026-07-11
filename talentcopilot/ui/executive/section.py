from __future__ import annotations


def render_section(
    title: str,
    subtitle: str = "",
    *,
    description: str | None = None,
) -> None:
    """Render a consistent Executive UI section heading.

    ``description`` remains supported as a backward-compatible alias
    for ``subtitle``.
    """
    import streamlit as st

    effective_subtitle = (
        description
        if description is not None
        else subtitle
    )

    st.markdown(f"### {title}")

    if effective_subtitle:
        st.caption(effective_subtitle)
