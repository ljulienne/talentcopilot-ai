import streamlit as st


def render_page_header(title: str, subtitle: str = "", description: str = "", icon: str = ""):
    """
    Reusable translated page header.
    """

    display_title = f"{icon} {title}" if icon else title

    st.markdown(
        f"""
<div class="tc-hero">
    <h1>{display_title}</h1>
    <h3>{subtitle}</h3>
    <p class="tc-muted">{description}</p>
</div>
""",
        unsafe_allow_html=True,
    )
