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

    def candidate(self, report: Any, compensation: Any | None = None) -> PdfExport:
        lines = [
            f"# Candidate Report - {getattr(report, 'candidate_name', 'Candidate')}",
            "",
            f"Role: {getattr(report, 'role_title', 'Recruitment')}",
            f"Official rank: #{getattr(report, 'rank', '-')}",
            f"Official role fit: {float(getattr(report, 'match_score', 0) or 0):.0f}%",
            f"Recommendation: {getattr(report, 'recommendation', 'Review')}",
            "",
            "## Executive summary",
            str(getattr(report, "executive_summary", "") or "No executive summary is available."),
        ]
        self._append_values(lines, "Strengths", getattr(report, "strengths", ()))
        self._append_values(lines, "Grounded evidence", getattr(report, "evidence", ()))
        self._append_values(lines, "Risks to validate", getattr(report, "risks", ()))
        self._append_values(lines, "Interview priorities", getattr(report, "interview_focus", ()))
        if compensation is not None and getattr(compensation, "documented", False):
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
        lines.extend(["", "## Governance", "- Compensation fit is displayed separately and never changes official talent fit or rank."])
        candidate_id = str(getattr(report, "candidate_id", "") or "candidate")
        return self._export(lines, f"talentcopilot_candidate_{candidate_id}.pdf", "TalentCopilot Candidate Report", getattr(report, "role_title", "Recruitment"))

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

    def comparison(self, report: Any, evaluations: dict[str, Any] | None = None) -> PdfExport:
        lines = [
            f"# Compare & Decide - {getattr(report, 'role_title', 'Recruitment')}",
            "",
            "## Finalist comparison",
        ]
        evaluations = evaluations or {}
        for candidate in list(getattr(report, "candidates", []) or []):
            candidate_id = str(getattr(candidate, "candidate_id", "") or "")
            evaluation = evaluations.get(candidate_id, {})
            lines.extend(
                [
                    f"### #{getattr(candidate, 'mission_rank', None) or getattr(candidate, 'rank', '-')} {getattr(candidate, 'candidate_name', 'Candidate')}",
                    f"- Official mission fit: {float(getattr(candidate, 'match_score', 0) or 0):.0f}%",
                    f"- Pre-interview recommendation: {getattr(candidate, 'recommendation', 'Review')}",
                    f"- Interview recommendation: {evaluation.get('recommendation', 'Not recorded') if isinstance(evaluation, dict) else 'Not recorded'}",
                    f"- Key strength: {getattr(candidate, 'key_strength', 'Not documented')}",
                    f"- Unresolved risk: {getattr(candidate, 'key_risk', 'Not documented')}",
                ]
            )
        self._append_values(lines, "Differentiators", getattr(report, "differentiators", ()))
        lines.extend(["", "## Governance", "- The report preserves official scores and ranks and keeps interview evidence separate."])
        return self._export(lines, "talentcopilot_compare_and_decide.pdf", "TalentCopilot Compare & Decide", getattr(report, "role_title", "Recruitment"))

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
