from talentcopilot.ui.brand import brand_lockup_html


def render_enterprise_brand(app_version: str):
    import streamlit as st

    st.sidebar.markdown(
        brand_lockup_html(version=app_version),
        unsafe_allow_html=True,
    )


def render_workspace_caption(label: str, description: str = ""):
    import streamlit as st

    st.sidebar.markdown(f"**{label}**")
    if description:
        st.sidebar.caption(description)


def render_current_recruitment(session=None):
    import streamlit as st

    role = (
        getattr(session, "role_title", "No active recruitment")
        if session is not None
        else "No active recruitment"
    )
    analyzed = int(getattr(session, "analyzed_count", 0) or 0) if session is not None else 0
    candidates = int(getattr(session, "candidate_count", 0) or 0) if session is not None else 0
    st.sidebar.markdown(
        f'<div class="tc-mission-card"><div class="tc-mission-kicker">Active mission</div>'
        f'<div class="tc-mission-role">{role}</div>'
        f'<div class="tc-mission-meta">{analyzed}/{candidates} candidates analyzed</div></div>',
        unsafe_allow_html=True,
    )
