from talentcopilot.models.decision_board import (
    CandidateDecisionSummary,
    DecisionBoardReport,
    DecisionReason,
    DecisionRisk,
    StakeholderDecision,
)


class DecisionBoardService:
    def build(self, session=None) -> DecisionBoardReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        candidates = []
        candidate_lookup = {}
        for candidate in getattr(session, "candidates", []) or []:
            if candidate.get("name"):
                candidate_lookup[candidate["name"]] = candidate

        for analysis in session.ranked_analyses:
            candidate = candidate_lookup.get(analysis.candidate_name, {})
            decision_report = getattr(analysis, "decision_report", None)

            ai_recommendation = "Review"
            reasons = []
            risks = []

            if decision_report:
                ai_recommendation = getattr(
                    decision_report.recommendation,
                    "value",
                    decision_report.recommendation,
                )

                summary = getattr(decision_report, "executive_summary", "")
                if summary:
                    reasons.append(DecisionReason("AI executive summary", summary, "High"))

                for concern in getattr(decision_report, "concerns", []) or []:
                    risks.append(
                        DecisionRisk(
                            title=getattr(concern, "title", "Concern"),
                            detail=getattr(concern, "explanation", ""),
                            severity=getattr(concern, "severity", "Medium"),
                        )
                    )

            for achievement in candidate.get("achievements", [])[:3]:
                reasons.append(DecisionReason("Evidence", str(achievement), "High"))

            if not risks:
                risks.append(DecisionRisk("No major risk detected", "No blocking risk identified in current analysis.", "Low"))

            match = float(getattr(analysis, "match_score", 0) or 0)
            consensus = min(96, max(55, int((match + 88) / 2)))

            candidates.append(
                CandidateDecisionSummary(
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    rank=int(getattr(analysis, "rank", 0) or 0),
                    match_score=match,
                    ai_recommendation=str(ai_recommendation),
                    consensus_score=consensus,
                    stakeholder_decisions=[
                        StakeholderDecision("AI", str(ai_recommendation), min(98, int(match)), "Evidence-based recommendation."),
                        StakeholderDecision("Recruiter", "Proceed", 86, "Profile is relevant for screening."),
                        StakeholderDecision("Hiring Manager", "Pending", 0, "Operational review not completed."),
                        StakeholderDecision("HR Director", "Pending", 0, "Executive approval not completed."),
                    ],
                    reasons=reasons,
                    risks=risks,
                )
            )

        return DecisionBoardReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            decision_status="In Review",
            candidates=candidates,
            next_actions=[
                "Validate Hiring Manager assessment for the top candidate.",
                "Review decision risks before moving to interview.",
                "Generate an executive summary once stakeholder feedback is complete.",
            ],
        )

    def _empty_report(self) -> DecisionBoardReport:
        return DecisionBoardReport(
            role_title="No active recruitment",
            session_id="-",
            decision_status="Not started",
            candidates=[],
            next_actions=["Load Enterprise Demo to start a decision review."],
        )
