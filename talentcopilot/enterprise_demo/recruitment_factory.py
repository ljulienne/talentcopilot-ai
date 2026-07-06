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

        # Calibrate the first candidates so the demo shows a realistic ranking:
        # strong matches, medium matches, and weaker profiles.
        required_skills = job.get("required_skills", [])
        preferred_skills = job.get("preferred_skills", [])

        for index, candidate in enumerate(selected_candidates):
            existing_skills = set(candidate.get("skills", []))

            if index == 0:
                # Strong top profile: almost all required + some preferred
                candidate["skills"] = list(existing_skills | set(required_skills) | set(preferred_skills[:2]))
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 12)

            elif index in [1, 2]:
                # Good shortlist profiles
                candidate["skills"] = list(existing_skills | set(required_skills[:4]) | set(preferred_skills[:1]))
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 9)

            elif index in [3, 4, 5]:
                # Interviewable profiles
                candidate["skills"] = list(existing_skills | set(required_skills[:3]))
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 7)

            else:
                # Weaker or partial profiles remain mostly unchanged
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 4)

        recruiter = self.repository.get_recruiter(job.get("recruiter_id"))

        return {
            "organization": organization,
            "job": job,
            "recruiter": recruiter,
            "scenario": scenario,
            "candidates": selected_candidates,
            "candidate_count": len(selected_candidates),
        }
