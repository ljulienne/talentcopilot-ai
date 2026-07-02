import streamlit as st

from talentcopilot.talent_pool.talent_metrics import enrich_talent_profiles
from talentcopilot.talent_pool.talent_store import list_talent_profiles
from talentcopilot.ui.components import section_title, assistant_panel, metric_card
from talentcopilot.ui.talent_profile.financial import render_financial
from talentcopilot.ui.talent_profile.history import render_history
from talentcopilot.ui.talent_profile.interview import render_interview
from talentcopilot.ui.talent_profile.overview import render_overview
from talentcopilot.ui.talent_profile.skills import render_skills


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


def _render_talent_profile(talent):
    name = talent.get("name", "Unknown Candidate")

    st.markdown(f"""
    <div class="tc-hero">
        <h1>👤 {name}</h1>
        <h3>Talent Intelligence Profile</h3>
        <p class="tc-muted">
        Consolidated profile based on all recruitment analyses involving this talent.
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_overview(talent)

    st.divider()
    render_skills(talent)

    st.divider()
    render_interview(talent)

    st.divider()
    render_financial(talent)

    st.divider()
    render_history(talent)

    st.divider()
    assistant_panel(
        "TalentCopilot Assessment",
        "This profile consolidates performance, recruitment history, detected skills, interview guidance and financial simulation. Future versions will add AI-powered offer recommendations, interview notes and career fit analysis.",
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
            "No talent profile found yet. Analyze and save a recruitment to automatically populate the Talent Pool.",
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
            best_talent.get("name", "Unknown"),
        )

    st.divider()

    section_title(
        "Talent Explorer",
        "Search, select and review consolidated Talent Profiles.",
    )

    search = st.text_input(
        "Search talents",
        placeholder="Search by candidate name or recruitment...",
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
            label_visibility="collapsed",
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
