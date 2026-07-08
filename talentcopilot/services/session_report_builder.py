
from typing import Any, Dict


class SessionReportBuilder:
    def build(self, session: Any) -> Dict:
        if session is None:
            return {
                "title": "No active recruitment session",
                "summary": "Create a session before generating a report.",
                "candidates": [],
                "recommendations": [],
                "risks": [],
            }

        candidates = []
        recommendations = []
        risks = []

        for analysis in getattr(session, "ranked_analyses", []):
            decision = "-"
            if getattr(analysis, "decision_report", None):
                decision = getattr(
                    analysis.decision_report.recommendation,
                    "value",
                    analysis.decision_report.recommendation,
                )
                recommendations.append(f"{analysis.candidate_name}: {decision}")

            if getattr(analysis, "errors", None):
                risks.extend([f"{analysis.candidate_name}: {error}" for error in analysis.errors])

            candidates.append({
                "rank": analysis.rank,
                "name": analysis.candidate_name,
                "match_score": analysis.match_score,
                "status": analysis.status.value,
                "decision": decision,
            })

        return {
            "title": f"Recruitment report — {session.role_title}",
            "summary": (
                f"{session.candidate_count} candidate(s), "
                f"{session.analyzed_count} analyzed, "
                f"{session.error_count} error(s)."
            ),
            "session_id": session.session_id,
            "role_title": session.role_title,
            "candidates": candidates,
            "recommendations": recommendations,
            "risks": risks,
        }

    def build_markdown(self, session: Any) -> str:
        report = self.build(session)

        lines = [
            f"# {report['title']}",
            "",
            report["summary"],
            "",
            "## Candidates",
        ]

        for candidate in report["candidates"]:
            lines.append(
                f"- #{candidate['rank']} {candidate['name']} — "
                f"{candidate['match_score']}% — {candidate['decision']}"
            )

        if report["recommendations"]:
            lines.extend(["", "## Recommendations"])
            lines.extend([f"- {item}" for item in report["recommendations"]])

        if report["risks"]:
            lines.extend(["", "## Risks"])
            lines.extend([f"- {item}" for item in report["risks"]])

        return "\n".join(lines)
