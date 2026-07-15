from talentcopilot.models.comparison_workspace import (
    ComparisonCandidate,
    ComparisonWorkspaceReport,
    DecisionMatrixLine,
    ScoreGap,
)


class ComparisonWorkspaceService:
    def build(self, session=None) -> ComparisonWorkspaceReport:
        if session is None or not getattr(session, "ranked_analyses", None):
            return self._empty_report()

        candidates = []
        matrix = []
        scores = []

        for analysis in session.ranked_analyses[:5]:
            decision_report = getattr(analysis, "decision_report", None)
            recommendation = "Review"
            key_strength = "Relevant experience"
            key_risk = "Requires validation"

            if decision_report:
                recommendation = getattr(
                    decision_report.recommendation,
                    "value",
                    decision_report.recommendation,
                )
                strengths = getattr(decision_report, "strengths", []) or []
                concerns = getattr(decision_report, "concerns", []) or []

                if strengths:
                    key_strength = getattr(strengths[0], "title", str(strengths[0]))
                if concerns:
                    key_risk = getattr(concerns[0], "title", str(concerns[0]))
                else:
                    key_risk = "No major risk detected"

            score = float(getattr(analysis, "match_score", 0) or 0)
            ai_confidence = getattr(
                analysis,
                "official_confidence_score",
                None,
            )
            if ai_confidence is not None:
                try:
                    ai_confidence = float(ai_confidence)
                except (TypeError, ValueError):
                    ai_confidence = None

            # Kept internally only; never exposed as a competing UI score.
            decision_score = getattr(
                analysis,
                "official_decision_score",
                None,
            )

            if decision_score is not None:
                try:
                    decision_score = float(decision_score)
                except (TypeError, ValueError):
                    decision_score = None
            scores.append(score)

            candidates.append(
                ComparisonCandidate(
                    rank=int(getattr(analysis, "rank", 0) or 0),
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    match_score=score,
                    decision_score=decision_score,
                    ai_confidence=ai_confidence,
                    recommendation=str(recommendation),
                    key_strength=str(key_strength),
                    key_risk=str(key_risk),
                )
            )

            matrix.append(
                DecisionMatrixLine(
                    candidate_name=getattr(analysis, "candidate_name", "Candidate"),
                    technical_fit=int(min(96, max(45, score))),
                    leadership_fit=int(min(95, max(50, score - 3))),
                    evidence_strength=int(min(97, max(55, score + 2))),
                    decision_readiness=int(min(96, max(50, (score + 88) / 2))),
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
            differentiators.append(f"{candidates[0].candidate_name} leads the shortlist based on current AI ranking.")
        if len(candidates) > 1:
            differentiators.append("Compare top candidates through evidence quality, not only match score.")
        differentiators.append("Complete a structured human review before final selection.")

        return ComparisonWorkspaceReport(
            role_title=getattr(session, "role_title", "Recruitment"),
            session_id=getattr(session, "session_id", "session"),
            candidates=candidates,
            score_gaps=score_gaps,
            matrix=matrix,
            differentiators=differentiators,
        )

    def _empty_report(self) -> ComparisonWorkspaceReport:
        return ComparisonWorkspaceReport(
            role_title="No active recruitment",
            session_id="-",
            candidates=[],
            score_gaps=[],
            matrix=[],
            differentiators=["Load Enterprise Demo to compare candidates."],
        )
