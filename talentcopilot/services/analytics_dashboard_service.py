from talentcopilot.models.analytics_dashboard import (
    AnalyticsDashboardReport,
    AnalyticsFunnelStage,
    AnalyticsKPI,
    AnalyticsSignal,
)


class AnalyticsDashboardService:
    def build(self, session=None) -> AnalyticsDashboardReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        ranked = getattr(session, "ranked_analyses", []) or []
        candidate_count = int(getattr(session, "candidate_count", len(ranked)) or 0)
        analyzed_count = int(getattr(session, "analyzed_count", len(ranked)) or 0)
        scores = [float(getattr(item, "match_score", 0) or 0) for item in ranked]

        top_match = max(scores) if scores else 0
        average_match = sum(scores) / max(1, len(scores))
        shortlist_count = len([s for s in scores if s >= 80])
        interview_ready_count = len([s for s in scores if s >= 70])
        weak_count = len([s for s in scores if s < 40])

        pipeline_score = min(100, int((analyzed_count / max(1, candidate_count)) * 100))
        candidate_score = int(min(100, max(0, average_match)))
        interview_score = min(100, 55 + interview_ready_count * 10)
        budget_score = 72 if top_match >= 90 else 86
        decision_score = min(100, 45 + shortlist_count * 18)

        signals = [
            AnalyticsSignal("Pipeline", pipeline_score, self._status(pipeline_score), "Candidates imported and analyzed."),
            AnalyticsSignal("Candidate Quality", candidate_score, self._status(candidate_score), "Average candidate match quality."),
            AnalyticsSignal("Interview Readiness", interview_score, self._status(interview_score), "Profiles ready for structured interview."),
            AnalyticsSignal("Budget Risk", budget_score, self._status(budget_score), "Estimated financial feasibility."),
            AnalyticsSignal("Decision Readiness", decision_score, self._status(decision_score), "Shortlist and decision board readiness."),
        ]

        global_readiness = int(sum(signal.score for signal in signals) / len(signals))

        funnel = [
            AnalyticsFunnelStage("Imported", candidate_count, 100),
            AnalyticsFunnelStage("Analyzed", analyzed_count, int((analyzed_count / max(1, candidate_count)) * 100)),
            AnalyticsFunnelStage("Interview Ready", interview_ready_count, int((interview_ready_count / max(1, candidate_count)) * 100)),
            AnalyticsFunnelStage("Shortlisted", shortlist_count, int((shortlist_count / max(1, candidate_count)) * 100)),
            AnalyticsFunnelStage("Weak Match", weak_count, int((weak_count / max(1, candidate_count)) * 100)),
        ]

        recommendations = []
        if shortlist_count == 0:
            recommendations.append("Review search criteria or widen sourcing strategy.")
        if weak_count > 0:
            recommendations.append("Reject or deprioritize weak matches before interview planning.")
        if top_match >= 90:
            recommendations.append("Validate budget feasibility for top candidate before final decision.")
        if interview_ready_count:
            recommendations.append("Prepare structured interviews for candidates above interview threshold.")
        recommendations.append("Use Decision Board before issuing final recommendation.")

        return AnalyticsDashboardReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            global_readiness=global_readiness,
            kpis=[
                AnalyticsKPI("Candidates", str(candidate_count), "Imported"),
                AnalyticsKPI("Analyzed", str(analyzed_count), "AI processed"),
                AnalyticsKPI("Top Match", f"{top_match:.0f}%", "Best candidate"),
                AnalyticsKPI("Average Match", f"{average_match:.0f}%", "Portfolio quality"),
                AnalyticsKPI("Shortlist", str(shortlist_count), ">= 80%"),
                AnalyticsKPI("Interview Ready", str(interview_ready_count), ">= 70%"),
            ],
            signals=signals,
            funnel=funnel,
            recommendations=recommendations,
        )

    def _status(self, score: int) -> str:
        if score >= 85:
            return "Strong"
        if score >= 65:
            return "Good"
        if score >= 45:
            return "Needs attention"
        return "Critical"

    def _empty_report(self) -> AnalyticsDashboardReport:
        return AnalyticsDashboardReport(
            role_title="No active recruitment",
            session_id="-",
            global_readiness=0,
            kpis=[
                AnalyticsKPI("Candidates", "0", "Load demo"),
                AnalyticsKPI("Analyzed", "0", "-"),
                AnalyticsKPI("Top Match", "-", "-"),
                AnalyticsKPI("Shortlist", "0", "-"),
            ],
            signals=[
                AnalyticsSignal("Pipeline", 0, "Critical", "No active recruitment session."),
            ],
            funnel=[
                AnalyticsFunnelStage("Imported", 0, 0),
                AnalyticsFunnelStage("Analyzed", 0, 0),
            ],
            recommendations=["Load Enterprise Demo or create a recruitment session."],
        )
