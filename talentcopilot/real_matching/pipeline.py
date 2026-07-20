from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.document_intelligence.candidate_extractor import CandidateDocumentExtractor
from talentcopilot.document_intelligence.models import ExtractedCandidateProfile
from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.job_intelligence.role_extractor import RoleProfileExtractor
from talentcopilot.real_matching.models import RealMatchingInput, RealMatchingOutput
from talentcopilot.recruitment_reasoning import RecruitmentReasoningEngine
from talentcopilot.mission_fit_v2 import MissionFitEngineV2
import json


class RealMatchingPipeline:
    def run(self, data: RealMatchingInput) -> RealMatchingOutput:
        candidate_analysis, extracted_candidate = DocumentIntelligencePipeline(
            extraction_mode=(
                CandidateDocumentExtractor.DETERMINISTIC_MODE
            )
        ).analyze_text(
            data.candidate_filename,
            data.candidate_text,
        )

        job_analysis = JobIntelligencePipeline(
            extraction_mode=(
                RoleProfileExtractor.DETERMINISTIC_MODE
            )
        ).analyze_text(
            data.job_filename,
            data.job_text,
        )
        role = job_analysis.role_profile

        candidate_dict = self._candidate_dict(extracted_candidate)
        expected_salary = data.expected_salary

        decision_input = DecisionCoreInput(
            candidate=candidate_dict,
            role_title=role.role_title,
            required_skills=role.required_skills,
            preferred_skills=role.preferred_skills,
            minimum_years_experience=role.minimum_years_experience,
            target_salary=role.target_salary,
            maximum_salary=role.maximum_salary,
            expected_salary=expected_salary if expected_salary is not None else role.target_salary,
        )

        decision_output = DecisionCoreOrchestrator().analyze_candidate(decision_input)

        # Release 7.0: the canonical upload score is produced by the generic,
        # criterion-level Recruitment Reasoning Engine from the complete source
        # documents. Existing Decision Core evidence and governance remain intact.
        mission_fit = RecruitmentReasoningEngine().evaluate(
            job_text=data.job_text,
            candidate_text=data.candidate_text,
            candidate_name=decision_output.profile.candidate_name,
        )
        legacy_mission_fit = MissionFitEngineV2().evaluate(
            job_text=data.job_text,
            candidate_text=data.candidate_text,
            candidate_name=decision_output.profile.candidate_name,
        )
        profile = decision_output.profile
        profile.fit_score = mission_fit.score
        profile.confidence_score = mission_fit.confidence
        profile.recommendation = mission_fit.recommendation
        profile.risk_level = mission_fit.risk_level
        profile.metadata.update({
            "profile_version": "recruitment-reasoning-v1.0",
            "fit_score": str(mission_fit.score),
            "fit_summary": mission_fit.rationale,
            "confidence_score": str(mission_fit.confidence),
            "recommendation": mission_fit.recommendation,
            "recommendation_rationale": mission_fit.rationale,
            "risk_level": mission_fit.risk_level,
            # Backward-compatible contract key retained for existing consumers.
            "mission_fit_engine": "mission-fit-v2.0",
            "recruitment_reasoning_engine": mission_fit.version,
            "recruitment_reasoning_trace": json.dumps(mission_fit.to_dict(), sort_keys=True),
            "mission_fit_breakdown": json.dumps(legacy_mission_fit.breakdown, sort_keys=True),
            "recruitment_reasoning_breakdown": json.dumps({item.criterion.key: round(item.evidence_score * 100, 2) for item in mission_fit.assessments}, sort_keys=True),
            "mission_fit_strengths": json.dumps(mission_fit.strengths),
            "mission_fit_gaps": json.dumps(mission_fit.gaps),
            "mission_fit_evidence": json.dumps([evidence for item in mission_fit.assessments for evidence in item.evidence]),
            "mission_fit_dimensions": json.dumps([item.to_dict() for item in mission_fit.assessments]),
        })

        return RealMatchingOutput(
            candidate_analysis=candidate_analysis,
            extracted_candidate=extracted_candidate,
            job_analysis=job_analysis,
            role_profile=role,
            decision_output=decision_output,
        )

    def _candidate_dict(self, candidate: ExtractedCandidateProfile) -> dict:
        return CandidateDocumentExtractor().to_candidate_dict(candidate)
