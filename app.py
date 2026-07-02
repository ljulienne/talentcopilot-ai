import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.ui.theme import apply_theme
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

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")
apply_theme()

if "analysis_batch" not in st.session_state:
    st.session_state.analysis_batch = None

if "recruitment_context" not in st.session_state:
    st.session_state.recruitment_context = None

if "current_recruitment" not in st.session_state:
    st.session_state.current_recruitment = None

st.sidebar.markdown("## 🧠 TalentCopilot AI")
st.sidebar.caption(f"Version {APP_VERSION} · Beta")
st.sidebar.markdown("---")

context = st.session_state.get("recruitment_context")

if context:
    st.sidebar.markdown("**Current Recruitment**")
    st.sidebar.caption(context.get("job_title", "Untitled recruitment"))
    st.sidebar.caption(context.get("company", ""))
    st.sidebar.markdown("---")

st.sidebar.markdown("**Workflow**")
st.sidebar.caption("1. New Recruitment")
st.sidebar.caption("2. Open Recruitment")
st.sidebar.caption("3. Dashboard Analysis")
st.sidebar.caption("4. Talent Review")
st.sidebar.caption("5. Recruiter Copilot")
st.sidebar.caption("6. Candidate Comparison")
st.sidebar.caption("7. Recruiter Report")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "➕ New Recruitment",
        "📂 Open Recruitment",
        "📊 Dashboard",
        "👥 Candidates",
        "🧠 Talent Pool",
        "💬 Recruiter Copilot",
        "⚖️ Comparison",
        "📄 Reports",
        "⚙️ Settings",
    ]
)

if page == "🏠 Home":
    render_home()

elif page == "➕ New Recruitment":
    render_new_recruitment()

elif page == "📂 Open Recruitment":
    render_open_recruitment()

elif page == "📊 Dashboard":
    render_dashboard()

elif page == "👥 Candidates":
    render_candidates()

elif page == "🧠 Talent Pool":
    render_talent_pool()

elif page == "💬 Recruiter Copilot":
    render_recruiter_copilot()

elif page == "⚖️ Comparison":
    batch = st.session_state.get("analysis_batch")
    results = batch["results"] if batch and batch.get("success") else []
    render_candidate_comparison(results)

elif page == "📄 Reports":
    render_reports()

elif page == "⚙️ Settings":
    render_settings()

footer(APP_VERSION)
