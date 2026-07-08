from talentcopilot.interview.models import InterviewCompetency, InterviewScorecardItem


class InterviewEvaluationService:
    def build_scorecard(self, competencies: list[InterviewCompetency]) -> list[InterviewScorecardItem]:
        scorecard = []
        for competency in competencies:
            if competency.evidence_level.lower() == "high":
                suggested = 4
            elif competency.evidence_level.lower() == "medium":
                suggested = 3
            else:
                suggested = 2

            scorecard.append(
                InterviewScorecardItem(
                    competency=competency.name,
                    suggested_score=suggested,
                    evaluation_guidance=(
                        "Confirm with one concrete example and rate from 1 to 5. "
                        "A strong answer should include context, action and measurable outcome."
                    ),
                )
            )
        return scorecard

    def decision_readiness(self, readiness_score: int, scorecard: list[InterviewScorecardItem]) -> int:
        if not scorecard:
            return readiness_score
        average_score = sum(item.suggested_score for item in scorecard) / len(scorecard)
        interview_component = int((average_score / 5) * 100)
        return int((readiness_score * 0.6) + (interview_component * 0.4))
