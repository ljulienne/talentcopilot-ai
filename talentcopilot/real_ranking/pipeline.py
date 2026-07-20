import json

from talentcopilot.comparative_ranking import ComparativeRankingEngine
from talentcopilot.calibrated_scoring import CalibratedMissionScoringEngine
from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline
from talentcopilot.real_ranking.models import CandidateTextInput, RankedCandidate, RealRankingInput, RealRankingOutput
from talentcopilot.recruiter_intelligence import RecruiterIntelligenceEngine
from talentcopilot.evidence_profiles import CandidateEvidenceProfileBuilder, MissionEvidenceProfileBuilder
from talentcopilot.career_intelligence import CareerFitEngine
from talentcopilot.decision_ranking import DecisionRankingPolicy


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
        recruiter_engine = RecruiterIntelligenceEngine()
        candidate_evidence_builder = CandidateEvidenceProfileBuilder()
        mission_evidence_builder = MissionEvidenceProfileBuilder()
        career_engine = CareerFitEngine()
        decision_policy = DecisionRankingPolicy()
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
            recruiter_assessment = recruiter_engine.assess(
                candidate_name=profile.candidate_name,
                candidate_text=candidate_input.text,
                job_text=data.job_text,
                mission_fit=calibrated.score,
                mission_breakdown=mission_breakdown,
            )
            candidate_evidence_profile = candidate_evidence_builder.build(
                candidate_text=candidate_input.text,
                extracted_candidate=match.extracted_candidate,
                candidate_name=profile.candidate_name,
            )
            mission_evidence_profile = mission_evidence_builder.build(
                job_text=data.job_text,
                role_profile=match.role_profile,
            )
            career_assessment = career_engine.assess(
                candidate_profile=candidate_evidence_profile,
                mission_profile=mission_evidence_profile,
                candidate_text=candidate_input.text,
                job_text=data.job_text,
            )
            decision_assessment = decision_policy.evaluate(
                mission_fit=calibrated.score,
                career=career_assessment,
                recruiter_fit=recruiter_assessment.strategic_fit_score,
                confidence=min(calibrated.confidence, career_assessment.confidence),
            )
            decision_score = decision_assessment.score
            decision_rationale = decision_assessment.rationale
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
                "recruiter_intelligence_engine": recruiter_engine.version,
                "recruiter_intelligence": json.dumps(recruiter_assessment.to_dict(), sort_keys=True),
                "recruiter_strategic_fit": str(recruiter_assessment.strategic_fit_score),
                "recruiter_confidence": str(recruiter_assessment.confidence_score),
                "recruiter_summary": recruiter_assessment.recruiter_summary,
                "candidate_dna": json.dumps(recruiter_assessment.candidate_dna.to_dict(), sort_keys=True),
                "recruiter_decisive_strengths": json.dumps(recruiter_assessment.decisive_strengths),
                "recruiter_material_gaps": json.dumps(recruiter_assessment.material_gaps),
                "recruiter_interview_focus": json.dumps(recruiter_assessment.interview_focus),
                "evidence_profile_contract": "evidence-profile-foundation-v1.0",
                "candidate_evidence_profile_builder": candidate_evidence_builder.version,
                "mission_evidence_profile_builder": mission_evidence_builder.version,
                "candidate_evidence_profile": json.dumps(candidate_evidence_profile.to_dict(), sort_keys=True),
                "mission_evidence_profile": json.dumps(mission_evidence_profile.to_dict(), sort_keys=True),
                "career_intelligence_engine": career_engine.version,
                "career_intelligence": json.dumps(career_assessment.to_dict(), sort_keys=True),
                "career_fit_score": str(career_assessment.score),
                "career_fit_confidence": str(career_assessment.confidence),
                "career_summary": career_assessment.summary,
                "career_strengths": json.dumps(career_assessment.strengths),
                "career_concerns": json.dumps(career_assessment.concerns),
                "career_interview_focus": json.dumps(career_assessment.interview_focus),
                "decision_ranking_contract": "decision-ranking-v1.0",
                "decision_ranking_policy": decision_policy.version,
                "decision_ranking_assessment": json.dumps(decision_assessment.to_dict(), sort_keys=True),
                "decision_score": str(decision_score),
                "decision_base_score": str(decision_assessment.base_score),
                "decision_alignment_adjustment": str(decision_assessment.alignment_adjustment),
                "decision_blockers": json.dumps(decision_assessment.blockers),
                "decision_rationale": decision_rationale,
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
                    decision_score=decision_score,
                    career_fit_score=career_assessment.score,
                    decision_rationale=decision_rationale,
                )
            )

        mission_order = sorted(
            ranked,
            key=lambda item: (
                -float(item.fit_score or 0),
                -float(item.comparative_score or 0),
                -float(item.ranking_score or 0),
                str(item.candidate_name or "").casefold(),
            ),
        )
        for index, item in enumerate(mission_order, start=1):
            item.mission_fit_rank = index
            item.matching_output.decision_output.profile.metadata["mission_fit_rank"] = str(index)

        ranked.sort(
            key=lambda item: (
                -float(item.decision_score or 0),
                -float(item.fit_score or 0),
                -float(item.career_fit_score or 0),
                str(item.candidate_name or "").casefold(),
            )
        )
        for index, item in enumerate(ranked, start=1):
            item.rank = index
            item.ranking_score = int(round(item.decision_score))
            metadata = item.matching_output.decision_output.profile.metadata
            metadata["decision_rank"] = str(index)
            metadata["official_rank"] = str(index)

        role_title = outputs[0].role_profile.role_title if outputs else "Unknown Role"
        return RealRankingOutput(
            role_title=role_title,
            total_candidates=len(data.candidates),
            ranked_candidates=ranked,
        )


    def _decision_score(self, *, mission_fit: float, career_fit: float, recruiter_fit: float, confidence: float) -> float:
        """Recommended interview priority; Mission Fit remains the dominant input."""
        score = (
            float(mission_fit or 0) * 0.64
            + float(career_fit or 0) * 0.24
            + float(recruiter_fit or 0) * 0.09
            + float(confidence or 0) * 0.03
        )
        return round(max(0.0, min(100.0, score)), 2)

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
