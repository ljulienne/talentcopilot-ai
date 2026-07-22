from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.services.recruitment_workflow_state import get_workflow_context, save_final_decision
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _candidate_id_by_name(session):
    return {
        str(getattr(item, "candidate_name", "")): str(getattr(item, "candidate_id", ""))
        for item in getattr(session, "ranked_analyses", []) or []
    }


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

    context = get_workflow_context(session, current_page="Decision Board")
    ids_by_name = _candidate_id_by_name(session)
    finalists = set(context.finalist_candidate_ids or context.shortlisted_candidate_ids)
    candidates = [item for item in report.candidates if not finalists or ids_by_name.get(item.candidate_name) in finalists]

    if len(candidates) < 1:
        st.warning("No finalist is available. Return to Comparison and select finalists first.")
        return
    if not context.finalists_compared:
        st.warning("The finalist comparison has not been confirmed yet. You can review evidence, but the final decision remains incomplete.")

    names = [item.candidate_name for item in candidates]
    default_index = 0
    if context.final_decision_candidate_id:
        selected_name = next((name for name in names if ids_by_name.get(name) == context.final_decision_candidate_id), None)
        if selected_name:
            default_index = names.index(selected_name)
    selected = st.selectbox("Decision candidate", names, index=default_index, key="decision_candidate_name")
    candidate = candidates[names.index(selected)]
    candidate_id = ids_by_name.get(selected, "")
    evaluation = context.interview_evaluations.get(candidate_id, {})

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
