from typing import Iterable, Optional


def render_enterprise_brand(app_version: str):
    import streamlit as st

    st.sidebar.markdown(
        f'''
        <div style="display:flex;align-items:center;margin-bottom:1rem;">
            <div class="tc-logo-mark">TC</div>
            <div>
                <div style="font-weight:900;font-size:1rem;">TalentCopilot</div>
                <div style="font-size:0.78rem;opacity:0.72;">Enterprise · {app_version}</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def render_workspace_caption(label: str, description: str = ""):
    import streamlit as st

    st.sidebar.markdown(f"**{label}**")
    if description:
        st.sidebar.caption(description)


def render_current_recruitment(session=None):
    import streamlit as st

    st.sidebar.markdown("---")
    st.sidebar.caption("Current recruitment")
    if session is None:
        st.sidebar.info("No active recruitment")
        return

    role = getattr(session, "role_title", "Recruitment")
    analyzed = getattr(session, "analyzed_count", 0)
    candidates = getattr(session, "candidate_count", 0)
    st.sidebar.success(role)
    st.sidebar.caption(f"{analyzed}/{candidates} analyzed")
