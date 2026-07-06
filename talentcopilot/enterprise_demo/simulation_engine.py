from typing import Any, Dict, List

from talentcopilot.core.models import (
    Candidate,
    CandidateCapability,
    Evidence,
    Job,
    JobRequirement,
)
from talentcopilot.engines.matching_engine import match_candidate_to_job
from talentcopilot.services.ranking_service import rank_candidates
from talentcopilot.engines.candidate_intelligence_engine import enrich_with_candidate_intelligence
from talentcopilot.engines.evidence_engine import enrich_with_evidence
from talentcopilot.engines.decision_builder import enrich_with_candidate_decisions


def _level_from_years(years: int) -> str:
    if years >= 10:
        return "Expert"
    if years >= 6:
        return "Advanced"
    if years >= 3:
        return "Intermediate"
    return "Beginner"


def _skill_name(repository, skill_id: str) -> str:
    skill = repository.get_skill(skill_id)
    return skill.get("name", skill_id) if skill else skill_id


def _certification_name(repository, certification_id: str) -> str:
    cert = repository.get_certification(certification_id)
    return cert.get("name", certification_id) if cert else certification_id


def _language_name(repository, language_id: str) -> str:
    language = repository.get_language(language_id)
    return language.get("name", language_id) if language else language_id


def build_core_candidate(repository, enterprise_candidate: Dict[str, Any]) -> Candidate:
    years = enterprise_candidate.get("years_experience", 0)
    level = _level_from_years(years)

    capabilities = []

    for skill_id in enterprise_candidate.get("skills", []):
        skill_name = _skill_name(repository, skill_id)

        capabilities.append(
            CandidateCapability(
                name=skill_name,
                category="Enterprise Demo",
                detected_level=level,
                confidence=88,
                evidence=[
                    Evidence(
                        text=f"{enterprise_candidate.get('name')} has demonstrated {skill_name} in enterprise HR contexts.",
                        source="Enterprise Demo Profile",
                        linked_competency=skill_name,
                        confidence=88,
                    )
                ],
            )
        )

    for language in enterprise_candidate.get("languages", []):
        language_name = _language_name(repository, language.get("language_id", ""))

        capabilities.append(
            CandidateCapability(
                name=language_name,
                category="Language",
                detected_level="Advanced",
                confidence=85,
                evidence=[
                    Evidence(
                        text=f"Language proficiency: {language_name} ({language.get('level')}).",
                        source="Enterprise Demo Profile",
                        linked_competency=language_name,
                        confidence=85,
                    )
                ],
            )
        )

    return Candidate(
        name=enterprise_candidate.get("name", "Unknown Candidate"),
        current_role=enterprise_candidate.get("current_title", ""),
        experiences=[
            f"{years} years of professional experience.",
            enterprise_candidate.get("summary", ""),
        ],
        certifications=[
            _certification_name(repository, cert_id)
            for cert_id in enterprise_candidate.get("certifications", [])
        ],
        languages=[
            _language_name(repository, lang.get("language_id", ""))
            for lang in enterprise_candidate.get("languages", [])
        ],
        capabilities=capabilities,
    )


def build_core_job(job_data: Dict[str, Any]) -> Job:
    requirements = []

    for skill in job_data.get("required_skills", []):
        requirements.append(
            JobRequirement(
                name=skill,
                category="Required",
                importance="High",
                expected_level="Advanced",
                weight=12.0,
            )
        )

    for skill in job_data.get("preferred_skills", []):
        requirements.append(
            JobRequirement(
                name=skill,
                category="Preferred",
                importance="Medium",
                expected_level="Intermediate",
                weight=6.0,
            )
        )

    for language in job_data.get("required_languages", []):
        requirements.append(
            JobRequirement(
                name=language,
                category="Language",
                importance="High",
                expected_level="Advanced",
                weight=8.0,
            )
        )

    return Job(
        title=job_data.get("title", "Untitled Job"),
        description=job_data.get("description", ""),
        requirements=requirements,
    )


class EnterpriseSimulationEngine:
    """
    Converts an enterprise recruitment scenario into a Streamlit-compatible analysis_batch.
    """

    def __init__(self, repository):
        self.repository = repository

    def run(self, recruitment: Dict[str, Any]) -> Dict[str, Any]:
        job = build_core_job(recruitment["job"])

        results: List[Dict[str, Any]] = []

        for enterprise_candidate in recruitment["candidates"]:
            candidate = build_core_candidate(self.repository, enterprise_candidate)
            match_result = match_candidate_to_job(candidate, job)

            results.append(
                {
                    "file": f"{enterprise_candidate.get('id')}_{enterprise_candidate.get('name', 'Candidate').replace(' ', '_')}.pdf",
                    "candidate": candidate,
                    "match_result": match_result,
                    "enterprise_candidate": enterprise_candidate,
                }
            )

        results = rank_candidates(results)
        results = enrich_with_candidate_intelligence(results)
        results = enrich_with_evidence(results)
        results = enrich_with_candidate_decisions(results)

        return {
            "success": True,
            "job": job,
            "results": results,
            "errors": [],
            "enterprise_context": {
                "organization": recruitment.get("organization"),
                "recruiter": recruitment.get("recruiter"),
                "scenario": recruitment.get("scenario"),
            },
        }
