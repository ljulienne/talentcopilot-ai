from talentcopilot.services.official_score_service import get_official_candidate_score

from talentcopilot.models.executive_reporting import (
    ExecutiveCandidateLine,
    ExecutiveReport,
    ExecutiveRiskLine,
)


class ExecutiveReportingService:
    def build(self, session=None) -> ExecutiveReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        shortlist = []
        risks = []

        for analysis in session.ranked_analyses[:5]:
            recommendation = "Review"
            readiness = int(min(96, max(50, get_official_candidate_score(analysis))))

            decision_report = getattr(analysis, "decision_report", None)
            if decision_report:
                recommendation = getattr(
                    decision_report.recommendation,
                    "value",
                    decision_report.recommendation,
                )

                for concern in getattr(decision_report, "concerns", []) or []:
                    risks.append(
                        ExecutiveRiskLine(
                            title=f"{analysis.candidate_name}: {getattr(concern, 'title', 'Concern')}",
                            detail=getattr(concern, "explanation", ""),
                            severity=getattr(concern, "severity", "Medium"),
                        )
                    )

            shortlist.append(
                ExecutiveCandidateLine(
                    rank=int(getattr(analysis, "rank", 0) or 0),
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    match_score=get_official_candidate_score(analysis),
                    recommendation=str(recommendation),
                    decision_readiness=readiness,
                )
            )

        if not risks:
            risks.append(
                ExecutiveRiskLine(
                    "No blocking risk detected",
                    "Current AI analysis does not identify a blocking risk for the shortlist.",
                    "Low",
                )
            )

        best = shortlist[0].candidate_name if shortlist else "the top-ranked candidate"

        return ExecutiveReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            executive_summary=(
                f"The recruitment for {getattr(session, 'role_title', 'the role')} has "
                f"{getattr(session, 'candidate_count', len(shortlist))} candidate(s), with {best} currently leading the shortlist. "
                "The next step is to validate stakeholder feedback before final decision."
            ),
            shortlist=shortlist,
            risks=risks,
            recommendations=[
                f"Review evidence and interview readiness for {best}.",
                "Confirm Hiring Manager assessment before final decision.",
                "Prepare stakeholder-ready summary after decision board validation.",
            ],
            next_steps=[
                "Complete Hiring Manager review.",
                "Update Decision Board.",
                "Generate final report after stakeholder alignment.",
            ],
        )

    def _empty_report(self) -> ExecutiveReport:
        return ExecutiveReport(
            role_title="No active recruitment",
            session_id="-",
            executive_summary="No active recruitment session is available. Load the Enterprise Demo to generate an executive report.",
            shortlist=[],
            risks=[],
            recommendations=["Load Enterprise Demo."],
            next_steps=["Start a recruitment session."],
        )

    def to_markdown(self, report: ExecutiveReport) -> str:
        lines = [
            f"# Executive Recruitment Report — {report.role_title}",
            "",
            "## Executive Summary",
            report.executive_summary,
            "",
            "## Shortlist",
        ]

        if report.shortlist:
            for candidate in report.shortlist:
                lines.append(
                    f"- #{candidate.rank} {candidate.candidate_name} — "
                    f"{candidate.match_score:.0f}% match — {candidate.recommendation} — "
                    f"{candidate.decision_readiness}% readiness"
                )
        else:
            lines.append("- No candidates available.")

        lines.extend(["", "## Risks"])
        if report.risks:
            for risk in report.risks:
                lines.append(f"- **{risk.severity}** — {risk.title}: {risk.detail}")
        else:
            lines.append("- No risks available.")

        lines.extend(["", "## Recommendations"])
        for item in report.recommendations:
            lines.append(f"- {item}")

        lines.extend(["", "## Next Steps"])
        for item in report.next_steps:
            lines.append(f"- {item}")

        return "\n".join(lines)
