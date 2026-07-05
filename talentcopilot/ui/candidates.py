
import streamlit as st

from talentcopilot.i18n import tr

from talentcopilot.ui.cards import render_decision_header
from talentcopilot.ui.design_system import render_risk_card, render_interview_focus_card

from talentcopilot.services.ranking_service import rank_candidates

from talentcopilot.ui.components import section_title, metric_card, assistant_panel, candidate_card


def render_candidates():
    st.markdown(f"""
    <div class="tc-hero">
        <h1>👥 {tr('candidates.title')}</h1>
        <h3>{tr('candidates.subtitle')}</h3>
        <p class="tc-muted">
        {tr('candidates.subtitle')}
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
        metric_card(tr("candidates.total"), len(results), "Analyzed profiles")

    with col2:
        metric_card(tr("candidates.top_score"), f"{top_match.overall_score}%", top_candidate["candidate"].name, "#10B981")

    with col3:
        metric_card(tr("candidates.top_confidence"), f"{top_match.confidence_score}%", "Highest ranked profile")

    assistant_panel(
        "Recruiter Copilot",
        "Review the candidate cards below, then use Candidate Comparison to compare your shortlist side by side."
    )

    st.divider()

    section_title(tr("candidates.list_title"), tr("candidates.list_subtitle"))

    for index, item in enumerate(results, start=1):
        candidate = item["candidate"]
        match = item["match_result"]

        col1, col2 = st.columns([1, 4])

        with col1:
            st.subheader(f"#{index}")

        with col2:
            render_decision_header(
                candidate_decision=item.get("candidate_decision"),
                match_result=match,
                rank=item.get("rank", index)
            )

            candidate_card(candidate.name, match.overall_score, match.recommendation)
            weighted = item.get("weighted_ranking", {})
            official_score = weighted.get("weighted_ranking_score", match.overall_score)

            st.caption(
                f"Weighted Ranking Score: {official_score}% | "
                f"Match Score: {match.overall_score}% | "
                f"Confidence: {match.confidence_score}% | "
                f"File: {item['file']}"
            )

            st.write(match.executive_summary)

            if weighted:
                with st.expander("⚖️ Why this rank?", expanded=False):
                    st.write(weighted.get("explanation", ""))

                    criteria = weighted.get("criteria", {})
                    weights = weighted.get("weights", {})

                    for key, score in criteria.items():
                        weight = weights.get(key, 0)
                        contribution = round(score * weight, 1)
                        label = key.replace("_", " ").title()

                        st.write(
                            f"**{label}**: {score}% × {round(weight * 100)}% = {contribution}"
                        )

                    st.caption(
                        "The official ranking score is calculated from weighted criteria. "
                        "This makes the ranking more explainable than a single raw match score."
                    )

            intelligence = item.get("candidate_intelligence")
            if intelligence:
                with st.expander("🧠 Candidate Intelligence", expanded=False):
                    st.write(f"**Readiness:** {intelligence.get('readiness', '-')}")
                    st.write(f"**Why:** {intelligence.get('why', '-')}")

                    st.write("**Strengths**")
                    for strength in intelligence.get("strengths", []):
                        st.write(f"✅ {strength}")

                    render_risk_card(intelligence.get("risk_factors", []))

                    st.write("**Development areas**")
                    for area in intelligence.get("development_areas", []):
                        st.write(f"⚠️ {area}")

                    decision = item.get("candidate_decision")
                    if decision:
                        render_interview_focus_card(decision.interview_plan)
                    else:
                        st.write("**Interview focus**")
                        for focus in intelligence.get("interview_focus", []):
                            st.write(f"🎯 {focus}")

        st.divider()
