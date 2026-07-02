import streamlit as st

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

    talents = list_talent_profiles()

    if not talents:
        assistant_panel(
            "Talent Intelligence",
            "No talent profile found yet. Analyze and save a recruitment to automatically populate the Talent Pool."
        )
        return

    total_talents = len(talents)
    total_applications = sum(talent.get("application_count", 0) for talent in talents)
    avg_score = round(
        sum(talent.get("average_score", 0) for talent in talents) / total_talents
    ) if total_talents else 0
    best_talent = max(talents, key=lambda talent: talent.get("highest_score", 0))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Talents", total_talents, "Consolidated profiles")

    with col2:
        metric_card("Applications", total_applications, "Across recruitments")

    with col3:
        metric_card("Average Match", f"{avg_score}%", "Talent Pool average")

    with col4:
        metric_card(
            "Best Match",
            f"{best_talent.get('highest_score', 0)}%",
            best_talent.get("name", "Unknown")
        )

    st.divider()

    section_title(
        "Search Talent Pool",
        "Find talents by name, recruitment history or profile key."
    )

    search = st.text_input(
        "Search talents",
        placeholder="Search by candidate name or recruitment..."
    )

    filtered_talents = _filter_talents(talents, search)

    st.caption(f"{len(filtered_talents)} talent(s) found")

    st.divider()

    for talent in filtered_talents:
        name = talent.get("name", "Unknown Candidate")
        application_count = talent.get("application_count", 0)
        average_score = talent.get("average_score", 0)
        highest_score = talent.get("highest_score", 0)
        average_confidence = talent.get("average_confidence", 0)
        last_recruitment = talent.get("last_recruitment_title", "-")

        with st.container():
            col_profile, col_score, col_history = st.columns([3, 2, 3])

            with col_profile:
                st.subheader(name)
                st.caption(talent.get("candidate_key", ""))
                st.write(f"Latest recruitment: **{last_recruitment}**")

            with col_score:
                metric_card("Average Match", f"{average_score}%", "Across applications")
                metric_card("Best Match", f"{highest_score}%", "Highest recorded score")

            with col_history:
                metric_card("Applications", application_count, "Recruitment history")
                metric_card("Avg Confidence", f"{average_confidence}%", "AI confidence")

            with st.expander(f"View history — {name}"):
                history = talent.get("application_history", [])

                if not history:
                    st.info("No application history available.")
                else:
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

            st.divider()
