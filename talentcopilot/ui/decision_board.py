from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.services.recruitment_workflow_state import (
    get_workflow_context,
    save_final_decision,
    select_workflow_candidate,
)
from talentcopilot.services.candidate_ordering import sort_by_official_rank
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_decision_board():
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()
    report = DecisionBoardService().build(session)

    enterprise_hero(
        "Decision Board",
        "Record a traceable final decision from canonical analysis and separately captured interview evidence.",
        "Decision flow",
    )

    if session is None or not report.candidates:
        if st.button("Load Enterprise Demo", key="decision_load_demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.rerun()
        st.info("Complete candidate analysis and finalist comparison before recording a decision.")
        return

    context = get_workflow_context(
        session,
        current_page="Decision Board",
    )

    finalists = set(
        context.finalist_candidate_ids
        or context.shortlisted_candidate_ids
    )

    candidates = [
        candidate
        for candidate in report.candidates
        if (
            not finalists
            or candidate.candidate_id in finalists
        )
    ]

    candidates = sort_by_official_rank(
        candidates
    )

    if len(candidates) < 1:
        st.warning(
            "No finalist is available. "
            "Return to Comparison and select "
            "finalists first."
        )
        return

    if not context.finalists_compared:
        st.warning(
            "The finalist comparison has not "
            "been confirmed yet. You can review "
            "evidence, but the final decision "
            "remains incomplete."
        )

    candidates_by_id = {
        candidate.candidate_id: candidate
        for candidate in candidates
        if candidate.candidate_id
    }

    option_ids = list(
        candidates_by_id
    )

    if not option_ids:
        st.error(
            "The finalist candidate identities "
            "could not be resolved."
        )
        return

    preferred_id = (
        context.final_decision_candidate_id
        if (
            context.final_decision_candidate_id
            in option_ids
        )
        else context.selected_candidate_id
        if (
            context.selected_candidate_id
            in option_ids
        )
        else option_ids[0]
    )

    selection_key = (
        "decision_candidate_id"
    )

    selection_context_key = (
        "decision_candidate_context"
    )

    selection_context = (
        str(
            getattr(
                session,
                "session_id",
                "session",
            )
        ),
        tuple(option_ids),
        preferred_id,
    )

    if (
        st.session_state.get(
            selection_context_key
        )
        != selection_context
    ):
        st.session_state[
            selection_context_key
        ] = selection_context

        st.session_state[
            selection_key
        ] = preferred_id

    elif (
        st.session_state.get(
            selection_key
        )
        not in option_ids
    ):
        st.session_state[
            selection_key
        ] = preferred_id

    candidate_id = st.selectbox(
        "Decision candidate",
        option_ids,
        key=selection_key,
        format_func=lambda selected_id: (
            f"#{candidates_by_id[selected_id].rank} "
            f"{candidates_by_id[selected_id].candidate_name}"
        ),
    )

    candidate_id = str(
        candidate_id
    )

    candidate = candidates_by_id[
        candidate_id
    ]

    select_workflow_candidate(
        candidate_id,
        candidate.candidate_name,
        source_widget_key=selection_key,
    )

    evaluation = (
        context.interview_evaluations.get(
            candidate_id,
            {},
        )
    )

    metric_grid([
        ("Candidate", candidate.candidate_name, f"Official rank #{candidate.rank}"),
        ("Official Match", f"{candidate.match_score:.0f}%", "Unchanged pre-interview score"),
        ("AI Recommendation", candidate.ai_recommendation, "Pre-interview decision signal"),
        ("Interview Evidence", f"{evaluation.get('evidence_coverage', 0)}%" if evaluation else "Not recorded", evaluation.get("recommendation", "Separate evidence layer")),
    ])

    insight_card(
        "Decision recommendation",
        f"Pre-interview recommendation: {candidate.ai_recommendation}. "
        f"Interview recommendation: {evaluation.get('recommendation', 'not recorded')}. "
        "Review the trade-offs and record a human-owned final decision below.",
        "Traceable decision",
    )

    with st.expander("Reasons, risks and stakeholder signals", expanded=True):
        section_title("Decision reasons")
        for reason in candidate.reasons:
            st.write(f"- **{reason.title}** — {reason.detail}")
        section_title("Unresolved risks")
        risks = list(evaluation.get("remaining_risks", [])) or [risk.detail for risk in candidate.risks]
        for risk in risks:
            st.warning(risk)
        section_title("Stakeholder matrix")
        st.dataframe([
            {"Stakeholder": item.stakeholder, "Recommendation": item.recommendation, "Confidence": item.confidence, "Comment": item.comment}
            for item in candidate.stakeholder_decisions
        ], use_container_width=True, hide_index=True)

    recommendation_options = ["Hire", "Proceed with conditions", "Hold", "Reject"]
    saved_recommendation = context.final_decision_recommendation
    recommendation_index = recommendation_options.index(saved_recommendation) if saved_recommendation in recommendation_options else 0
    recommendation = st.selectbox("Final recommendation", recommendation_options, index=recommendation_index, key="decision_final_recommendation")
    rationale = st.text_area(
        "Decision rationale",
        value=context.final_decision_rationale if context.final_decision_candidate_id == candidate_id else "",
        key=f"decision_rationale_{candidate_id}",
        height=150,
        placeholder="Record the decisive evidence, trade-offs, conditions and remaining risks.",
    )

    if st.button("Finalize decision", type="primary", key=f"decision_finalize_{candidate_id}", use_container_width=True):
        if not rationale.strip():
            st.error("Add a concise rationale before finalizing the decision.")
        else:
            save_final_decision(candidate_id, recommendation, rationale)
            st.success("Final decision recorded with traceability.")

    if context.decision_recorded:
        st.success(
            f"Decision recorded: {context.final_decision_recommendation} · "
            f"{context.final_decision_rationale}"
        )
