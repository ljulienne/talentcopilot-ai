import json

from talentcopilot.comparative_ranking import ComparativeRankingEngine
from talentcopilot.calibrated_scoring import CalibratedMissionScoringEngine
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
        candidate_by_filename = {candidate.filename: candidate for candidate in data.candidates}

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

        comparative_engine = ComparativeRankingEngine()
        calibration_engine = CalibratedMissionScoringEngine()
        ranked = []
        for match in outputs:
            profile = match.decision_output.profile
            filename = str(getattr(match.candidate_analysis, "filename", "") or "")
            candidate_input = candidate_by_filename.get(filename)
            if candidate_input is None:
                candidate_input = next(
                    (item for item in data.candidates if profile.candidate_name.lower() in item.text.lower()),
                    CandidateTextInput(filename=filename or "candidate", text=""),
                )

            comparative = comparative_engine.analyse(
                candidate_name=profile.candidate_name,
                candidate_text=candidate_input.text,
                job_text=data.job_text,
            )
            mission_breakdown = {}
            raw_breakdown = profile.metadata.get("mission_fit_breakdown")
            if raw_breakdown:
                try:
                    mission_breakdown = json.loads(raw_breakdown) if isinstance(raw_breakdown, str) else dict(raw_breakdown)
                except (TypeError, ValueError, json.JSONDecodeError):
                    mission_breakdown = {}

            calibrated = calibration_engine.calibrate(
                mission_fit=profile.fit_score,
                mission_breakdown=mission_breakdown,
                comparative=comparative,
                differentiators=comparative.differentiators,
                validation_points=comparative.validation_points,
            )
            profile.fit_score = calibrated.score
            profile.confidence_score = calibrated.confidence
            profile.metadata.update({
                "profile_version": "calibrated-mission-scoring-v1.0",
                "fit_score": str(calibrated.score),
                "comparative_ranking_engine": comparative_engine.version,
                "comparative_score": str(comparative.score),
                "comparative_breakdown": json.dumps(comparative.to_dict(), sort_keys=True),
                "comparative_differentiators": json.dumps(comparative.differentiators),
                "comparative_validation_points": json.dumps(comparative.validation_points),
                "calibrated_scoring_engine": calibration_engine.version,
                "calibrated_score": str(calibrated.score),
                "calibrated_confidence": str(calibrated.confidence),
                "calibrated_band": calibrated.band,
                "calibrated_breakdown": json.dumps(calibrated.to_dict(), sort_keys=True),
                "calibrated_limiting_factors": json.dumps(calibrated.limiting_factors),
            })
            if comparative.differentiators:
                profile.metadata["recommendation_rationale"] = (
                    f"{profile.metadata.get('recommendation_rationale', '')} "
                    f"Comparative differentiators: {', '.join(comparative.differentiators[:3])}."
                ).strip()

            ranking_score = self._ranking_score(profile, comparative.score)
            ranked.append(
                RankedCandidate(
                    rank=0,
                    candidate_name=profile.candidate_name,
                    recommendation=profile.recommendation or "No recommendation",
                    fit_score=int(round(profile.fit_score or 0)),
                    confidence_score=int(profile.confidence_score or 0),
                    risk_level=profile.risk_level or "Unknown",
                    ranking_score=ranking_score,
                    rationale=profile.metadata.get("recommendation_rationale", ""),
                    matching_output=match,
                    comparative_score=comparative.score,
                    comparative_breakdown=comparative.to_dict(),
                    differentiators=list(comparative.differentiators),
                    validation_points=list(comparative.validation_points),
                )
            )

        ranked.sort(
            key=lambda item: (
                -float(item.fit_score or 0),
                -float(item.comparative_score or 0),
                -float(item.ranking_score or 0),
                str(item.candidate_name or "").casefold(),
            )
        )
        for index, item in enumerate(ranked, start=1):
            item.rank = index

        role_title = outputs[0].role_profile.role_title if outputs else "Unknown Role"
        return RealRankingOutput(
            role_title=role_title,
            total_candidates=len(data.candidates),
            ranked_candidates=ranked,
        )

    def _ranking_score(self, profile, comparative_score: float = 70.0) -> int:
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
            rec_score * 0.30
            + fit * 0.35
            + confidence * 0.15
            + budget * 0.05
            + float(comparative_score or 0) * 0.15
            - risk_penalty
        )
        return max(0, min(100, score))
