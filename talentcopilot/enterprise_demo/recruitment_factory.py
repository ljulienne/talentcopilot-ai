from typing import Any, Dict, List

from talentcopilot.enterprise_demo.repository import EnterpriseDemoRepository
from talentcopilot.enterprise_demo.candidate_factory import EnterpriseCandidateFactory


class EnterpriseRecruitmentFactory:
    """
    Builds enterprise recruitment scenarios from organizations, jobs and candidates.
    """

    def __init__(self, repository: EnterpriseDemoRepository | None = None):
        self.repository = repository or EnterpriseDemoRepository()
        self.candidate_factory = EnterpriseCandidateFactory(self.repository)

    def build_recruitment(
        self,
        organization_id: str = "ORG001",
        job_id: str = "JOB001",
        scenario: str = "balanced",
        candidate_count: int = 12,
    ) -> Dict[str, Any]:
        organization = self.repository.get_organization(organization_id)
        job = self.repository.get_job(job_id)

        if organization is None:
            raise ValueError(f"Unknown organization_id: {organization_id}")

        if job is None:
            raise ValueError(f"Unknown job_id: {job_id}")

        candidates = self.repository.candidates()

        if not candidates:
            candidates = self.candidate_factory.generate_candidates()

        selected_candidates = candidates[:candidate_count]

        recruiter = self.repository.get_recruiter(job.get("recruiter_id"))

        return {
            "organization": organization,
            "job": job,
            "recruiter": recruiter,
            "scenario": scenario,
            "candidates": selected_candidates,
            "candidate_count": len(selected_candidates),
        }
