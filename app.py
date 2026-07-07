import streamlit as st

from talentcopilot.i18n import tr, LANGUAGES

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.ui.theme import apply_theme
from talentcopilot.ui.premium_theme import apply_premium_ui, premium_sidebar_brand
from talentcopilot.ui.sidebar import render_sidebar_brand, render_sidebar_context, render_sidebar_workflow
from talentcopilot.ui.home import render_home
from talentcopilot.ui.home_v2 import render_home_v2
from talentcopilot.ui.dashboard import render_dashboard
from talentcopilot.ui.comparison import render_candidate_comparison
from talentcopilot.ui.comparison_v2 import render_comparison_v2
from talentcopilot.ui.reports import render_reports
from talentcopilot.ui.reports_v2 import render_reports_v2
from talentcopilot.ui.settings import render_settings
from talentcopilot.ui.candidates import render_candidates
from talentcopilot.ui.candidates_v2 import render_candidates_v2
from talentcopilot.ui.components import footer
from talentcopilot.ui.recruitment_wizard import render_new_recruitment
from talentcopilot.ui.open_recruitment import render_open_recruitment
from talentcopilot.ui.talent_pool import render_talent_pool
from talentcopilot.ui.talent_pool_v2 import render_talent_pool_v2
from talentcopilot.ui.recruiter_copilot import render_recruiter_copilot
from talentcopilot.ui.decision_workspace import render_decision_workspace
from talentcopilot.ui.app_layout import render_page_shell
from talentcopilot.ui.dashboard_v2 import render_dashboard_v2

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

render_sidebar_brand(APP_VERSION)

selected_language = st.sidebar.selectbox(
    "🌍 Language",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language),
)

st.session_state.language = selected_language

st.sidebar.markdown("---")

context = st.session_state.get("recruitment_context")

render_sidebar_context(context)
render_sidebar_workflow()

pages = {
    tr("menu.home"): render_home_v2,
    "Decision Center": render_dashboard_v2,
    tr("menu.new_recruitment"): render_new_recruitment,
    tr("menu.open_recruitment"): render_open_recruitment,
    tr("menu.dashboard"): render_dashboard,
    "Decision Workspace": render_decision_workspace,
    tr("menu.candidates"): render_candidates_v2,
    tr("menu.talent_pool"): render_talent_pool_v2,
    tr("menu.recruiter_copilot"): render_recruiter_copilot,
    tr("menu.comparison"): render_comparison_v2,
    tr("menu.reports"): render_reports_v2,
    tr("menu.settings"): render_settings,
}

page = st.sidebar.radio(
    tr("navigation"),
    list(pages.keys())
)

selected_page = pages[page]

if selected_page in {
    render_dashboard_v2,
    render_decision_workspace,
    render_reports,
    render_candidates,
    render_talent_pool,
    render_recruiter_copilot,
}:
    render_page_shell(selected_page)
else:
    selected_page()

footer(APP_VERSION)
