from talentcopilot.decision_core.orchestrator import DecisionCoreOrchestrator
from talentcopilot.decision_core.orchestrator_models import DecisionCoreInput
from talentcopilot.document_intelligence.candidate_extractor import CandidateDocumentExtractor
from talentcopilot.document_intelligence.models import ExtractedCandidateProfile
from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.real_matching.models import RealMatchingInput, RealMatchingOutput


class RealMatchingPipeline:
    def run(self, data: RealMatchingInput) -> RealMatchingOutput:
        candidate_analysis, extracted_candidate = DocumentIntelligencePipeline().analyze_text(
            data.candidate_filename,
            data.candidate_text,
        )

        job_analysis = JobIntelligencePipeline().analyze_text(
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

        return RealMatchingOutput(
            candidate_analysis=candidate_analysis,
            extracted_candidate=extracted_candidate,
            job_analysis=job_analysis,
            role_profile=role,
            decision_output=decision_output,
        )

    def _candidate_dict(self, candidate: ExtractedCandidateProfile) -> dict:
        return CandidateDocumentExtractor().to_candidate_dict(candidate)
