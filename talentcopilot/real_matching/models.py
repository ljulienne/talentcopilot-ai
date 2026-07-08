from dataclasses import dataclass

from talentcopilot.decision_core.orchestrator_models import DecisionCoreOutput
from talentcopilot.document_intelligence.models import DocumentAnalysis, ExtractedCandidateProfile
from talentcopilot.job_intelligence.models import JobAnalysis, RoleProfile


@dataclass
class RealMatchingInput:
    candidate_filename: str
    candidate_text: str
    job_filename: str
    job_text: str
    expected_salary: float | None = None


@dataclass
class RealMatchingOutput:
    candidate_analysis: DocumentAnalysis
    extracted_candidate: ExtractedCandidateProfile
    job_analysis: JobAnalysis
    role_profile: RoleProfile
    decision_output: DecisionCoreOutput

    @property
    def recommendation(self) -> str:
        return self.decision_output.recommendation
