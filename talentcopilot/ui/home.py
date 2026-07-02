import streamlit as st

from talentcopilot.analytics.recruitment_statistics import (
    get_ai_insights,
    get_workspace_statistics,
)
from talentcopilot.demo.demo_data import (
    load_demo_batch,
    load_demo_recruitment_context,
)
from talentcopilot.ui.components import card, assistant_panel, section_title, metric_card


def _render_recent_recruitments(recent_recruitments):
    if not recent_recruitments:
        st.info("No saved recruitment yet.")
        return

    for item in recent_recruitments:
        title = item.get("title", "Untitled Recruitment")
        candidate_count = item.get("candidate_count", 0)
        updated_at = item.get("updated_at", "-")

        status = "Complete" if candidate_count > 0 else "Draft"

        col_title, col_status, col_date = st.columns([4, 1.5, 1.5])

        with col_title:
            st.write(f"**{title}**")
            st.caption(item.get("id", ""))

        with col_status:
            if status == "Complete":
                st.success("Complete")
            else:
                st.warning("Draft")

        with col_date:
            st.caption(updated_at[:10] if updated_at else "-")

        st.divider()


def render_home():
    stats = get_workspace_statistics()
    insights = get_ai_insights()
    top_candidate = stats.get("top_candidate")

    st.markdown("""
    <div class="tc-hero">
        <h1>🧠 TalentCopilot AI</h1>
        <h3>Recruiter Workspace</h3>
        <p class="tc-muted">
        Your AI-powered command center for recruitment analysis, candidate ranking and hiring decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Recruitments",
            stats.get("total_recruitments", 0),
            "Saved projects"
        )

    with col2:
        metric_card(
            "Candidates",
            stats.get("total_candidates", 0),
            "Analyzed profiles"
        )

    with col3:
        metric_card(
            "Average Match",
            f"{stats.get('average_match', 0)}%",
            "Across all candidates"
        )

    with col4:
        if top_candidate:
            metric_card(
                "Top Candidate",
                f"{top_candidate.get('score', 0)}%",
                top_candidate.get("name", "Unknown")
            )
        else:
            metric_card(
                "Top Candidate",
                "-",
                "No candidate yet"
            )

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        section_title(
            "Recent Recruitments",
            "Resume your latest recruitment projects."
        )

        _render_recent_recruitments(stats.get("recent_recruitments", []))

        section_title(
            "Quick Actions",
            "Start, test or continue your recruitment workflow."
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🎬 Launch Demo", use_container_width=True):
                st.session_state.recruitment_context = load_demo_recruitment_context()
                st.session_state.analysis_batch = load_demo_batch()
                st.success("Demo loaded. Go to Dashboard, Candidates, Comparison or Reports.")

        with col_b:
            st.info("Use the sidebar to create or open a recruitment.")

    with col_right:
        assistant_panel(
            "Recruiter Copilot",
            "This workspace summarizes your recruitment activity and highlights where to focus next."
        )

        section_title(
            "AI Insights",
            "Portfolio-level recruitment intelligence."
        )

        for insight in insights:
            st.write(f"• {insight}")

        card(
            "🧠 Explainable AI",
            "Every recommendation includes evidence, gaps, confidence and recruiter-ready reasoning.",
            "Trust"
        )

        card(
            "🌍 Multilingual",
            "French, English and Mandarin support through the Talent Knowledge Base.",
            "FR / EN / ZH"
        )
