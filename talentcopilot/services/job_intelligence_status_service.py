from dataclasses import dataclass

from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline


@dataclass
class JobIntelligenceStatus:
    language: str
    section_count: int
    role_title: str
    required_skills_count: int
    minimum_years_experience: int
    extraction_status: str


class JobIntelligenceStatusService:
    def build_sample(self) -> JobIntelligenceStatus:
        sample = '''
Transformation Lead
Responsibilities
Lead HRIS transformation projects and stakeholder management.
Requirements
Minimum 6 years experience.
Required skills: Project Management, Stakeholder Management, HRIS, Leadership.
Languages
English and French.
Compensation
85000 100000
'''
        analysis = JobIntelligencePipeline().analyze_text("sample_job.txt", sample)
        profile = analysis.role_profile
        return JobIntelligenceStatus(
            language=analysis.language,
            section_count=len(analysis.sections),
            role_title=profile.role_title,
            required_skills_count=len(profile.required_skills),
            minimum_years_experience=profile.minimum_years_experience,
            extraction_status=profile.extraction_status,
        )
