
import streamlit as st

from talentcopilot.config import APP_NAME, APP_VERSION
from talentcopilot.ui.theme import apply_theme
from talentcopilot.ui.home import render_home
from talentcopilot.ui.dashboard import render_dashboard
from talentcopilot.ui.comparison import render_candidate_comparison

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")
apply_theme()

if "analysis_batch" not in st.session_state:
    st.session_state.analysis_batch = None

st.sidebar.title("🧠 TalentCopilot")
st.sidebar.caption(f"Version {APP_VERSION}")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📊 Dashboard", "👥 Candidates", "⚖️ Comparison", "📄 Reports", "⚙️ Settings"]
)

if page == "🏠 Home":
    render_home()

elif page == "📊 Dashboard":
    render_dashboard()

elif page == "👥 Candidates":
    st.title("👥 Candidates")
    batch = st.session_state.get("analysis_batch")
    if not batch:
        st.info("Run an analysis first from the Dashboard.")
    else:
        for index, item in enumerate(batch["results"], start=1):
            candidate = item["candidate"]
            match = item["match_result"]
            st.write(f"**#{index} — {candidate.name}**")
            st.write(f"Match: {match.overall_score}% | Recommendation: {match.recommendation}")
            st.divider()

elif page == "⚖️ Comparison":
    batch = st.session_state.get("analysis_batch")
    results = batch["results"] if batch and batch.get("success") else []
    render_candidate_comparison(results)

elif page == "📄 Reports":
    st.title("📄 Reports")
    st.info("Recruiter reports will be added in v0.7.")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.info("Settings will be added later.")
