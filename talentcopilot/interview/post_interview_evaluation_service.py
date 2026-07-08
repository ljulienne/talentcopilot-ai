from talentcopilot.interview.evaluation_models import InterviewEvaluationSummary, InterviewRating


class PostInterviewEvaluationService:
    def build_default_ratings(self, report) -> list[InterviewRating]:
        ratings = []
        for item in getattr(report, "scorecard", []) or []:
            ratings.append(
                InterviewRating(
                    competency=item.competency,
                    score=int(getattr(item, "suggested_score", 3) or 3),
                    evidence_confirmed=int(getattr(item, "suggested_score", 3) or 3) >= 4,
                    notes="Suggested from current evidence. Adjust after interview.",
                )
            )
        return ratings

    def evaluate(self, candidate_name: str, ratings: list[InterviewRating]) -> InterviewEvaluationSummary:
        if not ratings:
            return InterviewEvaluationSummary(
                candidate_name=candidate_name,
                overall_score=0.0,
                decision_impact="No evaluation",
                recommendation_after_interview="Needs Evaluation",
                strengths_confirmed=[],
                risks_remaining=["No interview ratings available."],
                ratings=[],
            )

        average = sum(max(1, min(5, rating.score)) for rating in ratings) / len(ratings)
        confirmed = [rating.competency for rating in ratings if rating.evidence_confirmed and rating.score >= 4]
        risks = [rating.competency for rating in ratings if rating.score <= 2 or not rating.evidence_confirmed]

        if average >= 4.5 and len(risks) == 0:
            impact = "Strong positive"
            recommendation = "Proceed to Decision Board"
        elif average >= 3.7:
            impact = "Positive"
            recommendation = "Proceed with targeted validation"
        elif average >= 3.0:
            impact = "Neutral"
            recommendation = "Review before decision"
        else:
            impact = "Negative"
            recommendation = "Do not proceed yet"

        return InterviewEvaluationSummary(
            candidate_name=candidate_name,
            overall_score=round(average, 2),
            decision_impact=impact,
            recommendation_after_interview=recommendation,
            strengths_confirmed=confirmed,
            risks_remaining=risks,
            ratings=ratings,
        )

    def to_markdown(self, summary: InterviewEvaluationSummary) -> str:
        lines = [
            f"# Interview Evaluation — {summary.candidate_name}",
            "",
            f"Overall score: {summary.overall_score}/5",
            f"Decision impact: {summary.decision_impact}",
            f"Recommendation: {summary.recommendation_after_interview}",
            "",
            "## Ratings",
        ]

        for rating in summary.ratings:
            status = "confirmed" if rating.evidence_confirmed else "not confirmed"
            lines.append(f"- {rating.competency}: {rating.score}/5 — evidence {status}. {rating.notes}")

        lines.extend(["", "## Strengths confirmed"])
        if summary.strengths_confirmed:
            for item in summary.strengths_confirmed:
                lines.append(f"- {item}")
        else:
            lines.append("- None yet.")

        lines.extend(["", "## Risks remaining"])
        if summary.risks_remaining:
            for item in summary.risks_remaining:
                lines.append(f"- {item}")
        else:
            lines.append("- No major remaining risk.")

        return "\n".join(lines)
