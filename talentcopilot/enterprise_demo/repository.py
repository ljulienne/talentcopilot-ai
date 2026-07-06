from typing import Any, Dict, List, Optional

from talentcopilot.demo.enterprise_demo_loader import load_enterprise_demo


class EnterpriseDemoRepository:
    """
    Repository for Enterprise Demo data.

    This class is the single access point for enterprise demo JSON datasets.
    """

    def __init__(self):
        self.data = load_enterprise_demo()

    def all(self, dataset_name: str) -> List[Dict[str, Any]]:
        value = self.data.get(dataset_name, [])
        return value if isinstance(value, list) else []

    def get_by_id(self, dataset_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        for item in self.all(dataset_name):
            if item.get("id") == item_id:
                return item
        return None

    def organizations(self) -> List[Dict[str, Any]]:
        return self.all("organizations")

    def recruiters(self) -> List[Dict[str, Any]]:
        return self.all("recruiters")

    def jobs(self) -> List[Dict[str, Any]]:
        return self.all("jobs")

    def candidates(self) -> List[Dict[str, Any]]:
        return self.all("candidates")

    def skills(self) -> List[Dict[str, Any]]:
        return self.all("skills")

    def certifications(self) -> List[Dict[str, Any]]:
        return self.all("certifications")

    def languages(self) -> List[Dict[str, Any]]:
        return self.all("languages")

    def personas(self) -> List[Dict[str, Any]]:
        return self.all("candidate_personas")

    def talent_dimensions(self) -> List[Dict[str, Any]]:
        return self.all("talent_dimensions")

    def get_organization(self, organization_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("organizations", organization_id)

    def get_recruiter(self, recruiter_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("recruiters", recruiter_id)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("jobs", job_id)

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("skills", skill_id)

    def get_certification(self, certification_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("certifications", certification_id)

    def get_language(self, language_id: str) -> Optional[Dict[str, Any]]:
        return self.get_by_id("languages", language_id)

    def get_jobs_by_organization(self, organization_id: str) -> List[Dict[str, Any]]:
        return [
            job for job in self.jobs()
            if job.get("organization_id") == organization_id
        ]

    def get_recruiters_by_organization(self, organization_id: str) -> List[Dict[str, Any]]:
        return [
            recruiter for recruiter in self.recruiters()
            if recruiter.get("organization_id") == organization_id
        ]
