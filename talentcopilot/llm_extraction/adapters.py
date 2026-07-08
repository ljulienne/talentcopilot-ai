from talentcopilot.document_intelligence.models import ExtractedCandidateProfile
from talentcopilot.job_intelligence.models import RoleProfile
from talentcopilot.llm_extraction.models import CandidateExtractionResult, RoleExtractionResult


class CandidateExtractionAdapter:
    def to_extracted_candidate(self, result: CandidateExtractionResult, language: str = "unknown") -> ExtractedCandidateProfile:
        facts = result.facts
        skills = list(dict.fromkeys([
            *facts.skills,
            *facts.technologies,
        ]))
        return ExtractedCandidateProfile(
            candidate_name=facts.candidate_name or "Unknown Candidate",
            skills=skills,
            raw_excerpt=result.source_summary,
            language=language,
            extraction_status=result.extraction_status,
        )

    def to_candidate_dict(self, result: CandidateExtractionResult) -> dict:
        facts = result.facts
        return {
            "name": facts.candidate_name,
            "skills": list(dict.fromkeys([*facts.skills, *facts.technologies])),
            "years_experience": facts.years_experience,
            "achievements": facts.achievements,
            "languages": facts.languages,
            "certifications": facts.certifications,
            "responsibilities": facts.responsibilities,
            "current_title": facts.current_title,
            "current_company": facts.current_company,
        }


class RoleExtractionAdapter:
    def to_role_profile(self, result: RoleExtractionResult, language: str = "unknown") -> RoleProfile:
        facts = result.facts
        return RoleProfile(
            role_title=facts.title or "Unknown Role",
            required_skills=facts.required_skills,
            preferred_skills=facts.preferred_skills,
            responsibilities=facts.responsibilities,
            languages=facts.required_languages,
            certifications=facts.certifications,
            minimum_years_experience=facts.minimum_experience,
            target_salary=facts.salary_min,
            maximum_salary=facts.salary_max,
            raw_excerpt=result.source_summary,
            language=language,
            extraction_status=result.extraction_status,
        )
