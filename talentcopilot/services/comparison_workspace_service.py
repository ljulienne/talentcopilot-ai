from talentcopilot.recruitment_source_of_truth import RecruitmentSourceOfTruthService
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

        source = RecruitmentSourceOfTruthService().get(session)
        analyses_by_id = {
            str(getattr(item, "candidate_id", "")): item
            for item in getattr(session, "analyses", [])
        }

        for record in sorted(source.candidates, key=lambda item: item.interview_priority)[:5]:
            analysis = analyses_by_id.get(record.candidate_id)
            if analysis is None:
                continue

            score = float(record.mission_fit_score or 0)
            signals = self.signal_service.build(analysis, session)
            ai_confidence = record.confidence if record.confidence is not None else signals.confidence
            scores.append(score)

            candidates.append(
                ComparisonCandidate(
                    rank=record.interview_priority,
                    candidate_name=record.candidate_name,
                    match_score=score,
                    decision_score=record.decision_score,
                    ai_confidence=ai_confidence,
                    recommendation=signals.recommendation,
                    key_strength=signals.key_strength,
                    key_risk=signals.key_risk,
                    mission_rank=record.mission_rank,
                    interview_priority=record.interview_priority,
                    career_fit_score=record.career_fit_score,
                )
            )

            matrix.append(
                DecisionMatrixLine(
                    candidate_name=record.candidate_name,
                    technical_fit=int(min(100, max(0, round(score)))),
                    leadership_fit=int(min(100, max(0, round(record.recruiter_fit_score or score - 3)))),
                    evidence_strength=self._evidence_strength(score, ai_confidence),
                    decision_readiness=self._decision_readiness(record.decision_score or score, ai_confidence),
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
                f"{leader.candidate_name} is the current interview priority. "
                f"Mission Fit: {leader.match_score:.0f}% · {leader.key_strength}."
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
