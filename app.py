import streamlit as st

from talentcopilot.i18n import tr, LANGUAGES

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.ui.theme import apply_theme
from talentcopilot.ui.premium_theme import apply_premium_ui, premium_sidebar_brand
from talentcopilot.ui.home import render_home
from talentcopilot.ui.dashboard import render_dashboard
from talentcopilot.ui.comparison import render_candidate_comparison
from talentcopilot.ui.reports import render_reports
from talentcopilot.ui.settings import render_settings
from talentcopilot.ui.candidates import render_candidates
from talentcopilot.ui.components import footer
from talentcopilot.ui.recruitment_wizard import render_new_recruitment
from talentcopilot.ui.open_recruitment import render_open_recruitment
from talentcopilot.ui.talent_pool import render_talent_pool
from talentcopilot.ui.recruiter_copilot import render_recruiter_copilot
from talentcopilot.ui.decision_workspace import render_decision_workspace

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")
apply_theme()
apply_premium_ui()

if "language" not in st.session_state:
    st.session_state.language = "English"

if "analysis_batch" not in st.session_state:
    st.session_state.analysis_batch = None

if "recruitment_context" not in st.session_state:
    st.session_state.recruitment_context = None

if "current_recruitment" not in st.session_state:
    st.session_state.current_recruitment = None

premium_sidebar_brand(APP_VERSION)
st.sidebar.markdown("---")

selected_language = st.sidebar.selectbox(
    "🌍 Language",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language),
)

st.session_state.language = selected_language

st.sidebar.markdown("---")

context = st.session_state.get("recruitment_context")

if context:
    st.sidebar.markdown("**Current Recruitment**")
    st.sidebar.caption(context.get("job_title", "Untitled recruitment"))
    st.sidebar.caption(context.get("company", ""))
    st.sidebar.markdown("---")

st.sidebar.markdown("### 🚀 Decision Workflow")

with st.sidebar.container(border=True):
    st.markdown("**1 · Create**")
    st.caption("New Recruitment")

    st.markdown("**2 · Analyze**")
    st.caption("Dashboard Analysis")

    st.markdown("**3 · Decide**")
    st.caption("Decision Workspace")

    st.markdown("**4 · Validate**")
    st.caption("Interview & Copilot")

    st.markdown("**5 · Report**")
    st.caption("Decision Report")

st.sidebar.markdown("---")

pages = {
    tr("menu.home"): render_home,
    tr("menu.new_recruitment"): render_new_recruitment,
    tr("menu.open_recruitment"): render_open_recruitment,
    tr("menu.dashboard"): render_dashboard,
    "Decision Workspace": render_decision_workspace,
    tr("menu.candidates"): render_candidates,
    tr("menu.talent_pool"): render_talent_pool,
    tr("menu.recruiter_copilot"): render_recruiter_copilot,
    tr("menu.comparison"): "comparison",
    tr("menu.reports"): render_reports,
    tr("menu.settings"): render_settings,
}

page = st.sidebar.radio(
    tr("navigation"),
    list(pages.keys())
)

selected_page = pages[page]

if selected_page == "comparison":
    batch = st.session_state.get("analysis_batch")
    results = batch["results"] if batch and batch.get("success") else []
    render_candidate_comparison(results)
else:
    selected_page()

footer(APP_VERSION)
