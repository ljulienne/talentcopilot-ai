import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline
from talentcopilot.services.session_store import SessionStore


class DemoSessionFactory:
    """
    Builds a coherent demo RecruitmentSession from data/enterprise_demo.

    The enterprise demo candidate dataset uses IDs for skills, languages and certifications.
    This factory resolves those IDs into human-readable names before sending candidates
    to EnterprisePipeline.
    """

    def __init__(self, data_path: str = "data/enterprise_demo"):
        self.data_path = Path(data_path)

    def create_demo_session(self, job_index: int = 0, candidate_limit: int = 6):
        job, candidates = self.load_demo_inputs(job_index=job_index, candidate_limit=candidate_limit)
        session = EnterprisePipeline().run(job, candidates)
        session.metadata["source"] = "enterprise_demo"
        session.metadata["demo_candidate_limit"] = candidate_limit
        return SessionStore.set_current_session(session)

    def load_demo_inputs(self, job_index: int = 0, candidate_limit: int = 6) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        skills = self._index_by_id(self._load_json("skills.json", []))
        certs = self._index_by_id(self._load_json("certifications.json", []))
        languages = self._index_by_id(self._load_json("languages.json", []))
        jobs = self._load_json("jobs.json", [])
        candidates = self._load_json("candidates.json", [])

        if not jobs:
            job = {
                "title": "Senior HRIS Project Manager",
                "required_skills": ["HRIS", "Project Management", "Stakeholder Management"],
            }
        else:
            job = jobs[min(max(job_index, 0), len(jobs) - 1)]

        normalized = [
            self._normalize_candidate(candidate, skills, certs, languages)
            for candidate in candidates[:candidate_limit]
        ]

        return job, normalized

    def _normalize_candidate(self, candidate: Dict[str, Any], skills, certs, languages) -> Dict[str, Any]:
        normalized = dict(candidate)
        normalized["skills"] = [self._name(skills, value) for value in candidate.get("skills", [])]
        normalized["certifications"] = [self._name(certs, value) for value in candidate.get("certifications", [])]
        normalized["languages"] = [
            self._language_name(languages, value)
            for value in candidate.get("languages", [])
        ]
        achievements = []
        achievements.extend(candidate.get("strengths", []) or [])
        achievements.extend(candidate.get("risks", []) or [])
        if candidate.get("summary"):
            achievements.append(candidate["summary"])
        normalized["achievements"] = achievements
        return normalized

    def _language_name(self, languages, value):
        if isinstance(value, dict):
            name = self._name(languages, value.get("language_id"))
            level = value.get("level")
            return f"{name} ({level})" if level else name
        return self._name(languages, value)

    def _name(self, index, identifier):
        item = index.get(identifier)
        if not item:
            return str(identifier)
        return item.get("name") or item.get("label") or str(identifier)

    def _index_by_id(self, items):
        return {item.get("id"): item for item in items if isinstance(item, dict) and item.get("id")}

    def _load_json(self, filename: str, default):
        path = self.data_path / filename
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
