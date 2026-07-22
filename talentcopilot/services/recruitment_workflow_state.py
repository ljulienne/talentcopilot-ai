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


def select_workflow_candidate(candidate_id: str, candidate_name: str = "") -> None:
    try:
        import streamlit as st
        context = st.session_state.get(WORKFLOW_CONTEXT_KEY)
        if not isinstance(context, RecruitmentWorkflowContext):
            context = RecruitmentWorkflowContext()
        context.select_candidate(candidate_id, candidate_name)
        context.mark_completed("candidate")
        st.session_state[WORKFLOW_CONTEXT_KEY] = context
        st.session_state["candidate_intelligence_candidate_id"] = candidate_id
        st.session_state["interview_intelligence_candidate_id"] = candidate_id
    except Exception:
        pass
