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

    def _skill_id_by_name(self, skill_name: str) -> str:
        for skill in self.repository.skills():
            if skill.get("name", "").lower() == skill_name.lower():
                return skill.get("id", skill_name)
        return skill_name

    def _skill_ids_from_names(self, skill_names: List[str]) -> List[str]:
        return [self._skill_id_by_name(name) for name in skill_names]

    def _calibrate_candidates_for_job(
        self,
        candidates: List[Dict[str, Any]],
        job: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        required_skill_ids = self._skill_ids_from_names(job.get("required_skills", []))
        preferred_skill_ids = self._skill_ids_from_names(job.get("preferred_skills", []))

        calibrated = []

        for index, candidate in enumerate(candidates):
            candidate = dict(candidate)
            existing_skills = set(candidate.get("skills", []))

            if index == 0:
                candidate["skills"] = list(
                    existing_skills
                    | set(required_skill_ids)
                    | set(preferred_skill_ids[:3])
                )
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 12)

            elif index in [1, 2]:
                candidate["skills"] = list(
                    existing_skills
                    | set(required_skill_ids[:4])
                    | set(preferred_skill_ids[:2])
                )
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 9)

            elif index in [3, 4, 5]:
                candidate["skills"] = list(
                    existing_skills
                    | set(required_skill_ids[:3])
                    | set(preferred_skill_ids[:1])
                )
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 7)

            else:
                candidate["skills"] = list(existing_skills)
                candidate["years_experience"] = max(candidate.get("years_experience", 0), 4)

            calibrated.append(candidate)

        return calibrated

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
        selected_candidates = self._calibrate_candidates_for_job(selected_candidates, job)

        recruiter = self.repository.get_recruiter(job.get("recruiter_id"))

        return {
            "organization": organization,
            "job": job,
            "recruiter": recruiter,
            "scenario": scenario,
            "candidates": selected_candidates,
            "candidate_count": len(selected_candidates),
        }
