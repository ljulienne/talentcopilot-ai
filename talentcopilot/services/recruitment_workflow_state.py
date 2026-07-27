from __future__ import annotations

from typing import Any

from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService


WORKFLOW_CONTEXT_KEY = "talentcopilot_recruitment_workflow_context"


def get_workflow_context(session: Any = None, *, current_page: str = "") -> RecruitmentWorkflowContext:
    try:
        import streamlit as st
        existing = st.session_state.get(WORKFLOW_CONTEXT_KEY)
        if not isinstance(existing, RecruitmentWorkflowContext):
            existing = RecruitmentWorkflowContext()
        context = RecruitmentWorkflowService().build_context(
            session,
            existing,
            current_page=current_page,
        )
        st.session_state[WORKFLOW_CONTEXT_KEY] = context
        return context
    except Exception:
        return RecruitmentWorkflowService().build_context(
            session,
            RecruitmentWorkflowContext(),
            current_page=current_page,
        )


def save_workflow_context(context: RecruitmentWorkflowContext) -> RecruitmentWorkflowContext:
    try:
        import streamlit as st
        st.session_state[WORKFLOW_CONTEXT_KEY] = context
    except Exception:
        pass
    return context


def select_workflow_candidate(
    candidate_id: str,
    candidate_name: str = "",
    *,
    source_widget_key: str = "",
) -> None:
    """
    Synchronize the canonical workflow candidate.

    A widget that already exists in the current
    Streamlit run may reject a session-state
    assignment. Such a failure must not block
    synchronization of the other workspaces.
    """

    try:
        import streamlit as st
    except Exception:
        return

    context = st.session_state.get(
        WORKFLOW_CONTEXT_KEY
    )

    if not isinstance(
        context,
        RecruitmentWorkflowContext,
    ):
        context = (
            RecruitmentWorkflowContext()
        )

    candidate_id = str(
        candidate_id or ""
    )

    candidate_name = str(
        candidate_name or ""
    )

    context.select_candidate(
        candidate_id,
        candidate_name,
    )

    context.mark_completed(
        "candidate"
    )

    st.session_state[
        WORKFLOW_CONTEXT_KEY
    ] = context

    destination_keys = (
        "candidate_intelligence_candidate_id",
        "interview_intelligence_candidate_id",
    )

    for widget_key in destination_keys:
        if widget_key == source_widget_key:
            continue

        try:
            st.session_state[
                widget_key
            ] = candidate_id
        except Exception:
            continue


def save_interview_evaluation(candidate_id: str, evaluation: dict) -> RecruitmentWorkflowContext:
    context = get_workflow_context()
    key = str(candidate_id or "")
    if not key:
        return context
    context.interview_evaluations[key] = dict(evaluation or {})
    if key not in context.interview_assessed_candidate_ids:
        context.interview_assessed_candidate_ids.append(key)
    context.mark_completed("assess")
    return save_workflow_context(context)


def set_workflow_finalists(candidate_ids: list[str]) -> RecruitmentWorkflowContext:
    context = get_workflow_context()
    unique: list[str] = []
    for candidate_id in candidate_ids:
        value = str(candidate_id or "")
        if value and value not in unique:
            unique.append(value)
    context.shortlisted_candidate_ids = list(unique)
    context.finalist_candidate_ids = list(unique)
    return save_workflow_context(context)


def mark_finalists_compared() -> RecruitmentWorkflowContext:
    context = get_workflow_context()
    context.finalists_compared = True
    context.mark_completed("compare")
    return save_workflow_context(context)


def save_final_decision(candidate_id: str, recommendation: str, rationale: str) -> RecruitmentWorkflowContext:
    context = get_workflow_context()
    context.final_decision_candidate_id = str(candidate_id or "")
    context.final_decision_recommendation = str(recommendation or "")
    context.final_decision_rationale = str(rationale or "")
    context.decision_recorded = bool(context.final_decision_candidate_id and context.final_decision_rationale.strip())
    if context.decision_recorded:
        context.mark_completed("decide")
    return save_workflow_context(context)
