from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.services.recruitment_workflow_state import (
    get_workflow_context,
    mark_finalists_compared,
    set_workflow_finalists,
)
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page


def _candidate_id_by_name(session):
    return {
        str(getattr(item, "candidate_name", "")): str(getattr(item, "candidate_id", ""))
        for item in getattr(session, "ranked_analyses", []) or []
    }


def _ranking_table(candidates, evaluations, ids_by_name):
    import streamlit as st
    rows = []
    for candidate in candidates:
        candidate_id = ids_by_name.get(candidate.candidate_name, "")
        evaluation = evaluations.get(candidate_id, {})
        rows.append({
            "Mission Rank": candidate.mission_rank or candidate.rank,
            "Candidate": candidate.candidate_name,
            "Official Mission Fit": candidate.match_score,
            "AI Confidence": candidate.ai_confidence,
            "Pre-interview recommendation": candidate.recommendation,
            "Interview recommendation": evaluation.get("recommendation", "Not recorded"),
            "Interview evidence": f"{evaluation.get('evidence_coverage', 0)}%" if evaluation else "—",
            "Key Strength": candidate.key_strength,
            "Unresolved Risk": (evaluation.get("remaining_risks") or [candidate.key_risk])[0],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_comparison_workspace():
    import streamlit as st

    apply_enterprise_theme()
    service = ComparisonWorkspaceService()
    session = get_streamlit_session()
    report = service.build(session)

    enterprise_hero(
        "Finalist Comparison",
        "Compare canonical pre-interview evidence with separately recorded interview findings.",
        "Decision flow",
    )

    if session is None or not report.candidates:
        if st.button("Load Enterprise Demo", key="comparison_load_demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.rerun()
        st.info("Create a recruitment and assess candidates before selecting finalists.")
        return

    context = get_workflow_context(session, current_page="Comparison")
    ids_by_name = _candidate_id_by_name(session)
    names_by_id = {candidate_id: name for name, candidate_id in ids_by_name.items() if candidate_id}
    available_ids = [ids_by_name.get(candidate.candidate_name, "") for candidate in report.candidates]
    available_ids = [item for item in available_ids if item]
    default_ids = [item for item in (context.finalist_candidate_ids or context.shortlisted_candidate_ids) if item in available_ids]
    if len(default_ids) < 2:
        assessed = [item for item in context.interview_assessed_candidate_ids if item in available_ids]
        default_ids = list(dict.fromkeys(assessed + available_ids[:2]))[:2]

    selected_ids = st.multiselect(
        "Finalists",
        options=available_ids,
        default=default_ids,
        format_func=lambda candidate_id: names_by_id.get(candidate_id, candidate_id),
        key="comparison_finalist_candidate_ids",
        help="Select at least two candidates. This does not alter official scores or ranks.",
    )
    set_workflow_finalists(selected_ids)

    if len(selected_ids) < 2:
        st.warning("Select at least two finalists to unlock comparison and decision review.")
        return

    selected_names = {names_by_id[item] for item in selected_ids if item in names_by_id}
    selected_candidates = [item for item in report.candidates if item.candidate_name in selected_names]

    metric_grid([
        ("Role", report.role_title, "Active recruitment"),
        ("Finalists", str(len(selected_candidates)), "Selected for comparison"),
        ("Interview assessments", str(sum(1 for item in selected_ids if item in context.interview_evaluations)), "Saved evidence"),
        ("Official ranking", "Preserved", "No score or rank recomputation"),
    ])

    missing = [names_by_id[item] for item in selected_ids if item not in context.interview_evaluations]
    if missing:
        st.warning("Interview evidence is still missing for: " + ", ".join(missing))
    else:
        st.success("Interview evidence is available for every selected finalist.")

    section_title("Decision comparison", "Official Mission Fit remains unchanged; interview evidence is displayed separately.")
    _ranking_table(selected_candidates, context.interview_evaluations, ids_by_name)

    with st.expander("Pre-interview score gaps and differentiators"):
        for gap in report.score_gaps:
            st.metric(gap.label, f"{gap.value:.1f} pts", gap.interpretation)
        for item in report.differentiators:
            st.write(f"- {item}")

    if st.button("Confirm comparison and open Decision Board →", type="primary", key="comparison_open_decision", use_container_width=True):
        mark_finalists_compared()
        request_page("Decision Board", reason="Finalist comparison confirmed. Record the final decision.")
        st.rerun()
