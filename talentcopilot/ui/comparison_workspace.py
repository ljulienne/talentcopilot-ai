from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.compensation_budget_service import CompensationBudgetService
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.candidate_ordering import (
    order_candidate_ids,
    sort_by_official_rank,
)
from talentcopilot.services.recruitment_workflow_state import (
    get_workflow_context,
    mark_finalists_compared,
    set_workflow_finalists,
)
from talentcopilot.ui.design_system.components import page_header, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page


def _candidate_id_by_name(session):
    return {
        str(getattr(item, "candidate_name", "")): str(getattr(item, "candidate_id", ""))
        for item in getattr(session, "ranked_analyses", []) or []
    }


def _ranking_table(
    candidates,
    evaluations,
    ids_by_name,
    *,
    budget_by_name,
    expectations_by_id,
    workflow_context,
):
    import streamlit as st

    rows = []
    for candidate in candidates:
        candidate_id = ids_by_name.get(candidate.candidate_name, "")
        evaluation = evaluations.get(candidate_id, {})
        expectation = expectations_by_id.get(candidate_id)
        budget = budget_by_name.get(candidate.candidate_name)
        unresolved_risks = evaluation.get("remaining_risks", []) if isinstance(evaluation, dict) else []
        availability = "Not documented"
        if expectation is not None:
            availability = (
                getattr(expectation, "availability_date", "")
                or (
                    f"{int(getattr(expectation, 'notice_period_weeks', 0) or 0)} weeks notice"
                    if int(getattr(expectation, "notice_period_weeks", 0) or 0)
                    else "Not documented"
                )
            )
        final_recommendation = "Not recorded"
        if (
            workflow_context.decision_recorded
            and workflow_context.final_decision_candidate_id == candidate_id
        ):
            final_recommendation = workflow_context.final_decision_recommendation or "Recorded"

        rows.append({
            "Official Rank": candidate.mission_rank or candidate.rank,
            "Candidate": candidate.candidate_name,
            "Talent Fit": f"{candidate.match_score:.0f}%",
            "Evidence Confidence": (
                f"{candidate.ai_confidence:.0f}%"
                if candidate.ai_confidence is not None
                else "Not available"
            ),
            "Critical Risk": (unresolved_risks or [candidate.key_risk])[0],
            "Interview Assessment": evaluation.get("recommendation", "Not recorded"),
            "Compensation Fit": (
                getattr(budget, "budget_recommendation", "Pending compensation data")
                if budget is not None
                else "Pending compensation data"
            ),
            "Availability": availability,
            "Final Recommendation": final_recommendation,
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_comparison_workspace():
    import streamlit as st

    apply_enterprise_theme()
    service = ComparisonWorkspaceService()
    session = get_streamlit_session()
    report = service.build(session)

    page_header(
        "Compare & Decide",
        "Compare official evidence, interview findings and compensation context without altering the official ranking.",
        eyebrow="Recruitment · Final comparison",
        status="Human-owned decision",
    )

    if st.button(
        "← Back to Dashboard Perspective",
        key="comparison_back_dashboard",
        help="Return to the complete candidate portfolio.",
    ):
        request_page("Dashboard Perspective", reason="Returned to Dashboard Perspective from Compare & Decide.")
        st.rerun()


    if session is None or not report.candidates:
        if st.button("Load Enterprise Demo", key="comparison_load_demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.rerun()
        st.info("Create a recruitment and assess candidates before selecting finalists.")
        return

    context = get_workflow_context(session, current_page="Comparison")
    ids_by_name = _candidate_id_by_name(session)
    names_by_id = {
        candidate_id: name
        for name, candidate_id
        in ids_by_name.items()
        if candidate_id
    }

    ordered_candidates = sort_by_official_rank(
        report.candidates
    )

    available_ids = [
        ids_by_name.get(
            candidate.candidate_name,
            "",
        )
        for candidate in ordered_candidates
    ]

    available_ids = [
        candidate_id
        for candidate_id in available_ids
        if candidate_id
    ]

    default_pool = list(
        context.finalist_candidate_ids
        or context.shortlisted_candidate_ids
    )

    if len(default_pool) < 2:
        default_pool.extend(
            context.interview_assessed_candidate_ids
        )

    default_pool.extend(
        available_ids[:2]
    )

    default_ids = order_candidate_ids(
        default_pool,
        available_ids,
    )

    selection_key = (
        "comparison_finalist_candidate_ids"
    )

    stored_selection = (
        st.session_state.get(
            selection_key
        )
    )

    if isinstance(
        stored_selection,
        list,
    ):
        normalized_selection = (
            order_candidate_ids(
                stored_selection,
                available_ids,
            )
        )

        if (
            normalized_selection
            != stored_selection
        ):
            st.session_state[
                selection_key
            ] = normalized_selection

    raw_selected_ids = st.multiselect(
        "Finalists",
        options=available_ids,
        default=default_ids,
        format_func=lambda candidate_id: (
            names_by_id.get(
                candidate_id,
                candidate_id,
            )
        ),
        key=selection_key,
        help=(
            "Select at least two candidates. "
            "This does not alter official "
            "scores or ranks."
        ),
    )

    selected_ids = order_candidate_ids(
        raw_selected_ids,
        available_ids,
    )

    set_workflow_finalists(
        selected_ids
    )

    if len(selected_ids) < 2:
        st.warning("Select at least two finalists to unlock comparison and decision review.")
        return

    selected_candidates = [
        candidate
        for candidate in ordered_candidates
        if ids_by_name.get(
            candidate.candidate_name,
            "",
        ) in selected_ids
    ]

    metric_grid([
        ("Role", report.role_title, "Active recruitment"),
        ("Finalists", str(len(selected_candidates)), "Selected for comparison"),
        ("Interview assessments", str(sum(1 for item in selected_ids if item in context.interview_evaluations)), "Saved evidence"),
        ("Official ranking", "Preserved", "No score or rank recomputation"),
    ])

    compensation_service = CompensationBudgetService()
    budget_report = HiringBudgetService().build(
        session,
        compensation_service.load_budget(session),
    )
    budget_by_name = {
        str(getattr(item, "candidate_name", "")): item
        for item in list(getattr(budget_report, "assessments", []) or [])
    }
    expectations_by_id = {
        candidate_id: compensation_service.load_expectation(
            session,
            candidate_id=candidate_id,
            candidate_name=names_by_id.get(candidate_id, "Candidate"),
        )
        for candidate_id in available_ids
    }
    export = RecruitmentPdfService().comparison(
        report,
        context.interview_evaluations,
        compensation_report=budget_report,
        expectations=expectations_by_id,
        workflow_context=context,
    )
    export_col, budget_col = st.columns([1.15, 1])
    with export_col:
        st.download_button(
            "Download decision report (PDF)",
            data=export.data,
            file_name=export.file_name,
            mime=export.mime,
            key="comparison_decision_pdf",
            use_container_width=True,
        )
    with budget_col:
        if st.button(
            "Review Compensation & Budget",
            key="comparison_open_compensation",
            use_container_width=True,
        ):
            request_page(
                "Compensation & Budget",
                reason="Review compensation scenarios before the final decision.",
            )
            st.rerun()

    missing = [names_by_id[item] for item in selected_ids if item not in context.interview_evaluations]
    if missing:
        st.warning("Interview evidence is still missing for: " + ", ".join(missing))
    else:
        st.success("Interview evidence is available for every selected finalist.")

    section_title(
        "Decision comparison",
        "Talent Fit, evidence confidence, risks, interview, compensation and availability remain independent decision signals.",
    )
    _ranking_table(
        selected_candidates,
        context.interview_evaluations,
        ids_by_name,
        budget_by_name=budget_by_name,
        expectations_by_id=expectations_by_id,
        workflow_context=context,
    )

    with st.expander("Pre-interview score gaps and differentiators"):
        for gap in report.score_gaps:
            st.metric(gap.label, f"{gap.value:.1f} pts", gap.interpretation)
        for item in report.differentiators:
            st.write(f"- {item}")

    if st.button("Confirm comparison and open Decision Board →", type="primary", key="comparison_open_decision", use_container_width=True):
        mark_finalists_compared()
        request_page("Decision Board", reason="Finalist comparison confirmed. Record the final decision.")
        st.rerun()
