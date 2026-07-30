from __future__ import annotations

from typing import Any, Iterable

from talentcopilot.services.report_export_service import PdfExport, ReportExportService


class RecruitmentPdfService:
    """Recruiter-facing PDF exports built only from already stored product data."""

    def __init__(self, exporter: ReportExportService | None = None):
        self.exporter = exporter or ReportExportService()

    def mission(self, state: Any) -> PdfExport:
        lines = [
            f"# Recruitment Overview - {getattr(state, 'role_title', 'Recruitment')}",
            "",
            str(getattr(state, "summary", "") or ""),
            "",
            "## Official ranking",
        ]
        for candidate in list(getattr(state, "candidates", []) or []):
            lines.append(
                f"- #{getattr(candidate, 'rank', '-')} {getattr(candidate, 'name', 'Candidate')} - "
                f"{float(getattr(candidate, 'match_score', 0) or 0):.0f}% - "
                f"{getattr(candidate, 'recommendation', 'Review')}"
            )
        lines.extend(
            [
                "",
                "## Governance",
                "- Official talent scores and ranks are reproduced without recalculation.",
                "- Final hiring accountability remains with the human decision team.",
            ]
        )
        return self._export(lines, "talentcopilot_recruitment_overview.pdf", "TalentCopilot Recruitment Overview", getattr(state, "role_title", "Recruitment"))

    def dashboard(self, view: Any, compensation_report: Any | None = None) -> PdfExport:
        lines = [
            f"# Candidate Dashboard Perspective - {getattr(view, 'role_title', 'Recruitment')}",
            "",
            f"Candidates analysed: {getattr(view, 'analyzed_count', 0)}",
            f"Interviews completed: {getattr(view, 'interview_completed_count', 0)}",
            f"Ready for comparison: {getattr(view, 'ready_for_decision_count', 0)}",
            "",
            "## Candidate perspective",
        ]
        budget_by_name = {
            str(getattr(item, "candidate_name", "")): item
            for item in list(getattr(compensation_report, "assessments", []) or [])
        }
        for candidate in list(getattr(view, "candidates", []) or []):
            budget = budget_by_name.get(str(getattr(candidate, "candidate_name", "")))
            compensation = getattr(budget, "budget_recommendation", "Not documented") if budget else "Not documented"
            lines.extend(
                [
                    f"### #{getattr(candidate, 'official_rank', '-')} {getattr(candidate, 'candidate_name', 'Candidate')}",
                    f"- Official role fit: {float(getattr(candidate, 'official_match_score', 0) or 0):.0f}%",
                    f"- Evidence confidence: {getattr(candidate, 'confidence_score', 'Not available')}",
                    f"- Interview status: {getattr(candidate, 'interview_status', 'Not started')}",
                    f"- Compensation fit: {compensation}",
                    f"- Strongest area: {getattr(candidate, 'strongest_area', 'No differentiated strength established')}",
                    f"- Primary risk: {getattr(candidate, 'primary_risk', 'No critical risk identified')}",
                    f"- Critical gaps: {', '.join(getattr(candidate, 'critical_gaps', ()) or ()) or 'None documented'}",
                ]
            )
        lines.extend(
            [
                "",
                "## Recommended next action",
                f"- {getattr(view, 'next_action_title', 'Continue the recruitment workflow')}: "
                f"{getattr(view, 'next_action_detail', '')}",
            ]
        )
        return self._export(lines, "talentcopilot_candidate_dashboard.pdf", "TalentCopilot Candidate Dashboard Perspective", getattr(view, "role_title", "Recruitment"))

    def candidate(
        self,
        report: Any,
        compensation: Any | None = None,
        *,
        decision_view: Any | None = None,
    ) -> PdfExport:
        view = decision_view
        role_title = getattr(view, "role_title", None) or getattr(report, "role_title", "Recruitment")
        official_rank = getattr(view, "official_rank", None) or getattr(report, "rank", "-")
        official_score = (
            getattr(view, "official_match_score", None)
            if view is not None
            else getattr(report, "match_score", 0)
        )
        recommendation = (
            getattr(view, "pre_interview_recommendation", None)
            if view is not None
            else getattr(report, "recommendation", "Review")
        )
        lines = [
            f"# Candidate Decision Workspace - {getattr(report, 'candidate_name', 'Candidate')}",
            "",
            f"Role: {role_title}",
            f"Official rank: #{official_rank}",
            f"Official Talent Fit: {float(official_score or 0):.0f}%",
            f"Pre-interview recommendation: {recommendation or 'Review'}",
            "",
            "## Executive summary",
            str(getattr(report, "executive_summary", "") or "No executive summary is available."),
        ]

        if view is not None:
            lines.extend(["", "## Decision journey"])
            for stage in list(getattr(view, "journey", ()) or ()):
                lines.extend([
                    f"### {getattr(stage, 'label', 'Decision stage')}",
                    f"- Status: {getattr(stage, 'status', 'Pending')}",
                    f"- Recommendation: {getattr(stage, 'recommendation', 'Not recorded')}",
                    f"- Evidence or rationale: {getattr(stage, 'evidence_note', 'Not documented')}",
                ])

            self._append_values(lines, "Demonstrated strengths", getattr(view, "strengths", ()))
            self._append_values(lines, "Risks to validate", getattr(view, "risks", ()))
            self._append_values(lines, "Interview priorities", getattr(view, "interview_priorities", ()))

            lines.extend(["", "## Role requirement coverage"])
            requirements = list(getattr(view, "requirements", ()) or ())
            if requirements:
                for item in requirements:
                    post = getattr(item, "post_interview_level", None)
                    post_label = f"{float(post):.1f}" if post is not None else "Not assessed"
                    lines.append(
                        f"- {getattr(item, 'requirement', 'Requirement')}: "
                        f"required {float(getattr(item, 'required_level', 0) or 0):.1f}; "
                        f"pre-interview {float(getattr(item, 'pre_interview_level', 0) or 0):.1f}; "
                        f"post-interview {post_label}; "
                        f"status {getattr(item, 'current_status', 'Validate')}; "
                        f"evidence {getattr(item, 'evidence_status', 'Not established')}"
                    )
            else:
                lines.append("- No structured role requirement is available.")

            lines.extend([
                "",
                "## Compensation and availability",
                f"- Compensation status: {getattr(view, 'compensation_status', 'Not documented')}",
                f"- Compensation fit: {getattr(view, 'compensation_fit', 'Pending compensation data')}",
                f"- Expected base salary: " + (
                    f"{getattr(view, 'currency', 'EUR')} {float(getattr(view, 'expected_salary')):,.0f}"
                    if getattr(view, 'expected_salary', None) is not None
                    else "Not documented"
                ),
                f"- Availability date: {getattr(view, 'availability_date', 'Not documented')}",
                f"- Notice period: {int(getattr(view, 'notice_period_weeks', 0) or 0)} weeks",
                f"- Flexibility: {getattr(view, 'flexibility', 'Unknown')}",
            ])

            if getattr(view, "has_final_decision", False):
                lines.extend([
                    "",
                    "## Final human decision",
                    f"- Recommendation: {getattr(view, 'final_decision_recommendation', 'Not recorded')}",
                    f"- Owner: {getattr(view, 'final_decision_actor', '') or 'Not documented'}",
                    f"- Timestamp: {getattr(view, 'final_decision_timestamp', '') or 'Not documented'}",
                    f"- Rationale: {getattr(view, 'final_decision_rationale', '') or 'Not documented'}",
                ])
        else:
            self._append_values(lines, "Strengths", getattr(report, "strengths", ()))
            self._append_values(lines, "Grounded evidence", getattr(report, "evidence", ()))
            self._append_values(lines, "Risks to validate", getattr(report, "risks", ()))
            self._append_values(lines, "Interview priorities", getattr(report, "interview_focus", ()))

        if compensation is not None and getattr(compensation, "documented", False) and view is None:
            lines.extend(
                [
                    "",
                    "## Compensation expectations",
                    f"- Requested base salary: {getattr(compensation, 'currency', 'EUR')} {float(getattr(compensation, 'expected_salary', 0) or 0):,.0f}",
                    f"- Variable compensation: {getattr(compensation, 'currency', 'EUR')} {float(getattr(compensation, 'variable_compensation', 0) or 0):,.0f}",
                    f"- Benefits requested: {getattr(compensation, 'benefits_requested', '') or 'Not specified'}",
                    f"- Notice period: {int(getattr(compensation, 'notice_period_weeks', 0) or 0)} weeks",
                    f"- Flexibility: {getattr(compensation, 'flexibility', 'Unknown')}",
                ]
            )
        lines.extend([
            "",
            "## Governance",
            "- Official Talent Fit and rank are reproduced without recalculation.",
            "- Interview, compensation and final decision signals remain separate evidence layers.",
        ])
        candidate_id = str(getattr(report, "candidate_id", "") or "candidate")
        return self._export(
            lines,
            f"talentcopilot_candidate_{candidate_id}.pdf",
            "TalentCopilot Candidate Decision Workspace",
            role_title,
        )

    def interview(self, report: Any, evaluation: Any | None = None) -> PdfExport:
        lines = [
            f"# Interview & Assessment - {getattr(report, 'candidate_name', 'Candidate')}",
            "",
            f"Role: {getattr(report, 'role_title', 'Recruitment')}",
            f"Official rank: #{getattr(report, 'official_rank', '-')}",
            f"Official role fit: {float(getattr(report, 'fit_score', 0) or 0):.0f}%",
            f"Preparation confidence: {getattr(report, 'confidence_score', 'Not available')}%",
            "",
            "## Interview plan",
        ]
        plan = getattr(report, "plan", None)
        if plan is not None:
            lines.append(f"- Suggested duration: {getattr(plan, 'total_minutes', 0)} minutes")
            for section in list(getattr(plan, "sections", []) or []):
                lines.append(f"- {getattr(section, 'title', 'Section')}: {getattr(section, 'duration_minutes', 0)} minutes")
        self._append_values(lines, "Questions", getattr(report, "questions", ()))
        if evaluation:
            lines.extend(["", "## Saved interview assessment"])
            for key, value in dict(evaluation).items() if isinstance(evaluation, dict) else []:
                lines.append(f"- {str(key).replace('_', ' ').title()}: {value}")
        lines.extend(["", "## Governance", "- Interview findings are displayed separately from the immutable pre-interview score."])
        candidate_id = str(getattr(report, "candidate_id", "") or "candidate")
        return self._export(lines, f"talentcopilot_interview_{candidate_id}.pdf", "TalentCopilot Interview & Assessment", getattr(report, "role_title", "Recruitment"))

    def comparison(
        self,
        report: Any,
        evaluations: dict[str, Any] | None = None,
        *,
        compensation_report: Any | None = None,
        expectations: dict[str, Any] | None = None,
        workflow_context: Any | None = None,
    ) -> PdfExport:
        lines = [
            f"# Compare & Decide - {getattr(report, 'role_title', 'Recruitment')}",
            "",
            "## Finalist decision matrix",
        ]
        evaluations = evaluations or {}
        expectations = expectations or {}
        budget_by_name = {
            str(getattr(item, "candidate_name", "")): item
            for item in list(getattr(compensation_report, "assessments", []) or [])
        }
        for candidate in list(getattr(report, "candidates", []) or []):
            candidate_id = str(getattr(candidate, "candidate_id", "") or "")
            candidate_name = str(getattr(candidate, "candidate_name", "Candidate") or "Candidate")
            evaluation = evaluations.get(candidate_id, {})
            expectation = expectations.get(candidate_id)
            budget = budget_by_name.get(candidate_name)
            final_recommendation = "Not recorded"
            if (
                workflow_context is not None
                and bool(getattr(workflow_context, "decision_recorded", False))
                and str(getattr(workflow_context, "final_decision_candidate_id", "") or "") == candidate_id
            ):
                final_recommendation = str(
                    getattr(workflow_context, "final_decision_recommendation", "") or "Not recorded"
                )
            availability = (
                getattr(expectation, "availability_date", "")
                or (
                    f"{int(getattr(expectation, 'notice_period_weeks', 0) or 0)} weeks notice"
                    if expectation is not None and int(getattr(expectation, "notice_period_weeks", 0) or 0)
                    else "Not documented"
                )
            )
            lines.extend(
                [
                    f"### #{getattr(candidate, 'mission_rank', None) or getattr(candidate, 'rank', '-')} {candidate_name}",
                    f"- Official Talent Fit: {float(getattr(candidate, 'match_score', 0) or 0):.0f}%",
                    f"- Evidence confidence: {getattr(candidate, 'ai_confidence', 'Not available')}",
                    f"- Critical risk: {(evaluation.get('remaining_risks') or [getattr(candidate, 'key_risk', 'Not documented')])[0] if isinstance(evaluation, dict) else getattr(candidate, 'key_risk', 'Not documented')}",
                    f"- Interview assessment: {evaluation.get('recommendation', 'Not recorded') if isinstance(evaluation, dict) else 'Not recorded'}",
                    f"- Compensation fit: {getattr(budget, 'budget_recommendation', 'Pending compensation data') if budget is not None else 'Pending compensation data'}",
                    f"- Availability: {availability}",
                    f"- Final recommendation: {final_recommendation}",
                ]
            )
        self._append_values(lines, "Differentiators", getattr(report, "differentiators", ()))
        lines.extend([
            "",
            "## Governance",
            "- Official Talent Fit and rank are preserved.",
            "- Interview, compensation, availability and the final human recommendation remain independent decision signals.",
        ])
        return self._export(
            lines,
            "talentcopilot_compare_and_decide.pdf",
            "TalentCopilot Compare & Decide",
            getattr(report, "role_title", "Recruitment"),
        )

    def compensation(self, report: Any, budget: Any, expectations: Iterable[Any]) -> PdfExport:
        currency = str(getattr(budget, "currency", "EUR") or "EUR")
        lines = [
            f"# Compensation & Budget - {getattr(report, 'role_title', 'Recruitment')}",
            "",
            "## Position budget",
            f"- Approved salary range: {currency} {float(getattr(budget, 'minimum_salary', 0) or 0):,.0f} - {currency} {float(getattr(budget, 'maximum_salary', 0) or 0):,.0f}",
            f"- Target salary: {currency} {float(getattr(budget, 'target_salary', 0) or 0):,.0f}",
            f"- Target bonus: {float(getattr(budget, 'target_bonus_percent', 0) or 0):.1f}%",
            f"- Maximum first-year cost: {currency} {float(getattr(budget, 'first_year_cost_limit', 0) or 0):,.0f}",
            "",
            "## Candidate expectations",
        ]
        for item in expectations:
            status = "Documented" if getattr(item, "documented", False) else "Not documented"
            lines.extend(
                [
                    f"### {getattr(item, 'candidate_name', 'Candidate')} - {status}",
                    f"- Requested base salary: {getattr(item, 'currency', currency)} {float(getattr(item, 'expected_salary', 0) or 0):,.0f}",
                    f"- Benefits requested: {getattr(item, 'benefits_requested', '') or 'Not specified'}",
                    f"- Notice period: {int(getattr(item, 'notice_period_weeks', 0) or 0)} weeks",
                    f"- Flexibility: {getattr(item, 'flexibility', 'Unknown')}",
                ]
            )
        lines.extend(["", "## Governance", "- Compensation feasibility is independent from candidate talent suitability."])
        return self._export(lines, "talentcopilot_compensation_budget.pdf", "TalentCopilot Compensation & Budget", getattr(report, "role_title", "Recruitment"))

    def _export(self, lines: list[str], file_name: str, title: str, subtitle: str) -> PdfExport:
        return self.exporter.from_markdown("\n".join(lines), file_name=file_name, title=title, subtitle=subtitle)

    @staticmethod
    def _append_values(lines: list[str], title: str, values: Iterable[Any]) -> None:
        lines.extend(["", f"## {title}"])
        values = list(values or [])
        if not values:
            lines.append("- No information is currently documented.")
            return
        for value in values:
            if isinstance(value, str):
                text = value
            else:
                text = (
                    getattr(value, "description", "")
                    or getattr(value, "statement", "")
                    or getattr(value, "title", "")
                    or getattr(value, "question", "")
                    or str(value)
                )
            lines.append(f"- {text}")
