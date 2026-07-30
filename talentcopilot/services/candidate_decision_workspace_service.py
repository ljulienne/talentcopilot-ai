"""Build the consolidated candidate decision workspace from stored product data.

This service is presentation-only. It never recalculates official Talent Fit,
official rank, matching, recommendation engines or interview results.
"""

from __future__ import annotations

from typing import Any, Optional

from talentcopilot.models.candidate_decision_workspace import (
    CandidateDecisionWorkspaceView,
    DecisionJourneyStage,
    RequirementDecisionLine,
)
from talentcopilot.services.compensation_budget_service import CompensationBudgetService
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService
from talentcopilot.services.hiring_budget_service import HiringBudgetService


class CandidateDecisionWorkspaceService:
    def __init__(
        self,
        *,
        competency_service: Any | None = None,
        compensation_service: Any | None = None,
        budget_service: Any | None = None,
    ) -> None:
        self.competency_service = competency_service or CompetencyMatrixService()
        self.compensation_service = compensation_service or CompensationBudgetService()
        self.budget_service = budget_service or HiringBudgetService()

    def build(
        self,
        report: Any,
        session: Any,
        workflow_context: Any,
        decision_brief: Any | None = None,
    ) -> CandidateDecisionWorkspaceView:
        candidate_id = str(
            getattr(report, "candidate_id", "")
            or getattr(report, "candidate_name", "Candidate")
        )
        candidate_name = str(getattr(report, "candidate_name", "Candidate") or "Candidate")
        role_title = str(getattr(session, "role_title", "Recruitment") or "Recruitment")

        official_score = float(
            getattr(report, "official_match_score", None)
            or getattr(report, "match_score", 0.0)
            or 0.0
        )
        official_rank = int(
            getattr(report, "official_rank", None)
            or getattr(report, "rank", 0)
            or 0
        )

        matrix = self.competency_service.build(report, session)
        requirements = tuple(
            self._requirement_line(item)
            for item in matrix.active_competencies()
            if bool(getattr(item, "is_job_requirement", False))
        )

        evaluations = dict(getattr(workflow_context, "interview_evaluations", {}) or {})
        evaluation = evaluations.get(candidate_id, {})
        if not isinstance(evaluation, dict):
            evaluation = {}

        assessed_ids = set(
            str(value)
            for value in getattr(workflow_context, "interview_assessed_candidate_ids", []) or []
        )
        prepared_ids = set(
            str(value)
            for value in getattr(workflow_context, "interview_prepared_candidate_ids", []) or []
        )
        has_post_level = any(line.post_interview_level is not None for line in requirements)
        if candidate_id in assessed_ids or evaluation or str(getattr(matrix, "status", "")) == "post_interview":
            interview_status = "Completed"
        elif candidate_id in prepared_ids or has_post_level or str(getattr(matrix, "status", "")) == "interview_in_progress":
            interview_status = "In progress"
        else:
            interview_status = "Not started"

        interview_recommendation = self._clean(
            evaluation.get("recommendation"),
            "Not recorded",
        )
        interview_coverage = self._optional_int(evaluation.get("evidence_coverage"))

        expectation = self.compensation_service.load_expectation(
            session,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
        )
        budget = self.compensation_service.load_budget(session)
        budget_report = self.budget_service.build(session, budget)
        assessment = next(
            (
                item
                for item in list(getattr(budget_report, "assessments", []) or [])
                if str(getattr(item, "candidate_name", "")).casefold()
                == candidate_name.casefold()
            ),
            None,
        )

        compensation_status = "Documented" if bool(getattr(expectation, "documented", False)) else "Not documented"
        compensation_fit = self._clean(
            getattr(assessment, "budget_recommendation", "") if assessment is not None else "",
            "Pending compensation data" if compensation_status == "Not documented" else "Review required",
        )
        expected_salary = self._optional_float(getattr(expectation, "expected_salary", None))
        if expected_salary is not None and expected_salary <= 0:
            expected_salary = None

        is_final_candidate = (
            bool(getattr(workflow_context, "decision_recorded", False))
            and str(getattr(workflow_context, "final_decision_candidate_id", "") or "")
            == candidate_id
        )
        final_status = "Recorded" if is_final_candidate else "Pending"
        final_recommendation = self._clean(
            getattr(workflow_context, "final_decision_recommendation", "") if is_final_candidate else "",
            "Not recorded",
        )
        final_rationale = self._clean(
            getattr(workflow_context, "final_decision_rationale", "") if is_final_candidate else "",
            "",
        )
        final_actor = self._clean(
            getattr(workflow_context, "final_decision_actor", "") if is_final_candidate else "",
            "",
        )
        final_timestamp = self._clean(
            getattr(workflow_context, "final_decision_timestamp", "") if is_final_candidate else "",
            "",
        )

        confidence = self._confidence(report, decision_brief)
        evidence_coverage = self._optional_int(
            getattr(decision_brief, "evidence_coverage", None)
            if decision_brief is not None
            else None
        )

        pre_recommendation = self._clean(
            getattr(decision_brief, "recommendation_label", "") if decision_brief is not None else "",
            self._clean(
                getattr(report, "recommendation_label", "")
                or getattr(report, "recommendation", ""),
                "Human validation required",
            ),
        )

        strengths = self._unique(
            getattr(decision_brief, "strengths", ()) if decision_brief is not None else ()
        )
        if not strengths:
            strengths = self._unique(
                getattr(skill, "name", "")
                for skill in list(getattr(report, "skills", []) or [])
                if float(getattr(skill, "level", 0) or 0) >= 70
            )

        risks = self._unique(
            self._risk_text(item)
            for item in list(getattr(report, "risks", []) or [])
        )
        interview_priorities = self._unique(
            getattr(decision_brief, "interview_priorities", ())
            if decision_brief is not None
            else getattr(report, "interview_focus", ())
        )

        history = tuple(
            dict(entry)
            for entry in list(getattr(workflow_context, "decision_history", []) or [])
            if isinstance(entry, dict)
            and str(entry.get("candidate_id", "") or "") == candidate_id
        )

        journey = (
            DecisionJourneyStage(
                key="pre_interview",
                label="Pre-interview assessment",
                status="Available",
                recommendation=pre_recommendation,
                evidence_note=(
                    f"Official Talent Fit {official_score:.0f}% · official rank #{official_rank}."
                ),
            ),
            DecisionJourneyStage(
                key="interview",
                label="Interview evidence",
                status=interview_status,
                recommendation=interview_recommendation,
                evidence_note=(
                    f"Evidence coverage {interview_coverage}%"
                    if interview_coverage is not None
                    else "No saved interview evidence yet."
                ),
            ),
            DecisionJourneyStage(
                key="final_decision",
                label="Human decision",
                status=final_status,
                recommendation=final_recommendation,
                evidence_note=final_rationale or "Final rationale has not been recorded.",
            ),
        )

        return CandidateDecisionWorkspaceView(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            role_title=role_title,
            official_rank=official_rank,
            official_match_score=official_score,
            confidence_score=confidence,
            evidence_coverage=evidence_coverage,
            pre_interview_recommendation=pre_recommendation,
            interview_status=interview_status,
            interview_recommendation=interview_recommendation,
            interview_evidence_coverage=interview_coverage,
            compensation_status=compensation_status,
            compensation_fit=compensation_fit,
            currency=str(getattr(expectation, "currency", "EUR") or "EUR"),
            expected_salary=expected_salary,
            availability_date=self._clean(getattr(expectation, "availability_date", ""), "Not documented"),
            notice_period_weeks=int(getattr(expectation, "notice_period_weeks", 0) or 0),
            flexibility=self._clean(getattr(expectation, "flexibility", ""), "Unknown"),
            final_decision_status=final_status,
            final_decision_recommendation=final_recommendation,
            final_decision_rationale=final_rationale,
            final_decision_actor=final_actor,
            final_decision_timestamp=final_timestamp,
            requirements=requirements,
            strengths=tuple(strengths[:5]),
            risks=tuple(risks[:5]),
            interview_priorities=tuple(interview_priorities[:5]),
            journey=journey,
            decision_history=history,
        )

    def _requirement_line(self, item: Any) -> RequirementDecisionLine:
        required = float(getattr(item, "required_level", 0.0) or 0.0)
        pre = float(getattr(item, "ai_estimated_level", 0.0) or 0.0)
        post_raw = getattr(item, "interviewer_level", None)
        post = self._optional_float(post_raw)
        effective = post if post is not None else pre
        gap = effective - required
        if gap >= 0:
            status = "Demonstrated"
        elif gap >= -1:
            status = "Partial"
        else:
            status = "Validate"
        return RequirementDecisionLine(
            requirement=self._clean(getattr(item, "competency_name", ""), "Role requirement"),
            required_level=required,
            pre_interview_level=pre,
            post_interview_level=post,
            current_status=status,
            evidence_status=self._clean(getattr(item, "evidence_status", ""), "Not established"),
            confidence=self._clean(getattr(item, "confidence", ""), "Unknown"),
            interview_priority=self._clean(getattr(item, "interview_priority", ""), "Validate"),
            validation_status=self._clean(getattr(item, "validation_status", ""), "Pending"),
            evidence=self._clean(getattr(item, "evidence", ""), ""),
        )

    def _confidence(self, report: Any, decision_brief: Any | None) -> Optional[float]:
        if decision_brief is not None:
            value = self._optional_float(getattr(decision_brief, "confidence_score", None))
            if value is not None:
                return value
        breakdown = dict(getattr(report, "score_breakdown", {}) or {})
        return self._optional_float(breakdown.get("confidence"))

    def _risk_text(self, item: Any) -> str:
        title = self._clean(getattr(item, "title", ""), "Evidence to validate")
        detail = self._clean(getattr(item, "detail", ""), "")
        requirement = self._clean(getattr(item, "related_requirement", ""), "")
        if detail:
            return f"{title}: {detail}"
        if requirement:
            return f"{title} · {requirement}"
        return title

    @staticmethod
    def _clean(value: Any, fallback: str) -> str:
        text = " ".join(str(value or "").split())
        return text or fallback

    @classmethod
    def _unique(cls, values: Any) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for value in values or []:
            text = cls._clean(value, "")
            key = text.casefold()
            if text and key not in seen:
                output.append(text)
                seen.add(key)
        return output

    @staticmethod
    def _optional_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _optional_int(cls, value: Any) -> Optional[int]:
        parsed = cls._optional_float(value)
        return None if parsed is None else int(round(parsed))
