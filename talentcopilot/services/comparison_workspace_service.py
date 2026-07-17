from talentcopilot.models.comparison_workspace import (
    ComparisonCandidate,
    ComparisonWorkspaceReport,
    DecisionMatrixLine,
    ScoreGap,
)
from talentcopilot.services.candidate_decision_signal_service import (
    CandidateDecisionSignalService,
)


class ComparisonWorkspaceService:
    def __init__(self, signal_service=None):
        self.signal_service = signal_service or CandidateDecisionSignalService()

    def build(self, session=None) -> ComparisonWorkspaceReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        candidates = []
        matrix = []
        scores = []

        for analysis in session.ranked_analyses[:5]:
            score = float(
                getattr(
                    analysis,
                    "official_match_score",
                    getattr(analysis, "match_score", 0),
                )
                or 0
            )
            rank = int(
                getattr(
                    analysis,
                    "official_rank",
                    getattr(analysis, "rank", 0),
                )
                or 0
            )
            signals = self.signal_service.build(analysis, session)
            ai_confidence = signals.confidence

            # Kept internally only; never exposed as a competing UI score.
            decision_score = getattr(analysis, "official_decision_score", None)
            if decision_score is not None:
                try:
                    decision_score = float(decision_score)
                except (TypeError, ValueError):
                    decision_score = None

            scores.append(score)
            candidate_name = getattr(analysis, "candidate_name", "Candidate")

            candidates.append(
                ComparisonCandidate(
                    rank=rank,
                    candidate_name=candidate_name,
                    match_score=score,
                    decision_score=decision_score,
                    ai_confidence=ai_confidence,
                    recommendation=signals.recommendation,
                    key_strength=signals.key_strength,
                    key_risk=signals.key_risk,
                )
            )

            matrix.append(
                DecisionMatrixLine(
                    candidate_name=candidate_name,
                    technical_fit=int(min(100, max(0, round(score)))),
                    leadership_fit=int(min(100, max(0, round(score - 3)))),
                    evidence_strength=self._evidence_strength(score, ai_confidence),
                    decision_readiness=self._decision_readiness(score, ai_confidence),
                )
            )

        score_gaps = []
        if len(scores) >= 2:
            gap = scores[0] - scores[1]
            score_gaps.append(
                ScoreGap(
                    "Top 1 vs Top 2",
                    gap,
                    "Clear lead" if gap >= 8 else "Close competition",
                )
            )
        if len(scores) >= 3:
            gap = scores[1] - scores[2]
            score_gaps.append(
                ScoreGap(
                    "Top 2 vs Top 3",
                    gap,
                    "Meaningful gap" if gap >= 6 else "Needs deeper review",
                )
            )

        differentiators = []
        if candidates:
            leader = candidates[0]
            differentiators.append(
                f"{leader.candidate_name} leads with an official match of "
                f"{leader.match_score:.0f}%: {leader.key_strength}."
            )
        if len(candidates) > 1:
            differentiators.append(
                "Compare the shortlist through evidence quality and validation gaps, "
                "not through an additional competing score."
            )
        differentiators.append(
            "Complete a structured human review before final selection."
        )

        return ComparisonWorkspaceReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            candidates=candidates,
            score_gaps=score_gaps,
            matrix=matrix,
            differentiators=differentiators,
        )

    def _evidence_strength(self, score, confidence):
        value = confidence if confidence is not None else score
        return int(min(100, max(0, round(value))))

    def _decision_readiness(self, score, confidence):
        if confidence is None:
            return int(min(100, max(0, round(score))))
        return int(min(100, max(0, round(score * 0.65 + confidence * 0.35))))

    def _empty_report(self) -> ComparisonWorkspaceReport:
        return ComparisonWorkspaceReport(
            role_title="No active recruitment",
            session_id="-",
            candidates=[],
            score_gaps=[],
            matrix=[],
            differentiators=["Load Enterprise Demo to compare candidates."],
        )
