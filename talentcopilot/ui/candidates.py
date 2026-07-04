
import streamlit as st

from talentcopilot.services.ranking_service import rank_candidates

from talentcopilot.ui.components import section_title, metric_card, assistant_panel, candidate_card


def render_candidates():
    st.markdown("""
    <div class="tc-hero">
        <h1>👥 Candidates</h1>
        <h3>Candidate workspace</h3>
        <p class="tc-muted">
        Review analyzed candidates, scores, recommendations and confidence levels.
        </p>
    </div>
    """, unsafe_allow_html=True)

    batch = st.session_state.get("analysis_batch")

    if not batch:
        st.info("Run an analysis first from the Dashboard.")
        return

    results = batch.get("results", [])

    if not results:
        st.warning("No candidates available.")
        return

    top_candidate = results[0]
    top_match = top_candidate["match_result"]

    section_title("Candidate Overview", "Summary of analyzed profiles.")

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Candidates", len(results), "Analyzed profiles")

    with col2:
        metric_card("Top Score", f"{top_match.overall_score}%", top_candidate["candidate"].name, "#10B981")

    with col3:
        metric_card("Top Confidence", f"{top_match.confidence_score}%", "Highest ranked profile")

    assistant_panel(
        "Recruiter Copilot",
        "Review the candidate cards below, then use Candidate Comparison to compare your shortlist side by side."
    )

    st.divider()

    section_title("Candidate List", "Ranked by TalentCopilot match score.")

    for index, item in enumerate(results, start=1):
        candidate = item["candidate"]
        match = item["match_result"]

        col1, col2 = st.columns([1, 4])

        with col1:
            st.subheader(f"#{index}")

        with col2:
            candidate_card(candidate.name, match.overall_score, match.recommendation)
            st.caption(f"Confidence: {match.confidence_score}% | File: {item['file']}")
            st.write(match.executive_summary)

        st.divider()
