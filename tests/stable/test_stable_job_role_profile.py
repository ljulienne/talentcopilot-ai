from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.job_intelligence.role_extractor import RoleProfileExtractor


def test_role_profile_to_decision_core_requirements():
    analysis = JobIntelligencePipeline().analyze_text(
        "job.txt",
        "HRIS Lead\nRequirements\nMinimum 5 years experience. HRIS Workday Project Management"
    )
    profile = analysis.role_profile
    requirements = RoleProfileExtractor().to_role_requirements(profile)

    assert requirements.role_title == profile.role_title
    assert requirements.required_skills == profile.required_skills
    assert requirements.minimum_years_experience == profile.minimum_years_experience


def test_salary_extraction():
    extractor = RoleProfileExtractor()
    assert extractor._extract_salary("85000 100000") == (85000, 100000)

    analysis = JobIntelligencePipeline().analyze_text(
        "job.txt",
        "HRIS Lead\nRequirements\nHRIS\nCompensation\n85000 100000"
    )
    profile = analysis.role_profile

    assert profile.target_salary == 85000
    assert profile.maximum_salary == 100000


def test_salary_extraction_single_value():
    extractor = RoleProfileExtractor()
    assert extractor._extract_salary("salary up to 100000") == (None, 100000)


def test_job_intelligence_ui_imports():
    module = __import__("talentcopilot.ui.job_intelligence", fromlist=["render_job_intelligence"])
    assert hasattr(module, "render_job_intelligence")
