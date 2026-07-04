import streamlit as st

from talentcopilot.talent_pool.talent_metrics import enrich_talent_profiles
from talentcopilot.talent_pool.talent_store import list_talent_profiles
from talentcopilot.services.ranking_service import rank_candidates
from talentcopilot.ui.candidate_workspace import render_candidate_workspace
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


def render_talent_pool():
    st.markdown("""
    <div class="tc-hero">
        <h1>👥 Talent Intelligence</h1>
        <h3>Enterprise Talent Workspace</h3>
        <p class="tc-muted">
        Search, select and open consolidated Candidate Workspaces.
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

    talents = rank_candidates(enrich_talent_profiles(raw_talents))

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
        metric_card("Average Match", f"{avg_score}%", "Talent average")

    with col4:
        metric_card(
            "Top Talent",
            f"{best_talent.get('talent_score', 0)}%",
            best_talent.get("name", "Unknown"),
        )

    st.divider()

    section_title(
        "Talent Explorer",
        "Search a talent and open the Candidate Workspace."
    )

    search = st.text_input(
        "Search talents",
        placeholder="Search by candidate name, recruitment or profile key...",
    )

    filtered_talents = rank_candidates(_filter_talents(talents, search))

    if not filtered_talents:
        st.info("No talent matches your search.")
        return

    col_list, col_workspace = st.columns([1, 2.4])

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
            st.markdown(
                f"""
                <div class="tc-card">
                    <strong>{talent.get('name', 'Unknown Candidate')}</strong><br>
                    <span class="tc-muted">
                    Talent Score: {talent.get('talent_score', 0)}% · 
                    Applications: {talent.get('application_count', 0)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_workspace:
        render_candidate_workspace(selected_talent)
