import streamlit as st

from talentcopilot.talent_pool.talent_metrics import enrich_talent_profiles
from talentcopilot.talent_pool.talent_store import list_talent_profiles
from talentcopilot.ui.components import section_title, assistant_panel, metric_card


def _filter_talents(talents, search):
    if not search:
        return talents

    query = search.lower().strip()

    return [
        talent for talent in talents
        if query in talent.get("name", "").lower()
        or query in talent.get("candidate_key", "").lower()
        or query in talent.get("last_recruitment_title", "").lower()
    ]


def _render_history(history):
    if not history:
        st.info("No application history available.")
        return

    for record in history:
        st.write(
            f"**{record.get('recruitment_title', 'Untitled Recruitment')}** "
            f"— {record.get('score', 0)}% match"
        )
        st.caption(
            f"Confidence: {record.get('confidence', 0)}% · "
            f"Recommendation: {record.get('recommendation', '-')}"
        )

        summary = record.get("executive_summary")
        if summary:
            st.write(summary)

        st.divider()


def _render_talent_profile(talent):
    name = talent.get("name", "Unknown Candidate")
    talent_score = talent.get("talent_score", 0)
    progression = talent.get("progression_trend", "Not enough history")
    best_application = talent.get("best_application")
    latest_application = talent.get("latest_application")

    st.markdown(f"""
    <div class="tc-hero">
        <h1>👤 {name}</h1>
        <h3>Talent Intelligence Profile</h3>
        <p class="tc-muted">
        Consolidated profile based on all recruitment analyses involving this talent.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Talent Score", f"{talent_score}%", "Overall talent value")

    with col2:
        metric_card("Applications", talent.get("application_count", 0), "Recruitment history")

    with col3:
        metric_card("Average Match", f"{talent.get('average_score', 0)}%", "Across applications")

    with col4:
        metric_card("AI Confidence", f"{talent.get('average_confidence', 0)}%", "Average confidence")

    st.progress(min(talent_score, 100) / 100)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        section_title("Talent Overview", "Key consolidated indicators.")

        metric_card("Highest Match", f"{talent.get('highest_score', 0)}%", "Best recorded match")
        metric_card("Progression", progression, "Score evolution")
        metric_card(
            "Latest Recruitment",
            talent.get("last_recruitment_title", "-"),
            "Most recent context"
        )

    with col_right:
        section_title("Best Application", "Highest scoring recruitment context.")

        if best_application:
            metric_card(
                "Best Score",
                f"{best_application.get('score', 0)}%",
                best_application.get("recruitment_title", "Untitled Recruitment"),
                "#10B981",
            )
            st.write(f"**Recommendation:** {best_application.get('recommendation', '-')}")
            summary = best_application.get("executive_summary")
            if summary:
                st.write(summary)
        else:
            st.info("No best application available.")

    st.divider()

    section_title(
        "Application History",
        "All recruitment analyses linked to this talent."
    )

    _render_history(talent.get("application_history", []))

    st.divider()

    assistant_panel(
        "TalentCopilot Assessment",
        "This profile consolidates the candidate's historical performance. Future versions will add skills, languages, salary expectations, interview notes and AI-generated talent summaries."
    )


def render_talent_pool():
    st.markdown("""
    <div class="tc-hero">
        <h1>👥 Talent Pool</h1>
        <h3>Enterprise Talent Intelligence</h3>
        <p class="tc-muted">
        Explore consolidated talent profiles automatically built from recruitment analyses.
        </p>
    </div>
    """, unsafe_allow_html=True)

    raw_talents = list_talent_profiles()

    if not raw_talents:
        assistant_panel(
            "Talent Intelligence",
            "No talent profile found yet. Analyze and save a recruitment to automatically populate the Talent Pool."
        )
        return

    talents = enrich_talent_profiles(raw_talents)

    total_talents = len(talents)
    total_applications = sum(talent.get("application_count", 0) for talent in talents)
    avg_score = round(
        sum(talent.get("average_score", 0) for talent in talents) / total_talents
    ) if total_talents else 0
    best_talent = max(talents, key=lambda talent: talent.get("talent_score", 0))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Talents", total_talents, "Consolidated profiles")

    with col2:
        metric_card("Applications", total_applications, "Across recruitments")

    with col3:
        metric_card("Average Match", f"{avg_score}%", "Talent Pool average")

    with col4:
        metric_card(
            "Top Talent",
            f"{best_talent.get('talent_score', 0)}%",
            best_talent.get("name", "Unknown")
        )

    st.divider()

    section_title(
        "Talent Explorer",
        "Search, select and review consolidated Talent Profiles."
    )

    search = st.text_input(
        "Search talents",
        placeholder="Search by candidate name or recruitment..."
    )

    filtered_talents = _filter_talents(talents, search)

    if not filtered_talents:
        st.info("No talent matches your search.")
        return

    col_list, col_profile = st.columns([1, 2])

    with col_list:
        st.caption(f"{len(filtered_talents)} talent(s) found")

        options = [
            f"{talent.get('name', 'Unknown Candidate')} — {talent.get('talent_score', 0)}%"
            for talent in filtered_talents
        ]

        selected_option = st.radio(
            "Select a talent",
            options,
            label_visibility="collapsed"
        )

        selected_index = options.index(selected_option)
        selected_talent = filtered_talents[selected_index]

        st.divider()

        for talent in filtered_talents[:10]:
            st.write(f"**{talent.get('name', 'Unknown Candidate')}**")
            st.caption(
                f"Talent Score: {talent.get('talent_score', 0)}% · "
                f"Applications: {talent.get('application_count', 0)}"
            )
            st.divider()

    with col_profile:
        _render_talent_profile(selected_talent)
