from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
from talentcopilot.services.candidate_identity import resolve_candidate_id
from talentcopilot.services.candidate_ordering import sort_by_official_rank
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

        source = RecruitmentSourceOfTruthService().get(session)
        analyses_by_id = {
            str(getattr(item, "candidate_id", "")): item
            for item in getattr(session, "analyses", []) or []
        }
        analyses_by_name = {
            str(getattr(item, "candidate_name", "")): item
            for item in getattr(session, "analyses", []) or []
        }
        candidates_by_id = {}
        candidates_by_name = {}
        for candidate in getattr(session, "candidates", []) or []:
            candidate_id = resolve_candidate_id(candidate)
            if candidate_id:
                candidates_by_id[candidate_id] = candidate
            candidate_name = str(candidate.get("name", "") or "")
            if candidate_name:
                candidates_by_name.setdefault(candidate_name, candidate)

        candidates = []
        for record in sort_by_official_rank(source.candidates):
            analysis = analyses_by_id.get(str(record.candidate_id))
            if analysis is None:
                analysis = analyses_by_name.get(record.candidate_name)
            if analysis is None:
                continue

            candidate = candidates_by_id.get(str(record.candidate_id))
            if candidate is None:
                candidate = candidates_by_name.get(record.candidate_name, {})
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
                risks.append(
                    DecisionRisk(
                        "No major risk detected",
                        "No blocking risk identified in current analysis.",
                        "Low",
                    )
                )

            match = float(record.mission_fit_score or 0)
            consensus = min(96, max(55, int((match + 88) / 2)))

            candidates.append(
                CandidateDecisionSummary(
                    candidate_id=str(record.candidate_id),
                    candidate_name=record.candidate_name,
                    # Decision Board displays the canonical recruitment rank used
                    # by Dashboard Perspective, Candidate Intelligence, Interview
                    # and Compare & Decide. Decision priority remains available in
                    # the source-of-truth record but must not replace this label.
                    rank=int(record.mission_rank or 0),
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

        candidates = sort_by_official_rank(candidates)

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
