from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from talentcopilot.models.recruitment_workflow import RecruitmentWorkflowContext
from talentcopilot.services.recruitment_workflow_service import RecruitmentWorkflowService


WORKFLOW_CONTEXT_KEY = "talentcopilot_recruitment_workflow_context"


def _persist_current_project(context: RecruitmentWorkflowContext) -> None:
    """Persist workflow changes only after the recruiter explicitly saved a project."""

    try:
        from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
        from talentcopilot.services.recruitment_project_persistence import persist_project_best_effort

        persist_project_best_effort(get_streamlit_session(), context)
    except Exception:
        pass


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
    _persist_current_project(context)
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

    _persist_current_project(context)


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


def save_final_decision(
    candidate_id: str,
    recommendation: str,
    rationale: str,
    *,
    actor: str = "Recruiter",
    evidence: Iterable[str] | None = None,
    accepted_risks: Iterable[str] | None = None,
) -> RecruitmentWorkflowContext:
    """Record a human-owned final decision and append an immutable audit entry."""

    context = get_workflow_context()
    candidate_key = str(candidate_id or "")
    recommendation_value = str(recommendation or "")
    rationale_value = str(rationale or "")
    actor_value = str(actor or "Recruiter")
    evidence_values = _unique_strings(evidence)
    risk_values = _unique_strings(accepted_risks)
    timestamp = datetime.now(timezone.utc).isoformat()

    previous_recommendation = str(context.final_decision_recommendation or "")
    context.final_decision_candidate_id = candidate_key
    context.final_decision_recommendation = recommendation_value
    context.final_decision_rationale = rationale_value
    context.final_decision_actor = actor_value
    context.final_decision_timestamp = timestamp
    context.final_decision_evidence = list(evidence_values)
    context.final_decision_accepted_risks = list(risk_values)
    context.decision_recorded = bool(candidate_key and rationale_value.strip())

    if context.decision_recorded:
        context.mark_completed("decide")
        context.decision_history.append({
            "timestamp": timestamp,
            "actor": actor_value,
            "candidate_id": candidate_key,
            "recommendation": recommendation_value,
            "previous_recommendation": previous_recommendation,
            "rationale": rationale_value,
            "evidence": list(evidence_values),
            "accepted_risks": list(risk_values),
        })
    return save_workflow_context(context)


def _unique_strings(values: Iterable[str] | None) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        text = " ".join(str(value or "").split())
        key = text.casefold()
        if text and key not in seen:
            output.append(text)
            seen.add(key)
    return output
