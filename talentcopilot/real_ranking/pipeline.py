from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline
from talentcopilot.real_ranking.models import CandidateTextInput, RankedCandidate, RealRankingInput, RealRankingOutput


class RealRankingPipeline:
    RECOMMENDATION_WEIGHT = {
        "Strong Hire": 100,
        "Hire": 90,
        "Interview": 72,
        "Review Compensation Feasibility": 68,
        "More Evidence Required": 55,
        "Review": 45,
        "Reject": 0,
    }

    RISK_PENALTY = {
        "Low": 0,
        "Medium": 8,
        "High": 18,
        "Critical": 35,
    }

    def run(self, data: RealRankingInput) -> RealRankingOutput:
        outputs = []

        for candidate in data.candidates:
            match = RealMatchingPipeline().run(
                RealMatchingInput(
                    candidate_filename=candidate.filename,
                    candidate_text=candidate.text,
                    job_filename=data.job_filename,
                    job_text=data.job_text,
                    expected_salary=candidate.expected_salary,
                )
            )
            outputs.append(match)

        ranked = []
        for match in outputs:
            profile = match.decision_output.profile
            ranking_score = self._ranking_score(profile)
            ranked.append(
                RankedCandidate(
                    rank=0,
                    candidate_name=profile.candidate_name,
                    recommendation=profile.recommendation or "No recommendation",
                    fit_score=int(profile.fit_score or 0),
                    confidence_score=int(profile.confidence_score or 0),
                    risk_level=profile.risk_level or "Unknown",
                    ranking_score=ranking_score,
                    rationale=profile.metadata.get("recommendation_rationale", ""),
                    matching_output=match,
                )
            )

        ranked.sort(key=lambda item: item.ranking_score, reverse=True)
        for index, item in enumerate(ranked, start=1):
            item.rank = index

        role_title = outputs[0].role_profile.role_title if outputs else "Unknown Role"
        return RealRankingOutput(
            role_title=role_title,
            total_candidates=len(data.candidates),
            ranked_candidates=ranked,
        )

    def _ranking_score(self, profile) -> int:
        recommendation = profile.recommendation or "Review"
        rec_score = self.RECOMMENDATION_WEIGHT.get(recommendation, 40)
        fit = int(profile.fit_score or 0)
        confidence = int(profile.confidence_score or 0)
        risk_penalty = self.RISK_PENALTY.get(profile.risk_level or "Medium", 10)

        budget_fit = profile.metadata.get("budget_fit_score")
        try:
            budget = int(float(budget_fit)) if budget_fit is not None else 70
        except ValueError:
            budget = 70

        score = int(
            rec_score * 0.35
            + fit * 0.35
            + confidence * 0.20
            + budget * 0.10
            - risk_penalty
        )
        return max(0, min(100, score))
