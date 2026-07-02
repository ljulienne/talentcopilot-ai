import streamlit as st

from talentcopilot.ui.components import metric_card, section_title


def render_overview(talent):
    talent_score = talent.get("talent_score", 0)
    progression = talent.get("progression_trend", "Not enough history")
    best_application = talent.get("best_application")

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
            "Most recent context",
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
