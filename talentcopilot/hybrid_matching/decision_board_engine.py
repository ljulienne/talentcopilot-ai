from talentcopilot.hybrid_matching.decision_board_models import HybridDecisionBoard, HybridDecisionCandidate


class HybridDecisionBoardEngine:
    def build_from_ranking_output(self, ranking_output) -> HybridDecisionBoard:
        candidates = []

        for item in ranking_output.ranked_candidates:
            hybrid = item.matching_output.hybrid_report
            recruiter = hybrid.recruiter_report if hybrid else None

            final_score = self._final_score(
                decision_fit=item.fit_score,
                confidence=item.confidence_score,
                hybrid_score=item.hybrid_score,
                ranking_score=item.ranking_score,
            )

            candidates.append(
                HybridDecisionCandidate(
                    rank=0,
                    candidate_name=item.candidate_name,
                    role_title=ranking_output.role_title,
                    decision_fit_score=item.fit_score,
                    semantic_score=item.semantic_score,
                    career_score=item.career_score,
                    hybrid_score=item.hybrid_score,
                    final_score=final_score,
                    readiness_level=recruiter.readiness_level if recruiter else "Unknown",
                    action_recommendation=recruiter.action_recommendation if recruiter else item.recommendation,
                    top_strengths=recruiter.top_strengths[:3] if recruiter else [],
                    gaps=recruiter.gaps[:3] if recruiter else [],
                    interview_focus=recruiter.interview_focus[:3] if recruiter else [],
                )
            )

        candidates.sort(key=lambda candidate: candidate.final_score, reverse=True)
        for index, candidate in enumerate(candidates, start=1):
            candidate.rank = index

        return HybridDecisionBoard(role_title=ranking_output.role_title, candidates=candidates)

    def _final_score(self, decision_fit: int, confidence: int, hybrid_score: int, ranking_score: int) -> int:
        if hybrid_score:
            score = int(decision_fit * 0.35 + confidence * 0.15 + hybrid_score * 0.35 + ranking_score * 0.15)
        else:
            score = int(decision_fit * 0.55 + confidence * 0.2 + ranking_score * 0.25)
        return max(0, min(100, score))
