from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from talentcopilot.models.recruitment_workflow import (
    RecruitmentWorkflowContext,
    WorkflowStepState,
)
from talentcopilot.services.recruitment_experience_architecture import WORKFLOW


PAGE_TO_STEP = {
    "Recruitment Workspace": "analysis",
    "Candidate Intelligence": "candidate",
    "Interview Intelligence": "prepare",
    "Comparison": "compare",
    "Decision Board": "decide",
}

STEP_PRIMARY_ACTIONS = {
    "setup": "Create recruitment",
    "role": "Add job description",
    "candidates": "Add candidates",
    "analysis": "Review candidate shortlist",
    "candidate": "Prepare interview",
    "prepare": "Open interview playbook",
    "assess": "Save assessment and compare",
    "compare": "Open decision board",
    "decide": "Finalize recommendation",
}


class RecruitmentWorkflowService:
    """Resolve a deterministic workflow shell from the canonical session.

    This presentation service never changes scores, ranking or analysis output.
    It only derives navigation state from existing recruitment data and explicit
    user-completion markers stored in the workflow context.
    """

    def build_context(
        self,
        session: Any,
        existing: RecruitmentWorkflowContext | None = None,
        *,
        current_page: str = "",
    ) -> RecruitmentWorkflowContext:
        context = existing or RecruitmentWorkflowContext()
        if session is not None:
            context.session_id = str(getattr(session, "session_id", "") or "")
            context.role_title = str(getattr(session, "role_title", "Recruitment") or "Recruitment")

        if current_page:
            context.last_page = current_page

        states = self.resolve_steps(session, context, current_page=current_page)
        current = next((item for item in states if item.current), states[0])
        context.current_step = current.key
        context.completed_steps = [item.key for item in states if item.completed]
        next_state = self.next_step(states)
        context.next_page = next_state.page_label if next_state else current.page_label
        return context

    def resolve_steps(
        self,
        session: Any,
        context: RecruitmentWorkflowContext | None = None,
        *,
        current_page: str = "",
    ) -> list[WorkflowStepState]:
        context = context or RecruitmentWorkflowContext()
        explicit = set(context.completed_steps)

        has_session = session is not None
        job = getattr(session, "job", {}) or {} if has_session else {}
        has_role = bool(str(job.get("title", "") or "").strip() or job.get("description") or job.get("raw_text"))
        candidates = list(getattr(session, "candidates", []) or []) if has_session else []
        analyses = list(getattr(session, "analyses", []) or []) if has_session else []
        analyzed_count = int(getattr(session, "analyzed_count", 0) or 0) if has_session else 0
        analysis_complete = bool(candidates) and analyzed_count >= len(candidates)
        has_selected = bool(context.selected_candidate_id or context.selected_candidate_name)
        interview_prepared = bool(context.interview_prepared_candidate_ids)
        interview_assessed = bool(context.interview_assessed_candidate_ids)
        finalist_count = len(context.finalist_candidate_ids or context.shortlisted_candidate_ids)

        completion = {
            "setup": has_session,
            "role": has_session and has_role,
            "candidates": has_session and bool(candidates),
            "analysis": has_session and analysis_complete,
            "candidate": has_selected or "candidate" in explicit,
            "prepare": interview_prepared or "prepare" in explicit,
            "assess": interview_assessed or "assess" in explicit,
            "compare": (context.finalists_compared and finalist_count >= 2) or "compare" in explicit,
            "decide": context.decision_recorded or "decide" in explicit,
        }

        prerequisite_reason = {
            "setup": "Create or load a recruitment to begin.",
            "role": "Add a job description before candidate analysis.",
            "candidates": "Upload at least one candidate.",
            "analysis": "Complete candidate analysis before deep review.",
            "candidate": "Select and review a candidate.",
            "prepare": "Select a candidate before preparing the interview.",
            "assess": "Prepare the interview before recording findings.",
            "compare": "Select at least two finalists and save interview evidence before comparison.",
            "decide": "Compare finalists before recording the decision.",
        }

        first_incomplete = next((step.key for step in WORKFLOW if not completion[step.key]), WORKFLOW[-1].key)
        requested_step = PAGE_TO_STEP.get(current_page, "")
        current_key = requested_step or first_incomplete

        states: list[WorkflowStepState] = []
        previous_complete = True
        for step in WORKFLOW:
            available = previous_complete or step.key == first_incomplete
            completed = bool(completion[step.key])
            current = step.key == current_key
            reason = "" if available else prerequisite_reason.get(step.key, "Complete previous steps first.")
            states.append(
                WorkflowStepState(
                    key=step.key,
                    label=step.label,
                    page_label=step.target_page,
                    completed=completed,
                    current=current,
                    available=available,
                    reason=reason,
                )
            )
            previous_complete = previous_complete and completed
        return states

    @staticmethod
    def next_step(states: Iterable[WorkflowStepState]) -> WorkflowStepState | None:
        states = list(states)
        current_index = next((i for i, item in enumerate(states) if item.current), -1)
        for item in states[current_index + 1 :]:
            if item.available and not item.completed:
                return item
        return next((item for item in states if not item.completed and item.available), None)

    @staticmethod
    def previous_step(states: Iterable[WorkflowStepState]) -> WorkflowStepState | None:
        states = list(states)
        current_index = next((i for i, item in enumerate(states) if item.current), -1)
        if current_index <= 0:
            return None
        for item in reversed(states[:current_index]):
            if item.available:
                return item
        return None

    @staticmethod
    def primary_action(context: RecruitmentWorkflowContext) -> str:
        return STEP_PRIMARY_ACTIONS.get(context.current_step, "Continue")

    @staticmethod
    def candidate_options(session: Any) -> list[tuple[str, str]]:
        options: list[tuple[str, str]] = []
        seen: set[str] = set()
        for analysis in list(getattr(session, "ranked_analyses", []) or []):
            candidate_id = str(getattr(analysis, "candidate_id", "") or getattr(analysis, "candidate_name", ""))
            candidate_name = str(getattr(analysis, "candidate_name", "") or candidate_id)
            if candidate_id and candidate_id not in seen:
                options.append((candidate_id, candidate_name))
                seen.add(candidate_id)
        return options
