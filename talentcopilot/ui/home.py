import streamlit as st

from talentcopilot.analytics.recruitment_statistics import (
    get_ai_insights,
    get_workspace_statistics,
)
from talentcopilot.ai.openai_recruiter import is_openai_available
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


def _render_ai_insights(insights):
    if not insights:
        st.info("No AI insight available yet.")
        return

    for insight in insights[:5]:
        st.markdown(
            f"""
            <div class="tc-card">
                <strong>💡 AI Insight</strong>
                <p class="tc-muted">{insight}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_platform_status(stats):
    openai_ready = is_openai_available()
    talent_pool_ready = stats.get("total_candidates", 0) > 0
    recruitment_ready = stats.get("total_recruitments", 0) > 0

    status_items = [
        ("OpenAI", openai_ready),
        ("Talent Pool", talent_pool_ready),
        ("Recruitments", recruitment_ready),
        ("Semantic Search", True),
    ]

    for label, ready in status_items:
        if ready:
            st.success(f"✅ {label} ready")
        else:
            st.warning(f"⚠️ {label} not ready")


def render_home():
    stats = get_workspace_statistics()
    insights = get_ai_insights()
    top_candidate = stats.get("top_candidate")

    st.markdown("""
    <div class="tc-hero">
        <h1>👋 Good morning, Louis</h1>
        <h3>AI Command Center</h3>
        <p class="tc-muted">
        Your enterprise AI workspace for recruitment intelligence, talent decisions and recruiter guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Recruitments", stats.get("total_recruitments", 0), "Saved projects")

    with col2:
        metric_card("Candidates", stats.get("total_candidates", 0), "Analyzed profiles")

    with col3:
        metric_card("Average Match", f"{stats.get('average_match', 0)}%", "Candidate pool")

    with col4:
        if top_candidate:
            metric_card(
                "Top Talent",
                f"{top_candidate.get('score', 0)}%",
                top_candidate.get("name", "Unknown"),
            )
        else:
            metric_card("Top Talent", "-", "No candidate yet")

    st.divider()

    section_title(
        "Today's AI Insights",
        "What deserves your attention right now."
    )

    _render_ai_insights(insights)

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        section_title(
            "Quick Actions",
            "Start, test or continue your recruitment workflow."
        )

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("🎬 Launch Demo", use_container_width=True):
                st.session_state.recruitment_context = load_demo_recruitment_context()
                st.session_state.analysis_batch = load_demo_batch()
                st.success("Demo loaded. Go to Dashboard, Candidates, Comparison or Reports.")

        with col_b:
            st.button("➕ New Recruitment", use_container_width=True)

        with col_c:
            st.button("💬 Ask AI Advisor", use_container_width=True)

        st.divider()

        section_title(
            "Recent Recruitments",
            "Resume your latest recruitment projects."
        )

        _render_recent_recruitments(stats.get("recent_recruitments", []))

    with col_right:
        assistant_panel(
            "AI Recruitment Advisor",
            "TalentCopilot summarizes your portfolio and helps you decide where to focus first."
        )

        section_title(
            "Platform Status",
            "System readiness and intelligence services."
        )

        _render_platform_status(stats)

        card(
            "🧠 Explainable AI",
            "Every recommendation includes evidence, gaps, confidence and recruiter-ready reasoning.",
            "Trust",
        )

        card(
            "🌍 Multilingual Ready",
            "French, English and Mandarin are planned as native interface languages.",
            "FR / EN / ZH",
        )
